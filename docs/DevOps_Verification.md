# DevOps verification — 12 October 2026

## GitHub Actions and Docker Hub

- [Main run 38201577529](https://github.com/aryanvinju/SE_MINPROJ/actions/runs/38201577529) completed successfully after PR #1 was merged. Test, container and publish jobs passed.
- The publish log shows pushes of `aryanvinju/se_miniproj:0cf74d38d7729b70ff8a66c9588400286f6d0aea` and `aryanvinju/se_miniproj:latest`.
- The pushed and locally pulled image digest was `sha256:ecbd5049e833911c3db2b09d0395d207a32797b2ef87b8235e233af3373d0e87`.
- After the plain black-on-white UI was merged, [main run 38203322240](https://github.com/aryanvinju/SE_MINPROJ/actions/runs/38203322240) passed and pushed `aryanvinju/se_miniproj:b465cb7535d3a544f649d29cea827ed1fae26933` and `:latest`, digest `sha256:5d299e742b84031632955994dfa2894e3282e3394b8c13f33d73945321199b95`.

## Docker runtime

- `docker pull` of the SHA tag completed with the same digest.
- Inspection of the unmounted image returned `data_csv False`, `models ['README.md']` and `reports ['README.md', 'dl_training_history.csv']`. The private survey rows and saved model files were absent.
- A container run on `127.0.0.1:5001` with local `models` and `reports` mounted read only returned `{"status":"ready"}` from `/health/ready`.
- POST `/api/predict` using `reports/example_request.json` returned ML, DL and QML labels, all `YES`, with `agreement_count: 3`.

## Docker Desktop Kubernetes

- Context: `docker-desktop`; node `desktop-control-plane` was Ready. All resources were created in namespace `lung-lab`.
- Two Kubernetes Secrets supplied the local model and report artifacts to the source-only image. The manifest's two Pods became `1/1 Running`; the Service's `/health/ready` returned ready and POST `/api/predict` returned the three model results.
- Scaling to three replicas produced three ready Pods; scaling back produced two ready Pods.
- Pod `lung-lab-855cc58c-hhtw2` was deleted. Deployment created `lung-lab-855cc58c-btg9m`, which became ready. The port forward attached to the deleted Pod closed; after reconnecting, the Service prediction worked.
- The deployment was then updated to the simplified UI image tag `b465cb7535d3a544f649d29cea827ed1fae26933`. Rollout completed with two ready Pods. The Service returned the new `TriadLens — model comparison` page and an ML/DL/QML prediction.

These are observed local and remote checks, not a claim of public cluster deployment or clinical validation. Browser case ST16 also passed in the local portal: example loading, ALL and individual model views, and required-input feedback. ST17 passed keyboard focus and a 375 px viewport with no horizontal overflow; 200 percent zoom was not independently verified.
