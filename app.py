"""Flask API and frontend. Train with train.py before starting this service."""
import json
import logging
import os
import time
import joblib
import numpy as np
import pandas as pd
import torch
from flask import Flask, jsonify, render_template, request
from werkzeug.exceptions import HTTPException
from core import ROOT, FEATURES, DeepClassifier, encode, validate_features, demo_risk_level
from quantum import states_for, fidelity_kernel


class Predictor:
    def __init__(self, model_dir):
        self.scaler = joblib.load(model_dir / 'scaler.joblib')
        self.ml = joblib.load(model_dir / 'ml.joblib')
        self.qml = joblib.load(model_dir / 'qml.joblib')
        self.dl = DeepClassifier()
        self.dl.load_state_dict(torch.load(model_dir / 'dl.pt', map_location='cpu', weights_only=True))
        self.dl.eval()

    def predict(self, features, selection):
        x = self.scaler.transform(encode(pd.DataFrame([features], columns=FEATURES)))
        results = []
        for name in (['ML', 'DL', 'QML'] if selection == 'ALL' else [selection]):
            started = time.perf_counter()
            if name == 'ML':
                score = float(self.ml.predict_proba(x)[0, 1])
                predicted, score_type = int(score >= 0.5), 'class YES model score'
            elif name == 'DL':
                with torch.no_grad():
                    score = float(torch.sigmoid(self.dl(torch.tensor(x, dtype=torch.float32)))[0])
                predicted, score_type = int(score >= 0.5), 'class YES model score'
            else:
                angles = self.qml['angle_scaler'].transform(self.qml['pca'].transform(x))
                kernel = fidelity_kernel(states_for(angles), self.qml['train_states'])
                score = float(self.qml['svm'].decision_function(kernel)[0])
                predicted = int(self.qml['svm'].predict(kernel)[0])
                score_type = 'SVM decision margin (not a probability)'
            results.append({'model': name, 'label': 'YES' if predicted else 'NO',
                            'score': score, 'score_type': score_type,
                            'risk': demo_risk_level(name, score),
                            'inference_ms': round((time.perf_counter() - started) * 1000, 3)})
        return results


def comparison_audit(results, extrapolated=False):
    """Describe model agreement without implying a clinical consensus."""
    if len(results) != 3:
        return None
    labels = {result['model']: result['label'] for result in results}
    yes_count = sum(label == 'YES' for label in labels.values())
    majority = 'YES' if yes_count >= 2 else 'NO'
    agreement = max(yes_count, 3 - yes_count)
    reasons = []
    if agreement < 3:
        reasons.append('Model labels disagree')
    if extrapolated:
        reasons.append('Age outside training range')
    return {'labels': labels, 'agreement_count': agreement,
            'unanimous': agreement == 3, 'majority_dataset_label': majority,
            'review_flag': bool(reasons), 'review_reasons': reasons,
            'note': 'Agreement is descriptive, not a diagnosis or clinical voting rule.'}


def create_app(model_dir=None):
    app = Flask(__name__)
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024
    torch.set_num_threads(1)
    predictor = None
    try:
        predictor = Predictor(model_dir or ROOT / 'models')
    except (FileNotFoundError, RuntimeError, ValueError, EOFError, KeyError, OSError):
        app.logger.exception('Models could not be loaded. Run python train.py.')
    metrics_path = ROOT / 'reports/metrics.json'
    metrics = json.loads(metrics_path.read_text(encoding='utf-8')) if metrics_path.exists() else None

    @app.get('/')
    def index():
        return render_template('index.html', binary_features=FEATURES[2:])

    @app.get('/health/live')
    def live():
        return jsonify(status='alive')

    @app.get('/health/ready')
    def ready():
        return jsonify(status='ready' if predictor else 'models unavailable'), 200 if predictor else 503

    @app.get('/api/metrics')
    def get_metrics():
        if metrics is None:
            return jsonify(error='Evaluation is unavailable. Run python train.py.'), 503
        return jsonify(metrics)

    @app.get('/api/example')
    def example():
        path = ROOT / 'reports/example_request.json'
        if not path.exists():
            return jsonify(error='Example unavailable. Run python train.py.'), 503
        return jsonify(json.loads(path.read_text(encoding='utf-8')))

    @app.post('/api/predict')
    def predict():
        if predictor is None:
            return jsonify(error='Models unavailable. Run python train.py and restart.'), 503
        if not request.is_json:
            return jsonify(error='Send a JSON request with Content-Type application/json.'), 415
        body = request.get_json()
        if not isinstance(body, dict) or set(body) != {'model', 'features'}:
            return jsonify(error='Request must contain exactly model and features.'), 400
        selection = body['model']
        if not isinstance(selection, str) or selection not in ('ML', 'DL', 'QML', 'ALL'):
            return jsonify(error='model must be ML, DL, QML or ALL.'), 400
        try:
            features = validate_features(body['features'])
        except ValueError as error:
            return jsonify(error=str(error)), 400
        results = predictor.predict(features, selection)
        warnings = []
        extrapolated = False
        if metrics:
            low, high = metrics['training_age_range']
            if not low <= features['AGE'] <= high:
                extrapolated = True
                warnings.append(f'Age is outside the training range ({low}–{high}); this is extrapolation.')
        return jsonify(results=results, comparison=comparison_audit(results, extrapolated), warnings=warnings,
                       note='Educational dataset classification only. Outputs are not a diagnosis or calibrated medical risk.')

    @app.errorhandler(HTTPException)
    def http_error(error):
        if request.path.startswith('/api/'):
            return jsonify(error=error.description), error.code
        return error

    @app.errorhandler(Exception)
    def unexpected_error(error):
        app.logger.exception('Unhandled server error')
        return jsonify(error='The server could not complete the request.'), 500

    @app.after_request
    def headers(response):
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['Cache-Control'] = 'no-store'
        response.headers['Content-Security-Policy'] = "default-src 'self'; style-src 'self'; script-src 'self'; frame-ancestors 'none'; base-uri 'self'; form-action 'self'"
        return response

    return app


app = create_app()

if __name__ == '__main__':
    # Flask development server is for a local lab demo. The container uses Gunicorn.
    app.run(host=os.getenv('HOST', '127.0.0.1'), port=int(os.getenv('PORT', '5000')), debug=False)
