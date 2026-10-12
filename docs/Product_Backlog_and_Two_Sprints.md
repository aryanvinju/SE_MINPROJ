# TriadLens product backlog and two-sprint plan

Plan recorded 12 October 2026. Repository: [aryanvinju/SE_MINPROJ](https://github.com/aryanvinju/SE_MINPROJ). The [SRS](SRS.md), [architecture](Architecture_Design.md), and [system test plan](System_Test_Plan.md) define acceptance. The dates below follow the instructor's assignment. Story points express relative effort, not hours.

Project team: Aryan Vinju, Aditya Shetty, Avantika Jitesh and Apeksha Ashok. Student identifiers are included in the private submission PDFs. GitHub issue ownership remains provisional until each teammate's GitHub username is supplied; this roster does not claim who authored existing code.

The implementation already exists as a working dry run. Existing code, tests, pull requests, CI, Docker Hub and local Kubernetes results are **pre-sprint evidence**. Sprint 1 and Sprint 2 have not happened as of 12 October; their reviews, teammate PRs and videos must be recorded during the stated weeks. Issue ownership is provisionally `@aryanvinju` until teammate GitHub usernames are supplied. Reassign each issue to its actual contributor before that sprint starts.

The [Jira board](https://pesuonline-team-g6ej69na.atlassian.net/jira/software/projects/SCRUM/boards/1/backlog) also has two future sprints on these dates. Sprint 1 (ID 103) contains SCRUM-5, SCRUM-6, SCRUM-9, SCRUM-10 and SCRUM-14, totaling 15 points. Sprint 2 (ID 104) contains SCRUM-7, SCRUM-8, SCRUM-11, SCRUM-12 and SCRUM-13, totaling 19 points. The earlier duplicate Docker Hub story SCRUM-15 sits in the product backlog; its scope is included in SCRUM-12. GitHub issues below are the detailed FR/NFR traceability record.

On GitHub, [Sprint 1 milestone](https://github.com/aryanvinju/SE_MINPROJ/milestone/1) contains issues #3–#7 and [Sprint 2 milestone](https://github.com/aryanvinju/SE_MINPROJ/milestone/2) contains issues #8–#12. Both milestones are open with the assignment due dates. They organize the issues while the requested GitHub Project board is awaiting Projects access.

## Product backlog

| Issue | Product backlog item and acceptance outcome | SRS trace | Points | Sprint | Owner |
|---|---|---|---:|---|---|
| [#3](https://github.com/aryanvinju/SE_MINPROJ/issues/3) | Clean the survey and save reproducible, disjoint split evidence | FR09, FR10, FR14; NFR05 | 3 | 1 | @aryanvinju, provisional |
| [#4](https://github.com/aryanvinju/SE_MINPROJ/issues/4) | Train ML baseline and report held-out metrics beside majority baseline | FR05, FR08, FR14; NFR01 | 3 | 1 | @aryanvinju, provisional |
| [#5](https://github.com/aryanvinju/SE_MINPROJ/issues/5) | Expose validated prediction API, clear errors and health checks | FR03, FR04, FR11, FR12; NFR02, NFR03, NFR06 | 3 | 1 | @aryanvinju, provisional |
| [#6](https://github.com/aryanvinju/SE_MINPROJ/issues/6) | Serve simple accessible form, example input and ML result | FR01, FR02, FR06; NFR04 | 3 | 1 | @aryanvinju, provisional |
| [#7](https://github.com/aryanvinju/SE_MINPROJ/issues/7) | Run PR/commit checks and record one-minute working-product video | NFR08, NFR09 | 3 | 1 | @aryanvinju, provisional |
| [#8](https://github.com/aryanvinju/SE_MINPROJ/issues/8) | Train and evaluate DL on the same split | FR05, FR06, FR08, FR14; NFR01, NFR05 | 5 | 2 | @aryanvinju, provisional |
| [#9](https://github.com/aryanvinju/SE_MINPROJ/issues/9) | Train and evaluate simulated quantum-kernel ML and label its margin correctly | FR05, FR06, FR07, FR14; NFR01 | 5 | 2 | @aryanvinju, provisional |
| [#10](https://github.com/aryanvinju/SE_MINPROJ/issues/10) | Show agreement, disagreement and out-of-training-age review reasons | FR15; NFR02, NFR05 | 3 | 2 | @aryanvinju, provisional |
| [#11](https://github.com/aryanvinju/SE_MINPROJ/issues/11) | Publish source-only Docker image and verify two Kubernetes replicas | FR12, FR13, FR16; NFR06, NFR07, NFR09, NFR10 | 3 | 2 | @aryanvinju, provisional |
| [#12](https://github.com/aryanvinju/SE_MINPROJ/issues/12) | Run full system tests, complete docs, record two-minute video and freeze | FR01–FR16; NFR01–NFR10 | 3 | 2 | @aryanvinju, provisional |

Total: **34 points**, with **15 in Sprint 1** and **19 in Sprint 2**. DL and QML have five points each because training, saved artifacts and held-out interpretation are more involved than a single UI or API slice. All SRS FR and NFR IDs appear in the backlog.

## Sprint 1 backlog — 19–23 October 2026, 15 points

Goal: a working, tested ML vertical slice from survey record to browser prediction, with reproducible data and CI. Complete [#3](https://github.com/aryanvinju/SE_MINPROJ/issues/3), [#4](https://github.com/aryanvinju/SE_MINPROJ/issues/4), [#5](https://github.com/aryanvinju/SE_MINPROJ/issues/5), [#6](https://github.com/aryanvinju/SE_MINPROJ/issues/6), and [#7](https://github.com/aryanvinju/SE_MINPROJ/issues/7). A teammate assigned to each implementation issue opens its PR; the repository owner reviews and merges only after checks pass. Record the PR, reviewer, commit and CI run on the issue. Upload `docs/demo/sprint1.mp4` or a link to an accessible video during the sprint. Close issues only when the linked acceptance criteria and video have been checked.

**One-minute recording plan:** 0–10 s state the problem and show the 15-field form; 10–25 s load a sample and get an ML result; 25–40 s show the cleaning and 175/44/55 split; 40–50 s show the held-out ML metrics and majority baseline; 50–60 s show the passing PR workflow and issue/PR link. Record the actual screen and voice of the student demonstrator.

## Sprint 2 backlog — 26–30 October 2026, 19 points

Goal: compare ML, DL and simulated QML, explain disagreement, and verify the packaged deployment. Complete [#8](https://github.com/aryanvinju/SE_MINPROJ/issues/8), [#9](https://github.com/aryanvinju/SE_MINPROJ/issues/9), [#10](https://github.com/aryanvinju/SE_MINPROJ/issues/10), [#11](https://github.com/aryanvinju/SE_MINPROJ/issues/11), and [#12](https://github.com/aryanvinju/SE_MINPROJ/issues/12). Follow the same assigned-contributor PR and owner-review process. Upload `docs/demo/sprint2.mp4` or an accessible video link. After the sprint review, record the frozen commit SHA and avoid additional feature changes in the submitted version.

**Two-minute recording plan:** 0–15 s recap the problem and dataset; 15–40 s use Load example and Run comparison; 40–60 s explain three labels, score types and the QML decision margin; 60–80 s show disagreement and out-of-range warning; 80–95 s show held-out metrics versus the majority baseline; 95–110 s show GitHub Actions, Docker Hub tag and two ready Kubernetes Pods; 110–120 s show tests, documentation and the frozen commit. Include actual command output or browser state, not a slide claiming a deployment.

## Dry run and evidence available on 12 October

The 12–16 October week is a practice dry run. Current checks demonstrate a functioning product before Sprint 1:

- [PR #1](https://github.com/aryanvinju/SE_MINPROJ/pull/1) and [PR #2](https://github.com/aryanvinju/SE_MINPROJ/pull/2) were merged before the scheduled sprints. They establish that GitHub PRs and Actions work; they do not satisfy the future teammate-authored PR requirement.
- The [main Actions run](https://github.com/aryanvinju/SE_MINPROJ/actions/runs/38203946359) passed test, container and publish jobs. The public image is [aryanvinju/se_miniproj](https://hub.docker.com/repository/docker/aryanvinju/se_miniproj/general).
- The [DevOps verification log](DevOps_Verification.md) records a pulled image, mounted-model prediction, two ready Docker Desktop Kubernetes Pods, Service prediction, scaling and replacement.
- The local full suite previously passed 57 tests; the [test plan](System_Test_Plan.md) and `reports/` contain evidence. Browser form, example and model comparison were exercised. The 200 percent zoom check is still open.

## Live demonstration now

From this workspace run `python app.py` after loading the local model artifacts, then open `http://127.0.0.1:5000/` (or the actual port shown in the terminal). Click **Load example**, select **ALL**, and click **Run comparison**. The page shows ML, DL and QML labels and the agreement audit. `GET /api/metrics` shows the held-out metrics. For a terminal proof, run `python -m pytest -q`, `Invoke-RestMethod http://127.0.0.1:5000/health/ready`, and `Invoke-RestMethod -Uri http://127.0.0.1:5000/api/predict -Method Post -ContentType 'application/json' -InFile reports/example_request.json` with the actual port substituted.

## Sprint review and deviations log

| Date | Planned requirement | Actual result or deviation | Evidence / decision |
|---|---|---|---|
| 12 Oct | Dry-run implementation and deployment | Core features and local Docker Desktop Kubernetes checks exist ahead of the scheduled sprints | PRs, Actions and DevOps log above |
| 12 Oct | GitHub Project board linked to repository | GitHub issues and two sprint milestones created; Project board creation remains blocked because the available GitHub credential lacks Projects scope and the browser session is signed out | [Repository Projects](https://github.com/aryanvinju/SE_MINPROJ/projects) |
| 12 Oct | Team assignments | `@aryanvinju` is provisional; teammates' handles have not yet been supplied | Reassign before each sprint |
| 23 Oct | Sprint 1 review, teammate PR, one-minute video | Pending scheduled sprint | Add PR/reviewer/CI/video links to #7 |
| 30 Oct | Sprint 2 review, two-minute video and freeze | Pending scheduled sprint | Add PR/reviewer/CI/video/frozen SHA to #12 |

At each review, replace pending rows with actual findings, document any deviation from the SRS, architecture or test plan, and explain it in the final demo. Do not backdate a PR, video, review or sprint completion.
