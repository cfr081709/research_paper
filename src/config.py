from pathlib import Path
import os, random
import numpy as np
import tensorflow as tf

SEED = 42

# Paths (portable)
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
RESULTS_DIR = BASE_DIR / "results"

METRICS_DIR = RESULTS_DIR / "metrics"
PREDICTIONS_DIR = RESULTS_DIR / "predictions"
METADATA_DIR = RESULTS_DIR / "metadata"

for d in [METRICS_DIR, PREDICTIONS_DIR, METADATA_DIR]:
    d.mkdir(parents=True, exist_ok=True)

def set_seed(seed: int = 42):
    # Reproducibility
    os.environ["PYTHONHASHSEED"] = str(seed)   # FIX: was str(SEED), ignoring the parameter
    os.environ["TF_DETERMINISTIC_OPS"] = "1"
    os.environ["TF_CUDNN_DETERMINISTIC"] = "1"
    os.environ["CUDA_VISIBLE_DEVICES"] = "-1"

    random.seed(seed)    # FIX: was SEED (module-level constant), ignoring parameter
    np.random.seed(seed) # FIX: same
    tf.random.set_seed(seed)  # FIX: same

    tf.config.threading.set_inter_op_parallelism_threads(1)
    tf.config.threading.set_intra_op_parallelism_threads(1)