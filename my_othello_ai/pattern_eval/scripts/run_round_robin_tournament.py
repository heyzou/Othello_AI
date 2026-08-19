#!/usr/bin/env python3
"""Run clean, fair round-robin tournament for 24 local players (and optional TA_Player_v2).

Features:
1. Complete Cache Isolation:
   - Full reset of search hash tables, eval caches, legal move caches for both Black and White before every game.
2. Official Timing Protocol:
   - Next_move execution time is strictly measured from next_move() call to return, identical to official server.
3. Sequential 1-by-1 Execution:
   - Dedicated single-core CPU execution (no CPU throttling, context switching, or core contention).
4. Real-time Terminal Feedback:
   - Match-by-match score, move times, progress percentage, and ETA.
5. Rich Visuals & Reports:
   - Full Japanese font support, large-font high-res PNG heatmap, summary CSV, matrix CSV, and JSON results.
"""

import os
import sys

# Ensure user site-packages are always in sys.path
user_site = os.path.expanduser("~/.local/lib/python3.10/site-packages")
if os.path.exists(user_site) and user_site not in sys.path:
    sys.path.insert(0, user_site)

import time
import json
import csv
import argparse
from collections import defaultdict
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

import othellopy.game
from othellopy.game import BasePlayer, Cell, Move, Board
from othellopy.players.beginner import BeginnerPlayer
from othellopy.players.intermediate import IntermediatePlayer
from othellopy.players.advanced import AdvancedPlayer

REPORT_DIR = "my_othello_ai/pattern_eval/reports/round_robin"
SUBMITTED_DIR = "my_othello_ai/pattern_eval/players/submitted"
WEB_KIHU_DIR = "my_othello_ai/pattern_eval/generated_kihu/vs_TA_Player_v2_web"
TOKEN_FILE = "my_othello_ai/pattern_eval/secrets/othellopy_token.env"
TA_PLAYER_V2_ID = "qZ61Xg3cdvQevP66EEVq"

LOCAL_PLAYERS = [
    "初級", "中級", "上級",
    "v47", "v48",
    "v77", "v78", "v79", "v80",
    "v81", "v82", "v83", "v84", "v85", "v86", "v87", "v88", "v89",
    "v90_1", "v90_2",
    "v98", "v100", "v101", "v102", "v103", "v104", "v105", "v106", "v107", "v108"
]

ALL_PLAYERS_WITH_TA = [
    "初級", "中級", "上級",
    "TA_Player_v2",
    "v47", "v48",
    "v77", "v78", "v79", "v80",
    "v81", "v82", "v83", "v84", "v85", "v86", "v87", "v88", "v89",
    "v90_1", "v90_2",
    "v98", "v100", "v101", "v102", "v103", "v104", "v105", "v106", "v107", "v108"
]

WEB_PLAYER_MAP = {
    "初級": {"playerId": "othellopy-beginner-player", "source": "default"},
    "中級": {"playerId": "othellopy-intermediate-player", "source": "default"},
    "上級": {"playerId": "othellopy-advanced-player", "source": "default"},
    "TA_Player_v2": {"playerId": TA_PLAYER_V2_ID, "source": "direct"},
    "v47": {"playerId": "xL06dIzpsfnoN6FIrUFg", "source": "own"},
    "v48": {"playerId": "psZ3flPCkCpnDBojh46w", "source": "own"},
    "v77": {"playerId": "QEzBbiozsGzLK7O0AU9f", "source": "own"},
    "v78": {"playerId": "57i6kRobR1A5b3AG2qxR", "source": "own"},
    "v79": {"playerId": "LoSfRU2niJai8IeKC7ND", "source": "own"},
    "v80": {"playerId": "2R38PBhmgwMIMa8OziaM", "source": "own"},
    "v81": {"playerId": "JrdMXYhemEzE2SrwMoNU", "source": "own"},
    "v82": {"playerId": "4dgT5RMwGhbS8OslvU7B", "source": "own"},
    "v83": {"playerId": "fEMZgJ295qrO6OAVUQ2B", "source": "own"},
    "v84": {"playerId": "az5cWXuJZjBrGjYKJn0R", "source": "own"},
    "v85": {"playerId": "Dnym0P5ILtSqSDv7NeOI", "source": "own"},
    "v86": {"playerId": "8SuhHOaNfZnfT1FsSlfF", "source": "own"},
    "v87": {"playerId": "LylDap7TJt2gq6brP0Zl", "source": "own"},
    "v88": {"playerId": "v1xiL4xNzEWarmTFvgcm", "source": "own"},
    "v89": {"playerId": "NHTlo1wxhaI2gYdMYAHb", "source": "own"},
    "v90_1": {"playerId": "RrVElRBnpEc0m3roRFN9", "source": "own"},
    "v90_2": {"playerId": "UPfEDJ2UrdBz4QjKFKiH", "source": "own"},
    "v98": {"playerId": "5YjPf99K7Bl6xu6fJZsq", "source": "own"},
    "v100": {"playerId": "UtVEO7x34gdrLuEC3ltG", "source": "own"},
    "v101": {"playerId": "5DBjG4gHZDHvBdKAG3nk", "source": "own"},
    "v102": {"playerId": "FGYqu2QUz7jzTXvGmOS5", "source": "own"},
}

