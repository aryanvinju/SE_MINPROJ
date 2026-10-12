# TriadLens: ML, DL and QML Disagreement Audit

**Problem statement:** Small, imbalanced survey datasets can conceal disagreement between models when a product reports only one prediction. TriadLens compares classical ML, deep learning and simulated quantum-kernel ML on a common lung-survey split, exposes agreement and out-of-range inputs, and shows held-out results against a majority-class baseline. It is an educational audit portal, not a diagnostic tool.

The project uses **lungcancer.csv** with ML, DL, QML, a Flask web interface, Git, GitHub, GitHub Actions, Docker, a Docker Hub publishing workflow, Kubernetes manifests, an SRS, a System Test Plan and a separate architecture/design specification. The public GitHub repository contains source code and a high-level performance table. The local submission bundle holds row-level data, detailed metrics, derived model artifacts and student-ID PDFs. See [data/README.md](data/README.md) for setup.

## Start here on this computer

Open a terminal in this folder and run:

```powershell
python app.py
```

Open **http://127.0.0.1:5000**, click **Load dataset example**, then **Run comparison**. Trained models are included in the local submission bundle. A clean public-repository checkout needs the dataset added and `python train.py` run first. You can also double-click `run_lab.cmd`. If port 5000 is already in use by the running preview, open the existing URL or set `$env:PORT='5001'` before starting.

With all three models selected, the result includes an agreement audit: per-model labels, a descriptive majority dataset label and a review flag when labels disagree or age lies outside the training range. A single-model request has no comparison audit. Agreement is not a clinical vote.

## Setup on another computer

