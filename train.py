"""Train all three models and write reproducible evaluation evidence."""
import argparse
import copy
import hashlib
import importlib.metadata
import json
import time
from datetime import datetime, timezone
import joblib
import numpy as np
import pandas as pd
import torch
from sklearn.decomposition import PCA
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (accuracy_score, balanced_accuracy_score, confusion_matrix,
                             precision_score, recall_score, f1_score, roc_auc_score)
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.svm import SVC
from core import ROOT, FEATURES, SEED, DeepClassifier, encode, load_dataset
from quantum import states_for, fidelity_kernel


def evaluate(y, predicted, score):
    return {'accuracy': float(accuracy_score(y, predicted)),
            'balanced_accuracy': float(balanced_accuracy_score(y, predicted)),
            'precision': float(precision_score(y, predicted, zero_division=0)),
            'recall': float(recall_score(y, predicted, zero_division=0)),
            'f1': float(f1_score(y, predicted, zero_division=0)),
            'roc_auc': float(roc_auc_score(y, score)),
            'confusion_matrix': confusion_matrix(y, predicted, labels=[0, 1]).tolist()}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--data', type=str, default=str(ROOT / 'data/lungcancer.csv'))
    args = parser.parse_args()
    torch.set_num_threads(1)
    torch.manual_seed(SEED)
    torch.use_deterministic_algorithms(True)
    np.random.seed(SEED)
    frame, audit = load_dataset(args.data)
    X, y = encode(frame), frame['LUNG_CANCER'].map({'NO': 0, 'YES': 1}).to_numpy()
    ids = np.arange(len(frame))
    development, test = train_test_split(ids, test_size=0.2, stratify=y, random_state=SEED)
    train, validation = train_test_split(development, test_size=0.2, stratify=y[development], random_state=SEED)
    scaler = StandardScaler().fit(X[train])
    xt, xv, xe = [scaler.transform(X[index]) for index in (train, validation, test)]
    models = ROOT / 'models'
    reports = ROOT / 'reports'
    models.mkdir(exist_ok=True)
    reports.mkdir(exist_ok=True)
    joblib.dump(scaler, models / 'scaler.joblib')
    results, outputs = {}, {}

    started = time.perf_counter()
    ml = LogisticRegression(class_weight='balanced', max_iter=2000, random_state=SEED)
    ml.fit(xt, y[train])
    ml_score = ml.predict_proba(xe)[:, 1]
    ml_pred = (ml_score >= 0.5).astype(int)
    results['ML'] = evaluate(y[test], ml_pred, ml_score)
    results['ML']['training_seconds'] = time.perf_counter() - started
    outputs['ML'] = (ml_pred, ml_score)
    joblib.dump(ml, models / 'ml.joblib')

    started = time.perf_counter()
    dl = DeepClassifier()
    optimizer = torch.optim.Adam(dl.parameters(), lr=0.003, weight_decay=0.001)
    positive_weight = float((y[train] == 0).sum() / (y[train] == 1).sum())
    loss_fn = torch.nn.BCEWithLogitsLoss(pos_weight=torch.tensor(positive_weight))
    tensors = [torch.tensor(a, dtype=torch.float32) for a in (xt, xv, xe, y[train], y[validation])]
    tx, vx, ex, ty, vy = tensors
    best_loss, best_epoch, stale, history = float('inf'), 0, 0, []
    best_state = copy.deepcopy(dl.state_dict())
    for epoch in range(1, 501):
        dl.train()
        optimizer.zero_grad()
        loss = loss_fn(dl(tx), ty)
        loss.backward()
        optimizer.step()
        dl.eval()
        with torch.no_grad():
            val_loss = float(loss_fn(dl(vx), vy))
        history.append({'epoch': epoch, 'train_loss': float(loss.detach()), 'validation_loss': val_loss})
        if val_loss < best_loss - 0.0001:
            best_loss, best_epoch, stale = val_loss, epoch, 0
            best_state = copy.deepcopy(dl.state_dict())
        else:
            stale += 1
        if stale >= 40:
            break
    dl.load_state_dict(best_state)
    dl.eval()
    with torch.no_grad():
        dl_score = torch.sigmoid(dl(ex)).numpy()
    dl_pred = (dl_score >= 0.5).astype(int)
    results['DL'] = evaluate(y[test], dl_pred, dl_score)
    results['DL'].update(training_seconds=time.perf_counter() - started, best_epoch=best_epoch,
                         epochs_run=epoch, validation_loss=best_loss)
    outputs['DL'] = (dl_pred, dl_score)
    torch.save(dl.state_dict(), models / 'dl.pt')
    pd.DataFrame(history).to_csv(reports / 'dl_training_history.csv', index=False)

    started = time.perf_counter()
    pca = PCA(n_components=4, svd_solver='full').fit(xt)
    angle_scaler = MinMaxScaler(feature_range=(-np.pi, np.pi), clip=True).fit(pca.transform(xt))
    train_states = states_for(angle_scaler.transform(pca.transform(xt)))
    test_states = states_for(angle_scaler.transform(pca.transform(xe)))
    qml = SVC(kernel='precomputed', C=1.0, class_weight='balanced', random_state=SEED)
    qml.fit(fidelity_kernel(train_states, train_states), y[train])
    test_kernel = fidelity_kernel(test_states, train_states)
    qml_pred, qml_score = qml.predict(test_kernel), qml.decision_function(test_kernel)
    results['QML'] = evaluate(y[test], qml_pred, qml_score)
    results['QML'].update(training_seconds=time.perf_counter() - started,
                          qubits=4, pca_explained_variance=float(pca.explained_variance_ratio_.sum()))
    outputs['QML'] = (qml_pred, qml_score)
    joblib.dump({'pca': pca, 'angle_scaler': angle_scaler, 'train_states': train_states, 'svm': qml}, models / 'qml.joblib')

    partitions = {'train': train, 'validation': validation, 'test': test}
    split_info = {name: {'count': len(index), 'NO': int((y[index] == 0).sum()),
                         'YES': int((y[index] == 1).sum()), 'row_ids': index.tolist()}
                  for name, index in partitions.items()}
    report = {'created_utc': datetime.now(timezone.utc).isoformat(), 'seed': SEED,
              'dataset': 'lungcancer.csv', 'dataset_sha256': hashlib.sha256(open(args.data, 'rb').read()).hexdigest(),
              **audit,
              'unique_rows': len(frame), 'features': FEATURES, 'splits': split_info,
              'training_age_range': [int(frame.iloc[train]['AGE'].min()), int(frame.iloc[train]['AGE'].max())],
              'majority_baseline_accuracy': float(accuracy_score(y[test], np.full(len(test), np.bincount(y[train]).argmax()))),
              'models': results,
              'versions': {p: importlib.metadata.version(p) for p in ['numpy', 'pandas', 'scikit-learn', 'torch', 'Flask', 'scipy', 'joblib']},
              'limitations': ['Small imbalanced dataset; one held-out split is not clinical validation.',
                             'QML uses four PCA components; ML and DL use all 15 features.',
                             'QML runs an exact noiseless NumPy statevector simulation, not quantum hardware.',
                             'Dataset source, license and binary feature meanings were not supplied.',
                             'Scores are model outputs, not calibrated estimates of individual medical risk.']}
    (reports / 'metrics.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    (reports / 'splits.json').write_text(json.dumps(split_info, indent=2), encoding='utf-8')
    evidence = frame.iloc[test].copy()
    evidence.insert(0, 'deduplicated_row_id', test)
    for name, (pred, score) in outputs.items():
        evidence[f'{name}_prediction'] = np.where(pred == 1, 'YES', 'NO')
        evidence[f'{name}_score'] = score
    evidence.to_csv(reports / 'test_predictions.csv', index=False)
    example = {k: (int(v) if k != 'GENDER' else v) for k, v in frame.iloc[train[0]][FEATURES].to_dict().items()}
    (reports / 'example_request.json').write_text(json.dumps({'model': 'ALL', 'features': example}, indent=2), encoding='utf-8')
    print(json.dumps({'rows': len(frame), 'splits': {k: v['count'] for k, v in split_info.items()}, 'results': results}, indent=2))


if __name__ == '__main__':
    main()
