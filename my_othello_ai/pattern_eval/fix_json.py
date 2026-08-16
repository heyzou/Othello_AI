import re

with open('players/experiments/exp_051_060/exp_051_fast_eval.py', 'r') as f:
    code = f.read()

code = re.sub(
    r'(            print\(f"         └─ \[Eval Breakdown\].*?"\))',
    r'\1\n            if actual_turn in (21, 32):\n                import json\n                with open(f"cache_stats_{actual_turn}.json", "w") as f:\n                    json.dump(MyPlayer._cache_stats, f)',
    code,
    count=1
)

with open('players/experiments/exp_051_060/exp_051_fast_eval.py', 'w') as f:
    f.write(code)

print("Fixed JSON!")
