import json
from pathlib import Path


NOTEBOOK_PATH = Path("common/pattern_eval_common.ipynb")


def _python_source(source):
    lines = []
    for line in source.splitlines():
        stripped = line.lstrip()
        if stripped.startswith("!") or stripped.startswith("%"):
            continue
        lines.append(line)
    return "\n".join(lines)


namespace = {
    "__name__": "__main__",
    "__file__": str(NOTEBOOK_PATH),
}

notebook = json.loads(NOTEBOOK_PATH.read_text(encoding="utf-8"))
for index, cell in enumerate(notebook["cells"]):
    if cell.get("cell_type") != "code":
        continue
    source = _python_source("".join(cell.get("source", [])))
    if not source.strip():
        continue
    code = compile(source, f"{NOTEBOOK_PATH}:cell-{index}", "exec")
    exec(code, namespace)
