"""Executable system and mathematical correctness tests; no invented results."""
import json
import numpy as np
import pandas as pd
import pytest
import torch
from app import create_app, comparison_audit
from core import ROOT, FEATURES, load_dataset, encode
from quantum import single_qubit_gate, cnot, states_for, fidelity_kernel


@pytest.fixture(scope='module')
def client():
    return create_app().test_client()


@pytest.fixture
def payload():
    return json.loads((ROOT / 'reports/example_request.json').read_text())


def test_ST01_frontend_and_assets(client):
    page = client.get('/')
    assert page.status_code == 200
    assert b'One dataset.' in page.data
    for path in ['/static/app.js', '/static/style.css']:
        assert client.get(path).status_code == 200


def test_ST02_health(client):
    assert client.get('/health/live').status_code == 200
    assert client.get('/health/ready').json['status'] == 'ready'


@pytest.mark.parametrize('model', ['ML', 'DL', 'QML', 'ALL'])
def test_ST03_model_selection(client, payload, model):
    payload['model'] = model
    response = client.post('/api/predict', json=payload)
    assert response.status_code == 200
    results = response.json['results']
    assert [r['model'] for r in results] == (['ML', 'DL', 'QML'] if model == 'ALL' else [model])
    assert all(r['label'] in ['YES', 'NO'] and np.isfinite(r['score']) for r in results)


def test_ST04_api_matches_all_held_out_predictions(client):
    rows = pd.read_csv(ROOT / 'reports/test_predictions.csv')
    for _, row in rows.iterrows():
        features = {k: (row[k] if k == 'GENDER' else int(row[k])) for k in FEATURES}
        response = client.post('/api/predict', json={'model': 'ALL', 'features': features})
        assert response.status_code == 200
        for result in response.json['results']:
            model = result['model']
            assert result['label'] == row[f'{model}_prediction']
            assert result['score'] == pytest.approx(row[f'{model}_score'], abs=1e-6)


@pytest.mark.parametrize('field,value', [('AGE', -1), ('AGE', 121), ('AGE', 30.5),
    ('AGE', True), ('AGE', '60'), ('AGE', None), ('AGE', float('nan')),
    ('AGE', float('inf')), ('GENDER', 'X'), ('SMOKING', 0), ('SMOKING', 3),
    ('SMOKING', True), ('SMOKING', '2')])
def test_ST05_invalid_values(client, payload, field, value):
    payload['features'][field] = value
    response = client.post('/api/predict', json=payload)
    assert response.status_code == 400 and 'error' in response.json


@pytest.mark.parametrize('case', ['missing', 'extra', 'not_object', 'bad_model', 'model_array', 'extra_root'])
def test_ST06_invalid_schema(client, payload, case):
    if case == 'missing': del payload['features']['AGE']
    if case == 'extra': payload['features']['UNKNOWN'] = 2
    if case == 'not_object': payload['features'] = []
    if case == 'bad_model': payload['model'] = 'ABC'
    if case == 'model_array': payload['model'] = []
    if case == 'extra_root': payload['unexpected'] = 1
    assert client.post('/api/predict', json=payload).status_code == 400


def test_ST07_transport_errors(client):
    assert client.post('/api/predict', data='hello').status_code == 415
    assert client.post('/api/predict', data='{broken', content_type='application/json').status_code == 400
    assert client.post('/api/predict', data=' ' * 20000, content_type='application/json').status_code == 413
    assert client.get('/api/predict').status_code == 405


def test_ST08_models_unavailable(tmp_path, payload):
    client = create_app(tmp_path).test_client()
    assert client.get('/health/live').status_code == 200
    assert client.get('/health/ready').status_code == 503
    assert client.post('/api/predict', json=payload).status_code == 503


def test_ST09_extrapolation_warning(client, payload):
    payload['features']['AGE'] = 0
    response = client.post('/api/predict', json=payload)
    assert response.status_code == 200 and response.json['warnings']


def test_ST10_split_integrity_and_scaler():
    import joblib
    frame, audit = load_dataset(ROOT / 'data/lungcancer.csv')
    metrics = json.loads((ROOT / 'reports/metrics.json').read_text())
    splits = metrics['splits']
    sets = [set(splits[k]['row_ids']) for k in ['train', 'validation', 'test']]
    assert not (sets[0] & sets[1] or sets[0] & sets[2] or sets[1] & sets[2])
    assert set.union(*sets) == set(range(len(frame)))
    assert audit == {'original_rows': 309, 'duplicates_removed': 33, 'conflicting_rows_excluded': 2}
    assert not frame.duplicated(subset=FEATURES).any()
    scaler = joblib.load(ROOT / 'models/scaler.joblib')
    assert np.allclose(scaler.mean_, encode(frame)[splits['train']['row_ids']].mean(axis=0))


