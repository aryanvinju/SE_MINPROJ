# Model artifacts

The local submission bundle includes trained `.joblib` and `.pt` files. They are excluded from the public repository because the quantum-kernel artifact contains encoded per-record training states. Obtain the dataset as described in `data/README.md`, then run `python train.py` to regenerate all artifacts locally. Load only artifacts you generated or otherwise trust.
