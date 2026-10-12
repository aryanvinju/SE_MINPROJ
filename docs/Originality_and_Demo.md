# TriadLens: genuine contribution and demo guide

Project team: Aryan Vinju, Aditya Shetty, Avantika Jitesh and Apeksha Ashok. Student identifiers are included in the private submission PDFs. Assign actual contributions and PR authorship only after the team confirms its work.

## How to make the submission defensible

Plagiarism checks are passed by doing and explaining original work, not by disguising copied code. Keep the raw dataset and its source note separate from authored code. Cite scikit-learn, PyTorch, Flask, Kubernetes and any tutorial ideas that influenced the implementation. Retain meaningful commits and pull request reviews showing who designed, coded, tested and revised each part. Do not claim a teammate wrote a module they did not write.

Each team member should be able to explain and, if asked, modify their contribution live. Good small extensions include an extra data-quality check, a justified test for a boundary case, or a new audit visualization. Run the full tests after each change and record the exact command and result. In the report, state clearly that the four-qubit feature circuit is simulated on a CPU and that no clinical validation or quantum speedup was demonstrated.

## Suggested division of work

1. Data and ML: audit the CSV, explain duplicate/conflicting rows, train logistic regression and the majority baseline.
2. DL: implement/check the PyTorch model, validation checkpoint choice and training curves.
3. QML: explain RY/RZ/CNOT gates, fidelity kernel, PCA compression and SVM; verify kernel mathematical tests.
4. Full stack and DevOps: API validation, disagreement audit, UI, Git/GitHub review, GitHub Actions, Docker, Docker Hub publication, Kubernetes configuration and documentation.

Use the actual team names and GitHub handles in pull requests and issue assignments. This is a suggested split until the team confirms membership.

## One-minute Sprint 1 video outline

Show the 309-row CSV, cleaning report and train/validation/test counts; run training; show ML, DL and QML metric table and baseline; show passing tests. Explain that the test partition was not used to choose model settings.

## Two-minute Sprint 2 video outline

Open the Flask UI; load an example; run ALL; explain model scores versus QML margin, agreement panel and age-range warning; submit an invalid value; show the GitHub PR and CI result. If a Docker Hub push and Kubernetes rollout have succeeded, show their real tags and Pod status. State any checks still pending and show the Jira sprint board.

## Release evidence checklist

- Exact Git commit and reviewed pull request links.
- GitHub Actions run URL with test and image-build status.
- Docker Hub repository and immutable image tag after an actual publish run.
- Model metric JSON, split IDs and held-out predictions.
- Test run output and manual browser notes.
- Docker image build/run output and Kubernetes rollout/pod/service output when actually executed.
- Sprint video files or links, with the features demonstrably working.

Never mark a future sprint, a remote CI run, or a deployment as complete before its evidence exists.
