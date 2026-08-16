import re

with open('players/experiments/exp_051_060/exp_051_fast_eval.py', 'r') as f:
    code = f.read()

code = re.sub(
    r'    _accum_eval_hit_time = 0\.0\n',
    r'    _accum_eval_hit_time = 0.0\n    _cache_stats = {"EVAL": [0, 0], "MOBILITY": [0, 0], "ADD_KEY": [0, 0], "LEGAL_MOVES": [0, 0], "LEGAL_MASK": [0, 0], "TT_HASH": [0, 0]}\n',
    code,
    count=1
)

with open('players/experiments/exp_051_060/exp_051_fast_eval.py', 'w') as f:
    f.write(code)

print("Fixed!")
