# Pattern Weight Training

This directory contains reference/non-submission code for training pattern evaluation weights.

## What the script does

`train_pattern_weights.sh` runs these steps from `reference_non_submission/`:

1. Rebuilds `evaluate.out` from `calc_additional_params.cpp`.
2. Runs `reference_original_tensorflow_code.py`.
3. Saves the trained model and exported weights under `models/`.

The current pattern count is `8`, so the expected outputs are:

```text
models/model_8patterns.h5
models/model_8patterns.txt
```

## Command

Run:

```bash
cd ~/Othello_AI/reference_non_submission
bash ./train_pattern_weights.sh
```

If you want to specify the TensorFlow Python explicitly:

```bash
cd ~/Othello_AI/reference_non_submission
PYTHON=/home/nakai/miniforge3_x86/envs/tensorflow/bin/python bash ./train_pattern_weights.sh
```

## Notes

- Put training records in `training_records/` before running.
- The script recompiles `evaluate.out` each time to avoid old `libstdc++` binary errors.
- The generated files are not submission code. The exported weights must still be converted into the player implementation before use.