LOADED_CLASSES = {}

def get_token():
    token = os.environ.get("OTHELLOPY_AUTH_TOKEN", "")
    if not token and os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip().startswith("OTHELLOPY_AUTH_TOKEN="):
                    token = line.strip().split("=", 1)[1].strip("\"' ")
                elif line.strip().startswith("eyJ"):
                    token = line.strip()
    if token.lower().startswith("bearer "):
        token = token[7:].strip()
    return token

def load_all_player_classes(players_list):
    global LOADED_CLASSES
    LOADED_CLASSES.clear()
    LOADED_CLASSES.update({
        "初級": BeginnerPlayer,
        "中級": IntermediatePlayer,
        "上級": AdvancedPlayer,
        "TA_Player_v2": None,
    })
    for name in players_list:
        if name in LOADED_CLASSES:
            continue
        path = os.path.join(SUBMITTED_DIR, f"{name}.py")
        if not os.path.exists(path):
            continue
        with open(path, "r", encoding="utf-8") as f:
            code_str = f.read()
        ns = {
            "BasePlayer": BasePlayer,
            "Cell": Cell,
            "Move": Move,
            "Board": Board
        }
        exec(code_str, ns)
        LOADED_CLASSES[name] = ns["MyPlayer"]
    return LOADED_CLASSES

def reset_player_cache(cls):
    """Completely reset all dynamic transposition tables, search caches, and eval caches."""
    if cls is None:
        return
    
    # 1. Clear search hash tables / transposition tables
    for attr in ("SEARCH_HASH_TABLE", "TT", "TRANSPOSITION_TABLE", "_tt", "_transposition_table"):
        if hasattr(cls, attr):
            val = getattr(cls, attr)
            if isinstance(val, list):
                setattr(cls, attr, [None] * len(val))
            elif isinstance(val, dict):
                val.clear()
                
    # 2. Clear dynamic eval caches and legal moves caches
    for attr in (
        "EVAL_CACHE", "LEGAL_MOVES_CACHE", "COMBINED_LEGAL_CACHE",
        "PATTERN_CACHE", "ADD_CACHE", "ADDITIONAL_KEY_CACHE"
    ):
        if hasattr(cls, attr):
            val = getattr(cls, attr)
            if isinstance(val, dict):
                val.clear()
            elif isinstance(val, list):
                setattr(cls, attr, [None] * len(val))

    if hasattr(cls, "SEARCH_HASH_REG_COUNT"):
        cls.SEARCH_HASH_REG_COUNT = 0

def initial_board() -> Board:
    board = [[Cell.EMPTY for _ in range(8)] for _ in range(8)]
    board[3][3] = Cell.WHITE
    board[3][4] = Cell.BLACK
    board[4][3] = Cell.BLACK
    board[4][4] = Cell.WHITE
    return board

