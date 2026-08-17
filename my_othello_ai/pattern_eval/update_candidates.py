import json
from pathlib import Path

path = Path("common/pattern_eval_common.ipynb")
with open(path, "r", encoding="utf-8") as f:
    data = json.load(f)

for cell in data["cells"]:
    if cell.get("cell_type") == "code":
        source = cell.get("source", [])
        source_str = "".join(source)
        
        old_str = '    Path("my_othello_ai/pattern_eval/players/experiments") / Path(MYPLAYER_FILE).name,\n'
        new_str = '    Path("my_othello_ai/pattern_eval/players/experiments") / Path(MYPLAYER_FILE).name,\n' + \
                  '    Path("my_othello_ai/pattern_eval/players/experiments/exp_071_080") / Path(MYPLAYER_FILE).name,\n'
                  
        if old_str in source_str and new_str not in source_str:
            source_str = source_str.replace(old_str, new_str)
            
            lines = [line + "\n" for line in source_str.split("\n")]
            if not source_str.endswith("\n"):
                lines[-1] = lines[-1].rstrip("\n")
            else:
                lines.pop()
            cell["source"] = lines

with open(path, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=1)
    f.write("\n")
