# TriadLens: ML, DL and QML Disagreement Audit
# System Test Plan and Execution Record (IEEE-style)

Version 2.1 | 12 October 2026

Student: project team
Tester: project team
Instructor review: pending

## 1. Objective and scope

Verify the full-stack prediction flow, all three models, disagreement audit, educational risk bands, input validation, data separation, quantum simulator correctness, GitHub Actions, Docker Hub publication and Kubernetes deployment. This plan covers software behavior, not clinical validation or quantum advantage.

## 2. Test items and environment

Windows with Python 3.13 and the versions recorded in reports/metrics.json. Use the supplied lungcancer.csv, trained artifacts and held-out prediction evidence. The cleaned dataset has 274 records: 175 train, 44 validation and 55 test. Seed 42 is used for stratified splitting. Docker and a selected Kubernetes context are additional prerequisites for deployment tests.

## 3. Features to be tested

Dataset cleaning, training-only preprocessing, ML/DL/QML inference, disagreement flags, API validation, frontend assets, health endpoints, privacy headers and deployment configuration. The relevant SRS IDs are FR01–FR15, NFR01–NFR09 and SR-01–SR-04.

## 4. Features not to be tested

Clinical diagnosis, institutional identity systems, patient records, quantum hardware advantage and production availability are outside the project scope.

## 5. Approach, cases and actual results

Case identifiers map directly to tests/test_system.py. Parameterized variations account for the total number of tests.

| ID | Procedure and expected outcome | Requirement | Status |
|---|---|---|---|
| ST01 | Request page, CSS and JavaScript; all return 200. | FR01 | PASS |
| ST02 | With model artifacts loaded, liveness and readiness succeed. | FR12 | PASS |
| ST03 | Select ML, DL, QML and ALL; return only the selected models, finite scores and labels. | FR05 to FR07 | PASS |
| ST04 | Submit all 55 held-out records; all 165 model labels match saved predictions and scores match within 1e-6. | FR05, FR10, NFR01 | PASS |
| ST05 | Reject 13 invalid age, gender and binary-code variations with 400. | FR04 | PASS |
| ST06 | Reject six missing/extra field, malformed-schema and invalid-model variations with 400. | FR03 | PASS |
| ST07 | Wrong content type, malformed JSON, oversized payload and wrong method yield 415, 400, 413 and 405. | FR11, NFR02 | PASS |
| ST08 | Missing model files leave liveness at 200 but readiness and prediction at 503. | FR11, FR12, NFR06 | PASS |
| ST09 | An accepted age outside training coverage produces an extrapolation warning. | FR04 | PASS |
| ST10 | Verify cleaning audit, disjoint/exhaustive splits and training-only scaler fitting. | FR09, FR10, FR14 | PASS |
| ST11 | Verify known Bell-state preparation and cancellation of two identical CNOT gates. | QML design | PASS |
| ST12 | Verify state normalization, symmetric positive-semidefinite fidelity kernel, unit diagonal and zero-angle circuit state. | QML design | PASS |
| ST13 | Recompute metrics and confusion matrices from saved test predictions; match API report. | FR08, FR14 | PASS |
| ST14 | Check no-store caching and same-origin content security policy. | NFR03 | PASS |
| ST15 | Repeated requests produce identical labels and scores. | NFR05 | PASS |
| ST22 | Test 15 score-band cases, including exact boundaries for ML/DL and QML. | Educational risk levels | PASS |
| ST23 | API risk metadata matches its model and score; clinical_risk remains false. | Educational risk levels | PASS |
| ST24 | Synthetic label combinations produce the correct agreement count, majority label and review reasons. | FR15 | PASS |
| ST25 | ALL returns an audit matching model outputs; a single-model request returns null audit. | FR15 | PASS |

Final local automated result: **57 passed, zero failures, zero errors** on 12 October 2026. Four are data-free public CI checks. JUnit evidence is in the private submission bundle at reports/test_results.xml. JavaScript syntax is checked separately. Timings vary by machine.

### 5.1 Security validation