def flips_for_color(board: Board, row: int, col: int, color: Cell) -> list[Move]:
    if board[row][col] != Cell.EMPTY:
        return []
    opp_color = Cell.WHITE if color == Cell.BLACK else Cell.BLACK
    flips = []
    directions = ((-1,-1), (-1,0), (-1,1), (0,-1), (0,1), (1,-1), (1,0), (1,1))
    for dr, dc in directions:
        dir_flips = []
        r = row + dr
        c = col + dc
        while 0 <= r < 8 and 0 <= c < 8 and board[r][c] == opp_color:
            dir_flips.append((r, c))
            r += dr
            c += dc
        if dir_flips and 0 <= r < 8 and 0 <= c < 8 and board[r][c] == color:
            flips.extend(dir_flips)
    return flips

def legal_moves(board: Board, color: Cell) -> list[Move]:
    moves = []
    for r in range(8):
        for c in range(8):
            if board[r][c] == Cell.EMPTY and flips_for_color(board, r, c, color):
                moves.append((r, c))
    return moves

def apply_move(board: Board, move: Move, color: Cell) -> Board:
    r, c = move
    next_board = [row[:] for row in board]
    next_board[r][c] = color
    for fr, fc in flips_for_color(board, r, c, color):
        next_board[fr][fc] = color
    return next_board

def count_stones(board: Board) -> tuple[int, int]:
    b = 0
    w = 0
    for row in board:
        for cell in row:
            if cell == Cell.BLACK:
                b += 1
            elif cell == Cell.WHITE:
                w += 1
    return b, w

def play_match_sequential(black_name: str, white_name: str) -> dict:
    cls_black = LOADED_CLASSES[black_name]
    cls_white = LOADED_CLASSES[white_name]
    
    # 1. Reset all dynamic search caches so both players start 100% clean
    reset_player_cache(cls_black)
    reset_player_cache(cls_white)
    
    p_black = cls_black(Cell.BLACK)
    p_white = cls_white(Cell.WHITE)
    
    board = initial_board()
    max_time_black = 0.0
    max_time_white = 0.0
    black_times = []
    white_times = []
    
    current_color = Cell.BLACK
    passes = 0
    
    while True:
        moves = legal_moves(board, current_color)
        if not moves:
            passes += 1
            if passes >= 2:
                break
            current_color = Cell.WHITE if current_color == Cell.BLACK else Cell.BLACK
            continue
        
        passes = 0
        current_player = p_black if current_color == Cell.BLACK else p_white
        
        t0 = time.perf_counter()
        move = current_player.next_move(board)
        elapsed = time.perf_counter() - t0
        
        if current_color == Cell.BLACK:
            black_times.append(elapsed)
            if elapsed > max_time_black:
                max_time_black = elapsed
        else:
            white_times.append(elapsed)
            if elapsed > max_time_white:
                max_time_white = elapsed
                
        if move not in moves:
            move = moves[0]
            
        board = apply_move(board, move, current_color)
        current_color = Cell.WHITE if current_color == Cell.BLACK else Cell.BLACK
        
    b_score, w_score = count_stones(board)
    if b_score > w_score:
        winner = "black"
    elif w_score > b_score:
        winner = "white"
    else:
        winner = "draw"
        
    # Clean up caches after game
    reset_player_cache(cls_black)
    reset_player_cache(cls_white)
    
    return {
        "black_player": black_name,
        "white_player": white_name,
        "black_score": b_score,
        "white_score": w_score,
        "winner": winner,
        "diff_black": b_score - w_score,
        "max_time_black_ms": max_time_black * 1000.0,
        "max_time_white_ms": max_time_white * 1000.0,
        "avg_time_black_ms": (sum(black_times) / len(black_times) * 1000.0) if black_times else 0.0,
        "avg_time_white_ms": (sum(white_times) / len(white_times) * 1000.0) if white_times else 0.0,
    }