def test_ST11_quantum_gates_known_bell_state():
    state = np.zeros(16, dtype=complex); state[0] = 1
    hadamard = np.array([[1, 1], [1, -1]]) / np.sqrt(2)
    state = cnot(single_qubit_gate(state, hadamard, 0), 0, 1)
    expected = np.zeros(16, dtype=complex); expected[[0, 12]] = 1 / np.sqrt(2)
    assert np.allclose(state, expected)
    assert np.allclose(cnot(cnot(state, 1, 3), 1, 3), state)


def test_ST12_quantum_kernel_properties():
    states = states_for(np.random.default_rng(42).uniform(-np.pi, np.pi, (12, 4)))
    assert np.allclose(np.linalg.norm(states, axis=1), 1)
    kernel = fidelity_kernel(states, states)
    assert np.allclose(kernel, kernel.T)
    assert np.allclose(np.diag(kernel), 1)
    assert np.linalg.eigvalsh(kernel).min() >= -1e-9
    zero = states_for(np.zeros((1, 4)))[0]
    assert np.allclose(zero, np.eye(16)[0])


def test_ST13_metrics_recompute(client):
    from train import evaluate
    metrics = client.get('/api/metrics').json
    rows = pd.read_csv(ROOT / 'reports/test_predictions.csv')
    y = (rows['LUNG_CANCER'] == 'YES').astype(int)
    for model in ['ML', 'DL', 'QML']:
        actual = evaluate(y, (rows[f'{model}_prediction'] == 'YES').astype(int), rows[f'{model}_score'])
        for key, value in actual.items():
            if key == 'confusion_matrix': assert value == metrics['models'][model][key]
            else: assert value == pytest.approx(metrics['models'][model][key])


def test_ST14_cache_and_content_security(client):
    response = client.get('/')
    assert response.headers['Cache-Control'] == 'no-store'
    assert "default-src 'self'" in response.headers['Content-Security-Policy']


def test_ST15_repeated_prediction(client, payload):
    first = client.post('/api/predict', json=payload).json['results']
    second = client.post('/api/predict', json=payload).json['results']
    assert [(r['label'], r['score']) for r in first] == [(r['label'], r['score']) for r in second]


@pytest.mark.parametrize('model,score,expected', [
    ('ML', 0, 'Low'), ('ML', 0.2999, 'Low'), ('ML', 0.3, 'Moderate'),
    ('ML', 0.6999, 'Moderate'), ('ML', 0.7, 'High'), ('ML', 1, 'High'),
    ('DL', 0.2, 'Low'), ('DL', 0.5, 'Moderate'), ('DL', 0.8, 'High'),
    ('QML', -2, 'Low'), ('QML', -0.5001, 'Low'), ('QML', -0.5, 'Moderate'),
    ('QML', 0.4999, 'Moderate'), ('QML', 0.5, 'High'), ('QML', 3, 'High')])
def test_ST22_risk_boundaries(model, score, expected):
    from core import demo_risk_level
    risk = demo_risk_level(model, score)
    assert risk['level'] == expected
    assert risk['clinical_risk'] is False


def test_ST23_risk_api(client, payload):
    from core import demo_risk_level
    response = client.post('/api/predict', json=payload)
    assert response.status_code == 200
    for result in response.json['results']:
        assert result['risk'] == demo_risk_level(result['model'], result['score'])


def test_ST24_disagreement_audit_rules():
    labels = [{'model': 'ML', 'label': 'YES'}, {'model': 'DL', 'label': 'NO'},
              {'model': 'QML', 'label': 'YES'}]
    audit = comparison_audit(labels)
    assert audit['unanimous'] is False
    assert audit['agreement_count'] == 2
    assert audit['majority_dataset_label'] == 'YES'
    assert audit['review_reasons'] == ['Model labels disagree']
    unanimous = comparison_audit([dict(item, label='NO') for item in labels], extrapolated=True)
    assert unanimous['unanimous'] is True
    assert unanimous['review_reasons'] == ['Age outside training range']
    assert comparison_audit(labels[:1]) is None


def test_ST25_disagreement_api(client, payload):
    response = client.post('/api/predict', json=payload)
    audit = response.json['comparison']
    assert audit['labels'] == {r['model']: r['label'] for r in response.json['results']}
    assert audit['agreement_count'] in (2, 3)
    assert audit['note'].startswith('Agreement is descriptive')
    payload['model'] = 'ML'
    assert client.post('/api/predict', json=payload).json['comparison'] is None
