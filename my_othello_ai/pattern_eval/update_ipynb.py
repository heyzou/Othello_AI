import json
from pathlib import Path

path = Path("common/pattern_eval_common.ipynb")
with open(path, "r", encoding="utf-8") as f:
    data = json.load(f)

for cell in data["cells"]:
    if cell.get("cell_type") == "code":
        source = cell.get("source", [])
        
        # Replace the _play_many calls
        old_play_many = """
black_summary, black_records = _play_many(
    "MyPlayer as BLACK vs AdvancedPlayer",
    black_player=MyPlayer,
    white_player=AdvancedPlayer,
    my_color=1,
    games=GAMES_PER_SIDE,
)

white_summary, white_records = _play_many(
    "MyPlayer as WHITE vs AdvancedPlayer",
    black_player=AdvancedPlayer,
    white_player=MyPlayer,
    my_color=2,
    games=GAMES_PER_SIDE,
)
""".strip().splitlines(True)
        
        new_play_many = """PLAY_SIDE = os.environ.get("PLAY_SIDE", "both").lower()

if PLAY_SIDE in ("black", "both"):
    black_summary, black_records = _play_many(
        "MyPlayer as BLACK vs AdvancedPlayer",
        black_player=MyPlayer,
        white_player=AdvancedPlayer,
        my_color=1,
        games=GAMES_PER_SIDE,
    )
else:
    black_summary = {"games": 0, "wins": 0, "losses": 0, "draws": 0, "slowest_move_overall": None}
    black_records = []

if PLAY_SIDE in ("white", "both"):
    white_summary, white_records = _play_many(
        "MyPlayer as WHITE vs AdvancedPlayer",
        black_player=AdvancedPlayer,
        white_player=MyPlayer,
        my_color=2,
        games=GAMES_PER_SIDE,
    )
else:
    white_summary = {"games": 0, "wins": 0, "losses": 0, "draws": 0, "slowest_move_overall": None}
    white_records = []
""".splitlines(True)

        source_str = "".join(source)
        
        source_str = source_str.replace('    "win_rate": total_wins / total_games,\n', '    "win_rate": (total_wins / total_games) if total_games else 0.0,\n')
        source_str = source_str.replace('    "avg_my_diff": sum(all_diffs) / total_games,\n', '    "avg_my_diff": (sum(all_diffs) / total_games) if total_games else 0.0,\n')
        source_str = source_str.replace('    "best_my_diff": max(all_diffs),\n', '    "best_my_diff": max(all_diffs) if all_diffs else 0,\n')
        source_str = source_str.replace('    "worst_my_diff": min(all_diffs),\n', '    "worst_my_diff": min(all_diffs) if all_diffs else 0,\n')

        old_print = """for side_name, summary in (("BLACK", black_summary), ("WHITE", white_summary)):
    slow = summary["slowest_move_overall"]
    print(
        f"{side_name}: {summary['wins']}W-{summary['losses']}L-{summary['draws']}D "
        f"/ slowest game={slow['game_index']} turn={slow['turn_index']} "
        f"time={slow['elapsed_ms']:.1f}ms"
    )
slow = evaluation_result["total"]["slowest_move_overall"]
print(
    f"TOTAL: {total_wins}W-{total_losses}L-{total_draws}D "
    f"/ slowest game={slow['game_index']} turn={slow['turn_index']} "
    f"color={slow['color']} time={slow['elapsed_ms']:.1f}ms"
)"""

        new_print = """for side_name, summary in (("BLACK", black_summary), ("WHITE", white_summary)):
    if summary["games"] == 0:
        continue
    slow = summary["slowest_move_overall"]
    print(
        f"{side_name}: {summary['wins']}W-{summary['losses']}L-{summary['draws']}D "
        f"/ slowest game={slow['game_index']} turn={slow['turn_index']} "
        f"time={slow['elapsed_ms']:.1f}ms"
    )
slow = evaluation_result["total"]["slowest_move_overall"]
if slow:
    print(
        f"TOTAL: {total_wins}W-{total_losses}L-{total_draws}D "
        f"/ slowest game={slow['game_index']} turn={slow['turn_index']} "
        f"color={slow['color']} time={slow['elapsed_ms']:.1f}ms"
    )
else:
    print(f"TOTAL: {total_wins}W-{total_losses}L-{total_draws}D")"""
        
        source_str = source_str.replace(old_print, new_print)
        
        if "black_summary, black_records = _play_many" in source_str and "PLAY_SIDE" not in source_str:
            import re
            source_str = re.sub(
                r'black_summary, black_records = _play_many\(.*?\n\)\n\nwhite_summary, white_records = _play_many\(.*?\n\)',
                "".join(new_play_many).strip(),
                source_str,
                flags=re.DOTALL
            )
            
        # Write back to source lines
        lines = [line + "\n" for line in source_str.split("\n")]
        # Fix the last element if it shouldn't end with \n
        if not source_str.endswith("\n"):
            lines[-1] = lines[-1].rstrip("\n")
        else:
            lines.pop()

        cell["source"] = lines

with open(path, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=1)
    f.write("\n")
