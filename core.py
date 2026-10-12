"""Shared validation, preprocessing, and model definitions for the lab."""
from pathlib import Path
import numpy as np
import pandas as pd
import torch
from torch import nn

ROOT = Path(__file__).resolve().parent
FEATURES = ['GENDER', 'AGE', 'SMOKING', 'YELLOW_FINGERS', 'ANXIETY',
            'PEER_PRESSURE', 'CHRONIC DISEASE', 'FATIGUE', 'ALLERGY',
            'WHEEZING', 'ALCOHOL CONSUMING', 'COUGHING',
            'SHORTNESS OF BREATH', 'SWALLOWING DIFFICULTY', 'CHEST PAIN']
BINARY = FEATURES[2:]
SEED = 42


def validate_features(values):
    if not isinstance(values, dict):
        raise ValueError('features must be a JSON object.')
    missing, extra = set(FEATURES) - values.keys(), values.keys() - set(FEATURES)
    if missing or extra:
        raise ValueError(f'Incorrect fields. Missing: {sorted(missing)}; unexpected: {sorted(extra)}')
    if values['GENDER'] not in ('M', 'F'):
        raise ValueError('GENDER must be M or F.')
    age = values['AGE']
    if isinstance(age, bool) or not isinstance(age, (int, float)) or not np.isfinite(age) or age != int(age) or not 0 <= age <= 120:
        raise ValueError('AGE must be a whole number from 0 to 120.')
    for name in BINARY:
        if isinstance(values[name], bool) or not isinstance(values[name], (int, float)) or values[name] not in (1, 2):
            raise ValueError(f'{name} must be numeric code 1 or 2.')
    return {name: values[name] for name in FEATURES}


def encode(frame):
    """Fixed coding only; all learned transformations are fitted on training data."""
    result = frame[FEATURES].copy()
    result['GENDER'] = result['GENDER'].map({'F': 0, 'M': 1})
    result[BINARY] = result[BINARY] - 1
    return result.to_numpy(dtype=np.float64)


def load_dataset(path):
    frame = pd.read_csv(path)
    frame.columns = frame.columns.str.strip()
    if set(frame.columns) != set(FEATURES + ['LUNG_CANCER']):
        raise ValueError('Dataset columns do not match the lung cancer schema.')
    if frame.isna().any().any():
        raise ValueError('Missing values found; resolve them before training.')
    for row in frame[FEATURES].to_dict('records'):
        validate_features(row)
    if not frame['LUNG_CANCER'].isin(['YES', 'NO']).all():
        raise ValueError('LUNG_CANCER must contain YES or NO.')
    original_count = len(frame)
    frame = frame.drop_duplicates().reset_index(drop=True)
    duplicates = original_count - len(frame)
    conflicts = frame.duplicated(subset=FEATURES, keep=False)
    audit = {'original_rows': original_count, 'duplicates_removed': duplicates,
             'conflicting_rows_excluded': int(conflicts.sum())}
    # Exclude both labels for contradictory inputs; do not guess the correct label.
    frame = frame.loc[~conflicts].reset_index(drop=True)
    return frame, audit


class DeepClassifier(nn.Module):
    """15 input features, two hidden layers, one output logit."""
    def __init__(self):
        super().__init__()
        self.network = nn.Sequential(nn.Linear(15, 32), nn.ReLU(),
                                     nn.Linear(32, 16), nn.ReLU(), nn.Linear(16, 1))

    def forward(self, x):
        return self.network(x).squeeze(-1)


def demo_risk_level(model, score):
    """Illustrative score bands only; not clinically established risk thresholds."""
    if model not in ('ML', 'DL', 'QML') or not np.isfinite(score):
        raise ValueError('A supported model and finite score are required.')
    low, high = (-0.5, 0.5) if model == 'QML' else (0.3, 0.7)
    level = 'Low' if score < low else ('Moderate' if score < high else 'High')
    return {'level': level, 'basis': 'Illustrative model score band',
            'thresholds': {'low_below': low, 'high_at_or_above': high},
            'clinical_risk': False}
