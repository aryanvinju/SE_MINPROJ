# Dataset setup

The row-level lung-survey CSV is intentionally excluded from the public repository. The local submission bundle includes `data/lungcancer.csv` with SHA-256 `77e4f763ab845eae865907c3014088beab8fa2e1185676bff91387858c729b1b`.

A public [Survey Lung Cancer dataset copy](https://huggingface.co/datasets/nateraw/lung-cancer) contains 309 rows and the same field schema. Its license page lists CC BY-NC-SA 4.0. We have not established byte identity with the local classroom copy or a verified binary-feature codebook. If using a separately downloaded copy, save it as `data/lungcancer.csv`, inspect its schema and license, then run `python train.py` to generate model artifacts. Do not present that retraining as reproducing the included metrics unless the input file hash and preprocessing audit match.