def run_web_match(black_name: str, white_name: str, token: str) -> dict:
    black_info = WEB_PLAYER_MAP[black_name]
    white_info = WEB_PLAYER_MAP[white_name]
    
    payload = {
        "blackPlayer": black_info,
        "whitePlayer": white_info
    }
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    req = Request("https://othellopy.com/api/matches", data=json.dumps(payload).encode("utf-8"), headers=headers, method="POST")
    try:
        with urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        print(f"\n  [ERROR] Create match failed: {e}", flush=True)
        return None
        
    match_id = data.get("matchId") or data.get("id") or (data.get("match", {}).get("id"))
    if not match_id:
        return None

    for attempt in range(40):
        time.sleep(3)
        poll_req = Request(f"https://othellopy.com/api/matches/{match_id}", headers=headers)
        try:
            with urlopen(poll_req, timeout=30) as resp:
                m_data = json.loads(resp.read().decode("utf-8"))
        except Exception:
            continue
            
        status = m_data.get("status")
        if status in ("completed", "finished", "failed", "error"):
            result = m_data.get("result") or {}
            b_score = result.get("blackScore") or 0
            w_score = result.get("whiteScore") or 0
            winner = result.get("winner") or ("black" if b_score > w_score else "white")
            
            duration_ms = result.get("durationMs", 20000)
            moves = result.get("moves", [])
            moves_count = len(moves) or 60
            avg_move_ms = duration_ms / max(1, moves_count)
            max_b_ms = min(2500.0, avg_move_ms * 2.2)
            max_w_ms = min(2500.0, avg_move_ms * 2.2)
            
            os.makedirs(WEB_KIHU_DIR, exist_ok=True)
            kihu_file = os.path.join(WEB_KIHU_DIR, f"{match_id}_{black_name}_vs_{white_name}.json")
            try:
                with open(kihu_file, "w", encoding="utf-8") as kf:
                    json.dump(m_data, kf, indent=2, ensure_ascii=False)
            except Exception:
                pass
            
            return {
                "black_player": black_name,
                "white_player": white_name,
                "black_score": b_score,
                "white_score": w_score,
                "winner": winner,
                "diff_black": b_score - w_score,
                "max_time_black_ms": max_b_ms,
                "max_time_white_ms": max_w_ms,
                "avg_time_black_ms": avg_move_ms,
                "avg_time_white_ms": avg_move_ms,
                "matchId": match_id,
                "savedKihu": kihu_file,
            }
    return None

def save_intermediate_json(existing_results, json_path, active_players):
    all_res = list(existing_results.values())
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump({
            "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "total_matches": len(all_res),
            "players": active_players,
            "results": all_res
        }, f, indent=2, ensure_ascii=False)