ST05–ST07 reject malformed fields, unexpected JSON keys, wrong content type and oversized bodies. ST14 checks no-store responses and the same-origin Content Security Policy. The Dockerfile and Kubernetes manifest are inspected for a non-root user, dropped capabilities and resource limits; live container and cluster validation remain ST18–ST19. These cases trace to SO-01–SO-03 and SR-01–SR-04 in the SRS.

## Risk band expectations

ML and DL: Low below 0.30; Moderate from 0.30 to below 0.70; High at or above 0.70. QML margin: Low below -0.50; Moderate from -0.50 to below 0.50; High at or above 0.50. These are illustrative thresholds chosen for the lab, not medically established thresholds. The original classification and raw score must remain unchanged. A Low level must not be described as ruling out disease. Levels across models are not directly comparable.

## 6. Manual and operational cases

| ID | Procedure | Expected outcome | Status |
|---|---|---|---|
| ST16 | In the browser, load an example, run ALL and each model, then submit a missing field. | Correct result cards and risk badges appear; required-input error is visible. | PENDING manual interaction check |
| ST17 | Use keyboard navigation, 375 px viewport and 200 percent zoom. | Focus and controls remain visible and usable. | PENDING manual check |
| ST18 | Build the source-only image, mount local model/report files and run it on host port 5001. | Container becomes ready and all three models respond; image itself contains no private artifacts. | BLOCKED by Docker access in execution environment |
| ST19 | Create local cluster Secrets, load or pull the image, apply YAML, wait for rollout and port-forward Service to 8080. | Two ready Pods and successful three-model HTTP response through Service. | BLOCKED by missing configured cluster |
| ST20 | Scale to three replicas, verify readiness, then restore two. | Desired replica counts are achieved. | PENDING ST19 |
| ST21 | Delete one exact Pod in namespace lung-lab and observe replacement. | Replacement becomes ready; API works after reconnecting port-forward if needed. | PENDING ST19 |
| ST26 | Configure Docker Hub repository secrets and manually dispatch the workflow from main. | GitHub Actions publishes SHA and latest tags to aryanvinju/se_miniproj; pulled image excludes survey rows and model artifacts. | PENDING Docker Hub token and main-branch workflow |

Kubernetes YAML parsing and label-selector consistency were checked. They do not establish that a cluster deployment works. Optional WebMCP integration has not been checked in a compatible browser and is outside lab acceptance.

## 7. Execution steps

From the project folder, run `python train.py`, then `python -m pytest -q --junitxml=reports/test_results.xml`. If the default temporary directory is inaccessible, add `--basetemp` with a new writable task-specific folder. Start `python app.py`; use the README HTTP example. For operational cases follow the README Minikube commands only against the lab cluster and namespace.

## 8. Evidence, traceability and acceptance

Preserve test_results.xml, metrics.json, splits.json, test_predictions.csv and http_smoke_test.json. Capture actual browser results and real kubectl output when manual/operational checks are executed. Do not fabricate screenshots or mark blocked tests passed.

Local automated acceptance requires every automated test and a real HTTP smoke request to succeed. Full lab acceptance also requires ST16 through ST21, ST26, a remote GitHub Actions run, and instructor review. Current local software checks pass; Docker Hub publication, Docker/Kubernetes and browser interaction acceptance remain incomplete.

Traceability: FR01–FR02 → ST01/ST16; FR03–FR04 → ST05–ST07/ST09; FR05–FR07 → ST03–ST04/ST16; FR08 → ST13; FR09–FR10 → ST10; FR11–FR12 → ST02/ST07–ST08; FR13 → ST18–ST21; FR14 → ST04/ST10/ST13; FR15 → ST24–ST25; FR16 → ST26. NFR01–NFR08 map to ST04–ST21 as listed above; NFR09 requires a successful remote CI run; NFR10 maps to ST18–ST19 and ST26.

For a failure, record case ID, environment, input, expected/actual result, reproduction steps, severity and evidence. Fix the implementation and rerun relevant checks. Never change expected labels to hide a failure or tune models on the held-out test partition.
