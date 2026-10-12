"""Data-free checks suitable for CI on the public repository."""
import numpy as np

from app import comparison_audit, create_app
from core import FEATURES, validate_features
from quantum import states_for, fidelity_kernel


def test_public_input_validation():
    values = {name: 1 for name in FEATURES}
    values.update(GENDER='F', AGE=40)
    assert validate_features(values)['AGE'] == 40
    values['SMOKING'] = 3
    try:
        validate_features(values)
    except ValueError:
        pass
    else:
        raise AssertionError('Invalid feature code was accepted')


def test_public_quantum_kernel_properties():
    states = states_for(np.zeros((2, 4)))
    kernel = fidelity_kernel(states, states)
    assert states.shape == (2, 16)
    assert np.allclose(kernel, np.ones((2, 2)))


def test_public_disagreement_audit():
    rows = [{'model': 'ML', 'label': 'YES'}, {'model': 'DL', 'label': 'NO'},
            {'model': 'QML', 'label': 'YES'}]
    audit = comparison_audit(rows, extrapolated=True)
    assert audit['agreement_count'] == 2
    assert audit['majority_dataset_label'] == 'YES'
    assert audit['review_reasons'] == ['Model labels disagree', 'Age outside training range']


def test_public_health_without_artifacts(tmp_path):
    client = create_app(tmp_path).test_client()
    live = client.get('/health/live')
    ready = client.get('/health/ready')
    assert live.status_code == 200 and ready.status_code == 503
    assert live.headers['Cache-Control'] == 'no-store'