Use Python 3.13 and an internet connection for the first installation. In PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe train.py
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe app.py
```

The dependency versions match the environment used to train the included models. A clean installation on another machine has not been verified. If you intentionally change package versions, retrain all models before running the app; serialized scikit-learn models are version-sensitive. Only load the supplied or your own trusted model files.

## What to demonstrate to your teacher

1. Show `data/lungcancer.csv` and explain the input columns and target.
2. Run `python train.py` and explain the shared train/validation/test split.
3. Show the three model implementations in `train.py`, `core.py` and `quantum.py`.
4. Open the app, load a dataset example, and run all three models. Then select each model individually.
5. Demonstrate a missing input and explain the API validation tests.
6. Show the held-out evaluation table and explain why the majority-class baseline matters.
7. Run `python -m pytest -q` and show the passing tests.
8. Follow the Kubernetes steps below on a working local cluster, then capture the real pod and service output.
9. Submit the SRS, System Test Plan, evaluation evidence, and project code. Add your name, USN, class and teacher details to the documents.

## Models and data preparation

| Approach | Implementation | Input | Output rule |
|---|---|---|---|
| ML | Scikit-learn logistic regression, balanced class weights | All 15 standardized features | YES score at least 0.5 |
| DL | PyTorch network 15 → 32 → 16 → 1 with ReLU hidden layers | All 15 standardized features | Sigmoid score at least 0.5 |
| QML | Four-qubit quantum fidelity kernel plus classical SVM | Four PCA components mapped to angles | SVM predicted class; margin shown separately |

The provided CSV has **309 rows**. Preprocessing strips column whitespace, removes **33 exact duplicate rows**, and excludes **two rows with identical inputs but contradictory labels**. It does not choose one conflicting label over another. The original CSV is kept unchanged. This leaves **274 records**, split with seed 42 into **175 training, 44 validation and 55 test** records using stratification. Reported performance applies to this cleaned subset.

Gender is encoded F=0, M=1. Binary feature codes 1 and 2 become 0 and 1 internally. Their real-world meanings were not supplied, so the UI deliberately labels them **Code 1** and **Code 2**. Do not assume a codebook without confirming it with the teacher. The target is NO=0 and YES=1. All fitted scaling and PCA transformations use training records only. Validation loss selects the DL checkpoint; test records are never used to choose model settings. ML and QML hyperparameters are fixed.

The DL model uses Adam, weighted binary cross-entropy with logits, weight decay, at most 500 epochs, and early stopping after 40 epochs without a sufficient validation improvement. The supplied run selected epoch 37 and stopped at epoch 77.

QML is a **genuine quantum-kernel algorithm simulated with NumPy**, not a classical classifier simply renamed QML. Two rounds of RY and RZ rotations and a CNOT chain prepare a 16-amplitude statevector. The kernel is the squared absolute inner product between two encoded states. A classical SVM trains on that kernel matrix. The four PCA components retain approximately 51.3% of training variance. No Qiskit or PennyLane dependency is required. If your teacher explicitly requires one of those frameworks or actual hardware, that is an additional requirement; this implementation uses an exact CPU simulator.

## Measured results

| Model | Accuracy | Balanced accuracy | Precision | Recall | F1 | ROC AUC |
|---|---:|---:|---:|---:|---:|---:|
| ML | 92.73% | 95.83% | 100.00% | 91.67% | 95.65% | 97.02% |
| DL | 92.73% | 95.83% | 100.00% | 91.67% | 95.65% | 98.81% |
| QML | 89.09% | 81.55% | 95.65% | 91.67% | 93.62% | 87.80% |

The test set has **7 NO and 48 YES** records. Always predicting YES achieves **87.27% accuracy**, so accuracy alone is insufficient. Confusion matrices use rows=true class and columns=predicted class in the order NO, YES:

- ML and DL: `[[7, 0], [4, 44]]`.
- QML: `[[5, 2], [4, 44]]`.

This is one small, imbalanced dataset split, not a clinical study. Predicted labels and model scores must not be interpreted as a diagnosis or a calibrated medical risk. QML receives fewer dimensions, so this is a comparison of these implementations, not proof that one entire learning paradigm is superior.

## API

| Method and path | Purpose |
|---|---|
| GET `/` | Web interface |
| POST `/api/predict` | Run ML, DL, QML or ALL |
| GET `/api/metrics` | Saved evaluation and split details |
| GET `/api/example` | Example from the training partition |
| GET `/health/live` | Process liveness |
| GET `/health/ready` | Models loaded and ready |

Use the complete request in `reports/example_request.json`:

```powershell
Invoke-RestMethod -Uri http://127.0.0.1:5000/api/predict -Method Post -ContentType 'application/json' -InFile reports/example_request.json
```

The API requires exactly `model` and `features`. It rejects missing/unknown fields, invalid codes, non-integer/out-of-range ages, malformed JSON, and oversized requests. QML returns a decision margin, **not a probability**. Survey submissions are not saved by the application.

## Docker

The Dockerfile uses Gunicorn rather than Flask's development server. The image deliberately excludes the survey CSV, trained model files and detailed reports. First ensure Docker Desktop is running with Linux containers. From this folder, run `python train.py` if model artifacts are not present, then mount those local files when starting the container:

```powershell
docker build -t lung-cancer-lab:1.0 .
$modelDir = (Resolve-Path .\models).Path
$reportDir = (Resolve-Path .\reports).Path
docker run --rm -p 5001:5000 --mount "type=bind,source=$modelDir,target=/app/models,readonly" --mount "type=bind,source=$reportDir,target=/app/reports,readonly" lung-cancer-lab:1.0
```

Open http://127.0.0.1:5001. The container loads the mounted model files. The build requires internet access for dependencies. GitHub Actions has built the source-only image; the mounted-model container run has not been verified in this environment.

## Docker Hub publication

The GitHub Actions `publish` job targets [aryanvinju/se_miniproj](https://hub.docker.com/repository/docker/aryanvinju/se_miniproj/general) and pushes a **source-only** image after tests pass on a push to `main`. It can also be rerun manually on `main` through **Actions → TriadLens CI → Run workflow**. It uses GitHub repository Actions secrets `DOCKERHUB_USERNAME` (value `aryanvinju`) and `DOCKERHUB_TOKEN` (a Docker Hub access token). The workflow tags the image with the Git commit SHA and `latest`. Never place the token in a tracked file or a workflow input.

The Docker Hub repository and GitHub Actions secrets have been supplied. Verify publication in the Actions run and Docker Hub tag list after merging this PR. The published image still needs local model and report artifacts mounted at runtime; it does not contain row-level survey data or encoded training states.

## Kubernetes with Minikube

The namespace `lung-lab` isolates this demonstration. The manifest defines two replicas, a ClusterIP Service, startup/readiness/liveness probes, resource limits, a non-root container and read-only Secret mounts for model/report artifacts. Use this only in a local lab cluster; the reports include dataset row identifiers.

```powershell
minikube start --driver=docker
kubectl create namespace lung-lab --dry-run=client -o yaml | kubectl apply -f -
kubectl create secret generic triadlens-models --from-file=models/scaler.joblib --from-file=models/ml.joblib --from-file=models/qml.joblib --from-file=models/dl.pt -n lung-lab --dry-run=client -o yaml | kubectl apply -f -
kubectl create secret generic triadlens-reports --from-file=reports/metrics.json --from-file=reports/example_request.json -n lung-lab --dry-run=client -o yaml | kubectl apply -f -
docker build -t lung-cancer-lab:1.0 .
minikube image load lung-cancer-lab:1.0
kubectl apply -f k8s/lung-lab.yaml
kubectl rollout status deployment/lung-lab -n lung-lab --timeout=180s
kubectl get pods,svc -n lung-lab
kubectl port-forward service/lung-lab 8080:80 -n lung-lab
```

Keep the port-forward terminal open and visit http://127.0.0.1:8080. In a second terminal:

```powershell
Invoke-RestMethod http://127.0.0.1:8080/health/ready
Invoke-RestMethod -Uri http://127.0.0.1:8080/api/predict -Method Post -ContentType 'application/json' -InFile reports/example_request.json
kubectl scale deployment/lung-lab --replicas=3 -n lung-lab
kubectl rollout status deployment/lung-lab -n lung-lab
kubectl get pods -n lung-lab
kubectl scale deployment/lung-lab --replicas=2 -n lung-lab
```

For a self-healing demonstration, delete **one pod belonging to this lab** using its exact name from `kubectl get pods -n lung-lab`; show that the Deployment creates a replacement. Restart port-forward if its selected pod was deleted. Do not delete unrelated pods. To remove this lab's resources when finished, use `kubectl delete -f k8s/lung-lab.yaml`.

To use the Docker Hub image after it has been published, create the same namespace and Secrets on the selected local cluster, apply the manifest, then run `kubectl set image deployment/lung-lab web=aryanvinju/se_miniproj:<commit-sha> -n lung-lab` before checking rollout. Replace the bracketed SHA with the one shown in the successful Actions run. If using Docker Desktop's Kubernetes, enable it and select its context; skip Minikube commands. Avoid using a public cluster with the supplied detailed reports.

Troubleshooting: `ImagePullBackOff` usually means the image is absent from the cluster; `CrashLoopBackOff` requires reading `kubectl logs deployment/lung-lab -n lung-lab`; an unset context means a cluster has not been selected. Do not claim deployment success until rollout and HTTP requests succeed.

## Verification status

- **57 automated tests passed locally**, including four data-free public CI checks, model disagreement rules, API predictions on all 55 held-out records, malformed-input handling, missing-model readiness, split integrity, known quantum gate behavior, and kernel properties.
- A live HTTP request to the local app and a three-model prediction succeeded.
- JavaScript passed Node's syntax check. Browser interaction, responsive layout and accessibility tests are listed as pending manual checks.
- GitHub Actions has passed the public checks and built the source-only Docker image. Check the latest main-branch Actions run for Docker Hub publication. A mounted-model Docker run and live Kubernetes deployment remain unverified: Docker access was denied and no current Kubernetes context was configured.
- Optional WebMCP registration is feature-detected. No compatible browser validation context was available; it is not part of the verified lab acceptance criteria.

## Files to submit

- `docs/SRS.md`: requirements specification, use case diagram, security requirements and acceptance criteria.
- `docs/System_Test_Plan.md`: test cases, traceability, actual evidence and pending deployment checks.
- `docs/Architecture_Design.md`: component and sequence diagrams, API and security design.
- `docs/Originality_and_Demo.md`: source attribution, genuine contribution workflow and demo steps.
- `reports/metrics.json`, `test_predictions.csv`, `splits.json`, `dl_training_history.csv`: model evidence.
- `reports/test_results.xml`, `http_smoke_test.json`: executed test evidence.
- Python code, frontend, saved models, original dataset, Dockerfile, Kubernetes YAML and this README.

The documents are editable Markdown and can be opened in a text editor or copied into your institution's report format. The local CSV's provenance and license were not supplied. A public [Survey Lung Cancer copy](https://huggingface.co/datasets/nateraw/lung-cancer) has the same 309-row schema and first records; byte identity with the local copy has not been independently verified. Only the local lungcancer.csv is included.

## Git and GitHub Actions

The `.github/workflows/ci.yml` workflow runs the public, data-free Python checks and a JavaScript syntax check on pushes and pull requests, builds the Docker image, and checks that private artifacts are absent. Its `publish` job logs in to Docker Hub using repository secrets and pushes an image after a successful main-branch push or manual main-branch run. The full 57-case local suite requires the private row-level dataset and derived evidence. Git tracks source changes locally; GitHub hosts the branch, pull request and Actions runs. Review a teammate's diff and record the review on GitHub before merge.

| Tool | Project use | Current evidence |
|---|---|---|
| Git | Versioned source and local commits | `git log` in this workspace |
| GitHub | Source branch and review PR | [TriadLens PR #1](https://github.com/aryanvinju/SE_MINPROJ/pull/1) |
| GitHub Actions | Python/JavaScript checks, image build and main-branch publish | [Successful PR CI run](https://github.com/aryanvinju/SE_MINPROJ/actions/runs/38200322711); inspect latest main run for publication |
| Docker | Reproducible source-only Gunicorn image | Dockerfile and CI image build; mounted-model run pending |
| Docker Hub | Image registry for `aryanvinju/se_miniproj` | Verify SHA and latest tags after the main-branch run |
| Kubernetes | Two replicas, Service, health probes and artifact Secret mounts | Manifest validated; live rollout pending |

## Primary references

- [Scikit-learn evaluation guidance](https://scikit-learn.org/stable/modules/cross_validation.html)
- [Scikit-learn SVC and precomputed kernels](https://scikit-learn.org/stable/modules/generated/sklearn.svm.SVC.html)
- [PyTorch binary cross-entropy with logits](https://docs.pytorch.org/docs/stable/generated/torch.nn.BCEWithLogitsLoss.html)
- [Qiskit quantum kernel tutorial](https://qiskit-community.github.io/qiskit-machine-learning/tutorials/03_quantum_kernel.html) — conceptual reference; this project implements its own simulator.
- [Kubernetes Deployments](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/)
- [Kubernetes Services](https://kubernetes.io/docs/concepts/services-networking/service/)


## Educational risk levels

Each model returns Low, Moderate or High **demo risk**, derived from its existing score. These bands do not change the model or its YES/NO prediction. ML/DL use Low below 0.30, Moderate from 0.30 to below 0.70 and High at or above 0.70. QML uses its uncalibrated SVM margin: Low below -0.50, Moderate from -0.50 to below 0.50 and High at or above 0.50. These are arbitrary demonstration thresholds, not medical cutoffs or calibrated cancer probabilities. Low does not rule out disease; categories from different models are not directly comparable. API results include risk.level, risk.basis, risk.thresholds and risk.clinical_risk=false. ST22 and ST23 cover boundary assignments and API consistency.