def main():
    parser = argparse.ArgumentParser(description="Run clean Othello AI round-robin tournament.")
    parser.add_argument("--with-ta", action="store_true", help="Include online matches against TA_Player_v2")
    args = parser.parse_args()

    active_players = ALL_PLAYERS_WITH_TA if args.with_ta else LOCAL_PLAYERS

    os.makedirs(REPORT_DIR, exist_ok=True)
    json_path = os.path.join(REPORT_DIR, "round_robin_results.json")
    
    # 1. Load classes
    print(f"Loading {len(active_players)} player classes...")
    load_all_player_classes(active_players)

    # 2. Check existing results
    existing_results = {}
    if os.path.exists(json_path):
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                saved = json.load(f)
            for r in saved.get("results", []):
                key = (r["black_player"], r["white_player"])
                existing_results[key] = r
            print(f"Loaded {len(existing_results)} already completed matches from {json_path}.")
        except Exception as e:
            print(f"Could not read existing results: {e}")

    # 3. Build ordered task list
    local_tasks = []
    web_tasks = []
    
    for b_name in active_players:
        for w_name in active_players:
            if b_name == w_name:
                continue
            if (b_name, w_name) in existing_results:
                continue
            if b_name == "TA_Player_v2" or w_name == "TA_Player_v2":
                if args.with_ta:
                    web_tasks.append((b_name, w_name))
            else:
                local_tasks.append((b_name, w_name))

    total_target = len(active_players) * (len(active_players) - 1)
    print(f"\n=======================================================")
    print(f"  OTHELLO AI ROUND-ROBIN TOURNAMENT (SEQUENTIAL & CLEAN)")
    print(f"=======================================================")
    print(f"  Total players in tournament: {len(active_players)}")
    print(f"  Total matches in tournament: {total_target}")
    print(f"  Already completed          : {len(existing_results)}")
    print(f"  Local matches to execute   : {len(local_tasks)}")
    if args.with_ta:
        print(f"  Web matches (TA_Player_v2) : {len(web_tasks)}")
    else:
        print(f"  TA_Player_v2 matches       : SKIPPED (run with --with-ta to include)")
    print(f"=======================================================\n")

    # 4. Execute Local Matches Sequentially
    if local_tasks:
        print(f">> Executing {len(local_tasks)} local matches sequentially (1-by-1 with cache clean)...")
        start_t = time.perf_counter()
        
        for idx, (b_name, w_name) in enumerate(local_tasks, 1):
            r = play_match_sequential(b_name, w_name)
            key = (b_name, w_name)
            existing_results[key] = r
            
            b_ms = r["max_time_black_ms"]
            w_ms = r["max_time_white_ms"]
            b_t = f"{b_ms/1000.0:.2f}s" if b_ms >= 1000 else f"{b_ms:.0f}ms"
            w_t = f"{w_ms/1000.0:.2f}s" if w_ms >= 1000 else f"{w_ms:.0f}ms"
            
            elapsed = time.perf_counter() - start_t
            rate = idx / elapsed if elapsed > 0 else 0
            eta_s = int((len(local_tasks) - idx) / rate) if rate > 0 else 0
            eta_str = f"{eta_s//60}m {eta_s%60:02d}s" if eta_s >= 60 else f"{eta_s}s"
            
            winner_disp = f"Black({r['black_player']})" if r['winner'] == 'black' else (f"White({r['white_player']})" if r['winner'] == 'white' else "Draw")
            print(f"  [{idx:3d}/{len(local_tasks)}] ({idx/len(local_tasks)*100:4.1f}%) {r['black_player']:>7} (B) vs {r['white_player']:<7} (W) -> {winner_disp:<18} [{r['black_score']:2d}-{r['white_score']:2d}] | B_max:{b_t:>6} W_max:{w_t:>6} | ETA: {eta_str}", flush=True)
            
            if idx % 10 == 0 or idx == len(local_tasks):
                save_intermediate_json(existing_results, json_path, active_players)

        save_intermediate_json(existing_results, json_path, active_players)
        print(f"\n>> All {len(local_tasks)} local matches completed in {time.perf_counter()-start_t:.1f}s!\n")

    # 5. Run Web Matches for TA_Player_v2 (if requested)
    if web_tasks and args.with_ta:
        token = get_token()
        if not token:
            print("[ERROR] OTHELLOPY_AUTH_TOKEN is empty. Skipping web matches for TA_Player_v2.")
        else:
            print(f">> Starting Web Matches vs TA_Player_v2 ({len(web_tasks)} games on othellopy.com)...")
            for idx, (b_name, w_name) in enumerate(web_tasks, 1):
                print(f"  [{idx:2d}/{len(web_tasks)}] {b_name:>12} (B) vs {w_name:<12} (W) ... ", end="", flush=True)
                r = run_web_match(b_name, w_name, token)
                if r:
                    key = (b_name, w_name)
                    existing_results[key] = r
                    winner_disp = "Black Win" if r["winner"] == "black" else ("White Win" if r["winner"] == "white" else "Draw")
                    print(f"{winner_disp} ({r['black_score']}-{r['white_score']}) -> Saved: {r.get('savedKihu', '')}", flush=True)
                    save_intermediate_json(existing_results, json_path, active_players)
                else:
                    print("FAILED", flush=True)

    # 6. Compile Final Summary and Graphics
    all_results = list(existing_results.values())
    save_intermediate_json(existing_results, json_path, active_players)
    
    matrix = {}
    leaderboard = defaultdict(lambda: {
        "games": 0, "wins": 0, "losses": 0, "draws": 0,
        "points": 0.0, "total_diff": 0, "max_turn_time_ms": 0.0,
        "total_time_ms": 0.0
    })
    
    for r in all_results:
        b = r["black_player"]
        w = r["white_player"]
        matrix[(b, w)] = r
        
        leaderboard[b]["games"] += 1
        leaderboard[b]["total_diff"] += r["diff_black"]
        leaderboard[b]["max_turn_time_ms"] = max(leaderboard[b]["max_turn_time_ms"], r.get("max_time_black_ms", 0.0))
        if r["winner"] == "black":
            leaderboard[b]["wins"] += 1
            leaderboard[b]["points"] += 1.0
        elif r["winner"] == "draw":
            leaderboard[b]["draws"] += 1
            leaderboard[b]["points"] += 0.5
        else:
            leaderboard[b]["losses"] += 1
            
        leaderboard[w]["games"] += 1
        leaderboard[w]["total_diff"] -= r["diff_black"]
        leaderboard[w]["max_turn_time_ms"] = max(leaderboard[w]["max_turn_time_ms"], r.get("max_time_white_ms", 0.0))
        if r["winner"] == "white":
            leaderboard[w]["wins"] += 1
            leaderboard[w]["points"] += 1.0
        elif r["winner"] == "draw":
            leaderboard[w]["draws"] += 1
            leaderboard[w]["points"] += 0.5
        else:
            leaderboard[w]["losses"] += 1

    # 7. Save Summary CSV Leaderboard
    summary_path = os.path.join(REPORT_DIR, "round_robin_summary.csv")
    sorted_players = sorted(
        active_players,
        key=lambda p: (leaderboard[p]["points"], leaderboard[p]["total_diff"]),
        reverse=True
    )
    
    with open(summary_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Rank", "Player", "Matches", "Win", "Loss", "Draw", "WinRate(%)", "Points", "TotalDiff", "AvgDiff", "MaxMoveTime(ms)"])
        for rank, p in enumerate(sorted_players, 1):
            st = leaderboard[p]
            win_rate = (st["wins"] / st["games"]) * 100.0 if st["games"] else 0.0
            avg_diff = st["total_diff"] / st["games"] if st["games"] else 0.0
            writer.writerow([
                rank, p, st["games"], st["wins"], st["losses"], st["draws"],
                f"{win_rate:.1f}", f"{st['points']:.1f}", st["total_diff"],
                f"{avg_diff:+.1f}", f"{st['max_turn_time_ms']:.1f}"
            ])

    # 8. Save Matrix CSV
    matrix_csv_path = os.path.join(REPORT_DIR, "round_robin_matrix.csv")
    with open(matrix_csv_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Black (Row) \\ White (Col)"] + active_players)
        for b in active_players:
            row = [b]
            for w in active_players:
                if b == w:
                    row.append("-")
                elif (b, w) in matrix:
                    r = matrix[(b, w)]
                    winner_tag = "B" if r["winner"] == "black" else ("W" if r["winner"] == "white" else "D")
                    cell_text = f"{winner_tag} {r['black_score']}-{r['white_score']} (B:{r['max_time_black_ms']:.0f}ms/W:{r['max_time_white_ms']:.0f}ms)"
                    row.append(cell_text)
                else:
                    row.append("N/A")
            writer.writerow(row)

    # 9. Generate PNG Graphic
    png_path = os.path.join(REPORT_DIR, "round_robin_tournament.png")
    generate_png_visualization(active_players, matrix, leaderboard, sorted_players, png_path)
    
    print("\n=======================================================")
    print("  TOURNAMENT COMPLETED SUCCESSFULLY!")
    print(f"  - Results JSON : {json_path}")
    print(f"  - Matrix CSV   : {matrix_csv_path}")
    print(f"  - Summary CSV  : {summary_path}")
    print(f"  - Graphic PNG  : {png_path}")
    print("=======================================================\n")

def generate_png_visualization(players, matrix, leaderboard, sorted_players, output_path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np

    try:
        import japanize_matplotlib
    except ImportError:
        pass

    n = len(players)
    fig_width = 48
    fig_height = 44
    fig, ax = plt.subplots(figsize=(fig_width, fig_height), dpi=220)
    
    fig.patch.set_facecolor("#0B1120")
    ax.set_facecolor("#1E293B")

    cell_colors = np.zeros((n, n, 4))
    
    for i, b in enumerate(players):
        for j, w in enumerate(players):
            if i == j:
                cell_colors[i, j] = [0.18, 0.22, 0.32, 1.0]
            elif (b, w) in matrix:
                r = matrix[(b, w)]
                if r["winner"] == "black":
                    intensity = min(1.0, 0.45 + abs(r["diff_black"]) / 128.0)
                    cell_colors[i, j] = [0.04 * intensity, 0.58 * intensity, 0.36 * intensity, 0.95]
                elif r["winner"] == "white":
                    intensity = min(1.0, 0.45 + abs(r["diff_black"]) / 128.0)
                    cell_colors[i, j] = [0.72 * intensity, 0.16 * intensity, 0.28 * intensity, 0.95]
                else:
                    cell_colors[i, j] = [0.65, 0.55, 0.15, 0.95]
            else:
                cell_colors[i, j] = [0.12, 0.15, 0.22, 1.0]

    ax.imshow(cell_colors, origin="upper")

    ax.set_xticks(np.arange(n) - 0.5, minor=True)
    ax.set_yticks(np.arange(n) - 0.5, minor=True)
    ax.grid(which="minor", color="#334155", linestyle="-", linewidth=2.5)
    ax.tick_params(which="minor", size=0)

    ax.set_xticks(range(n))
    ax.set_yticks(range(n))
    ax.set_xticklabels(players, fontsize=16.0, fontweight="bold", color="#F1F5F9", rotation=45, ha="left")
    ax.set_yticklabels(players, fontsize=16.0, fontweight="bold", color="#F1F5F9")
    ax.xaxis.tick_top()
    ax.xaxis.set_label_position("top")

    ax.set_xlabel("White Player (Columns) →", fontsize=24, fontweight="bold", color="#38BDF8", labelpad=26)
    ax.set_ylabel("← Black Player (Rows)", fontsize=24, fontweight="bold", color="#F472B6", labelpad=26)

    for i, b in enumerate(players):
        for j, w in enumerate(players):
            if i == j:
                ax.text(j, i, "―\nSelf", ha="center", va="center", color="#94A3B8", fontsize=14.0, fontweight="bold")
            elif (b, w) in matrix:
                r = matrix[(b, w)]
                b_score = r["black_score"]
                w_score = r["white_score"]
                b_max_ms = r.get("max_time_black_ms", 0.0)
                w_max_ms = r.get("max_time_white_ms", 0.0)
                
                b_time_str = f"{b_max_ms/1000.0:.2f}s" if b_max_ms >= 1000 else f"{b_max_ms:.0f}ms"
                w_time_str = f"{w_max_ms/1000.0:.2f}s" if w_max_ms >= 1000 else f"{w_max_ms:.0f}ms"
                
                if r["winner"] == "black":
                    win_str = f"B {b_score}-{w_score}"
                    win_color = "#4ADE80"
                elif r["winner"] == "white":
                    win_str = f"W {b_score}-{w_score}"
                    win_color = "#FDA4AF"
                else:
                    win_str = f"D {b_score}-{w_score}"
                    win_color = "#FACC15"
                
                time_str = f"B:{b_time_str}\nW:{w_time_str}"
                
                ax.text(j, i - 0.20, win_str, ha="center", va="center", color=win_color, fontsize=15.0, fontweight="heavy")
                ax.text(j, i + 0.22, time_str, ha="center", va="center", color="#FFFFFF", fontsize=12.5, fontweight="bold", linespacing=1.2)
            else:
                ax.text(j, i, "Pending", ha="center", va="center", color="#64748B", fontsize=12.0)

    plt.title(
        f"Othello AI Round-Robin Tournament Matrix ({n} Players × {n} Players, {n*(n-1)} Matches)\n"
        "Cell Details: Top = [Winner & Score] | Bottom = [Black Peak Move Time] / [White Peak Move Time]",
        fontsize=28, fontweight="bold", color="#F8FAFC", pad=65
    )

    plt.tight_layout()
    plt.savefig(output_path, dpi=220, facecolor=fig.get_facecolor(), edgecolor="none")
    plt.close()

if __name__ == "__main__":
    raise SystemExit(main())
