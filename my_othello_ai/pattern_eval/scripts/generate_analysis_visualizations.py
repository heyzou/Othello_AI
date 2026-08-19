#!/usr/bin/env python3
"""Generate rich PNG visualizations for Othello AI round-robin results:
1. round_robin_overall_rankings.png : Black, White, and Total win-rate rankings + avg/max times.
2. round_robin_limit_1.8s.png       : Leaderboard and matrix under 1.8s timeout rule.
3. round_robin_limit_1.6s.png       : Leaderboard and matrix under 1.6s timeout rule.
4. round_robin_limit_1.4s.png       : Leaderboard and matrix under 1.4s timeout rule.
"""

import os
import sys
import json
from collections import defaultdict

# Ensure user site-packages
user_site = os.path.expanduser("~/.local/lib/python3.10/site-packages")
if os.path.exists(user_site) and user_site not in sys.path:
    sys.path.insert(0, user_site)

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

try:
    import japanize_matplotlib
except ImportError:
    pass

REPORT_DIR = "my_othello_ai/pattern_eval/reports/round_robin"
JSON_PATH = os.path.join(REPORT_DIR, "round_robin_results.json")

def load_data():
    with open(JSON_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data["results"], data["players"]

def compute_base_stats(results, players):
    stats = defaultdict(lambda: {
        'total_games': 0, 'total_wins': 0, 'total_losses': 0, 'total_draws': 0, 'total_points': 0.0, 'total_diff': 0,
        'black_games': 0, 'black_wins': 0, 'black_losses': 0, 'black_draws': 0, 'black_points': 0.0, 'black_diff': 0,
        'white_games': 0, 'white_wins': 0, 'white_losses': 0, 'white_draws': 0, 'white_points': 0.0, 'white_diff': 0,
        'all_avg_times': [], 'black_avg_times': [], 'white_avg_times': [],
        'max_time': 0.0, 'max_time_b': 0.0, 'max_time_w': 0.0
    })

    matrix = {}
    for r in results:
        b = r['black_player']
        w = r['white_player']
        matrix[(b, w)] = r
        diff_b = r['diff_black']
        winner = r['winner']
        
        tb_max = r.get('max_time_black_ms', 0.0) / 1000.0
        tw_max = r.get('max_time_white_ms', 0.0) / 1000.0
        tb_avg = r.get('avg_time_black_ms', 0.0)
        tw_avg = r.get('avg_time_white_ms', 0.0)
        
        # Black
        stats[b]['total_games'] += 1
        stats[b]['black_games'] += 1
        stats[b]['total_diff'] += diff_b
        stats[b]['black_diff'] += diff_b
        stats[b]['all_avg_times'].append(tb_avg)
        stats[b]['black_avg_times'].append(tb_avg)
        stats[b]['max_time'] = max(stats[b]['max_time'], tb_max)
        stats[b]['max_time_b'] = max(stats[b]['max_time_b'], tb_max)
        if winner == 'black':
            stats[b]['total_wins'] += 1
            stats[b]['black_wins'] += 1
            stats[b]['total_points'] += 1.0
            stats[b]['black_points'] += 1.0
        elif winner == 'draw':
            stats[b]['total_draws'] += 1
            stats[b]['black_draws'] += 1
            stats[b]['total_points'] += 0.5
            stats[b]['black_points'] += 0.5
        else:
            stats[b]['total_losses'] += 1
            stats[b]['black_losses'] += 1
            
        # White
        stats[w]['total_games'] += 1
        stats[w]['white_games'] += 1
        stats[w]['total_diff'] -= diff_b
        stats[w]['white_diff'] -= diff_b
        stats[w]['all_avg_times'].append(tw_avg)
        stats[w]['white_avg_times'].append(tw_avg)
        stats[w]['max_time'] = max(stats[w]['max_time'], tw_max)
        stats[w]['max_time_w'] = max(stats[w]['max_time_w'], tw_max)
        if winner == 'white':
            stats[w]['total_wins'] += 1
            stats[w]['white_wins'] += 1
            stats[w]['total_points'] += 1.0
            stats[w]['white_points'] += 1.0
        elif winner == 'draw':
            stats[w]['total_draws'] += 1
            stats[w]['white_draws'] += 1
            stats[w]['total_points'] += 0.5
            stats[w]['white_points'] += 0.5
        else:
            stats[w]['total_losses'] += 1
            stats[w]['white_losses'] += 1

    return stats, matrix

def generate_overall_rankings_png(results, players, stats):
    """Generate 3-way ranking breakdown PNG (Total, Black, White)."""
    fig = plt.figure(figsize=(48, 28), dpi=200)
    fig.patch.set_facecolor("#090D16")

    plt.suptitle(
        "Othello AI 総当たり戦 詳細分析ランキング（白黒総合・先手黒・後手白 & 思考時間詳細）\n"
        f"全 {len(players)} モデル / {len(results)} 試合 完全逐次測定 (キャッシュ完全分離・公式タイマー準拠)",
        fontsize=28, fontweight="bold", color="#F8FAFC", y=0.97
    )

    # Sorts
    by_total = sorted(players, key=lambda p: (stats[p]['total_points']/stats[p]['total_games'], stats[p]['total_diff']), reverse=True)
    by_black = sorted(players, key=lambda p: (stats[p]['black_points']/stats[p]['black_games'], stats[p]['black_diff']), reverse=True)
    by_white = sorted(players, key=lambda p: (stats[p]['white_points']/stats[p]['white_games'], stats[p]['white_diff']), reverse=True)

    gs = fig.add_gridspec(1, 3, left=0.02, right=0.98, top=0.90, bottom=0.05, wspace=0.10)

    # 1. TOTAL RANKING TABLE
    ax1 = fig.add_subplot(gs[0, 0])
    ax1.set_facecolor("#0F172A")
    ax1.axis("off")
    ax1.set_title("【1】白黒総合 勝率ランキング (Total)", fontsize=21, fontweight="bold", color="#38BDF8", pad=15)

    headers1 = ["順位", "モデル", "総合勝率", "勝-敗", "得失差", "黒平均", "黒最大", "白平均", "白最大"]
    rows1 = []
    for i, p in enumerate(by_total, 1):
        st = stats[p]
        wr = st['total_wins'] / st['total_games'] * 100
        b_avg = sum(st['black_avg_times'])/len(st['black_avg_times']) if st['black_avg_times'] else 0
        w_avg = sum(st['white_avg_times'])/len(st['white_avg_times']) if st['white_avg_times'] else 0
        rows1.append([
            f"{i}", p, f"{wr:.1f}%", f"{st['total_wins']}-{st['total_losses']}",
            f"{st['total_diff']:+d}", f"{b_avg:.0f}ms", f"{st['max_time_b']:.2f}s",
            f"{w_avg:.0f}ms", f"{st['max_time_w']:.2f}s"
        ])
    
    t1 = ax1.table(cellText=rows1, colLabels=headers1, loc="center", cellLoc="center")
    t1.auto_set_font_size(False)
    t1.set_fontsize(11.0)
    t1.scale(1.0, 1.85)

    # 2. BLACK RANKING TABLE
    ax2 = fig.add_subplot(gs[0, 1])
    ax2.set_facecolor("#0F172A")
    ax2.axis("off")
    ax2.set_title("【2】先手 (黒番) 勝率ランキング (Black)", fontsize=21, fontweight="bold", color="#F472B6", pad=15)

    headers2 = ["順位", "モデル", "黒勝率", "勝-敗", "得失差", "黒平均時間", "黒最大時間"]
    rows2 = []
    for i, p in enumerate(by_black, 1):
        st = stats[p]
        wr = st['black_wins'] / st['black_games'] * 100
        avg_t = sum(st['black_avg_times'])/len(st['black_avg_times']) if st['black_avg_times'] else 0
        rows2.append([
            f"{i}", p, f"{wr:.1f}%", f"{st['black_wins']}-{st['black_losses']}",
            f"{st['black_diff']:+d}", f"{avg_t:.0f}ms", f"{st['max_time_b']:.2f}s"
        ])
    
    t2 = ax2.table(cellText=rows2, colLabels=headers2, loc="center", cellLoc="center")
    t2.auto_set_font_size(False)
    t2.set_fontsize(12.0)
    t2.scale(1.0, 1.85)

    # 3. WHITE RANKING TABLE
    ax3 = fig.add_subplot(gs[0, 2])
    ax3.set_facecolor("#0F172A")
    ax3.axis("off")
    ax3.set_title("【3】後手 (白番) 勝率ランキング (White)", fontsize=21, fontweight="bold", color="#A78BFA", pad=15)

    headers3 = ["順位", "モデル", "白勝率", "勝-敗", "得失差", "白平均時間", "白最大時間"]
    rows3 = []
    for i, p in enumerate(by_white, 1):
        st = stats[p]
        wr = st['white_wins'] / st['white_games'] * 100
        avg_t = sum(st['white_avg_times'])/len(st['white_avg_times']) if st['white_avg_times'] else 0
        rows3.append([
            f"{i}", p, f"{wr:.1f}%", f"{st['white_wins']}-{st['white_losses']}",
            f"{st['white_diff']:+d}", f"{avg_t:.0f}ms", f"{st['max_time_w']:.2f}s"
        ])
    
    t3 = ax3.table(cellText=rows3, colLabels=headers3, loc="center", cellLoc="center")
    t3.auto_set_font_size(False)
    t3.set_fontsize(12.0)
    t3.scale(1.0, 1.85)

    # Styling tables
    for tbl, highlight_color in [(t1, "#0284C7"), (t2, "#DB2777"), (t3, "#7C3AED")]:
        for (r, c), cell in tbl.get_celld().items():
            cell.set_edgecolor("#334155")
            cell.set_linewidth(1.2)
            if r == 0:
                cell.set_facecolor(highlight_color)
                cell.set_text_props(color="#FFFFFF", fontweight="bold", fontsize=13.0)
            else:
                if r <= 3:
                    cell.set_facecolor("#1E293B" if r % 2 == 0 else "#253348")
                    cell.set_text_props(color="#FDE047" if c == 0 else "#F8FAFC", fontweight="bold")
                else:
                    cell.set_facecolor("#111827" if r % 2 == 0 else "#1A2234")
                    cell.set_text_props(color="#CBD5E1")

    out_path = os.path.join(REPORT_DIR, "round_robin_overall_rankings.png")
    plt.savefig(out_path, dpi=200, facecolor=fig.get_facecolor(), edgecolor="none")
    plt.close()
    print(f"Generated: {out_path}")

def generate_timeout_limit_png(results, players, limit_s):
    """Generate separate PNG for tournament under timeout limit (e.g. 1.8s, 1.6s, 1.4s)."""
    limit_ms = limit_s * 1000.0
    
    st = defaultdict(lambda: {
        'games': 0, 'wins': 0, 'losses': 0, 'draws': 0, 'points': 0.0, 'diff': 0,
        'to_losses': 0, 'max_t': 0.0, 'avg_t': []
    })
    
    matrix = {}
    for r in results:
        b = r['black_player']
        w = r['white_player']
        tb = r.get('max_time_black_ms', 0.0)
        tw = r.get('max_time_white_ms', 0.0)
        
        b_to = (tb >= limit_ms)
        w_to = (tw >= limit_ms)
        
        if b_to and w_to:
            adj = 'both_timeout'
        elif b_to:
            adj = 'white'
        elif w_to:
            adj = 'black'
        else:
            adj = r['winner']
            
        matrix[(b, w)] = {
            'orig_winner': r['winner'],
            'adj_winner': adj,
            'b_to': b_to,
            'w_to': w_to,
            'black_score': r['black_score'],
            'white_score': r['white_score'],
            'diff_black': r['diff_black'],
            'tb': tb,
            'tw': tw
        }
        
        st[b]['games'] += 1
        st[b]['max_t'] = max(st[b]['max_t'], tb)
        st[b]['max_t_b'] = max(st[b].get('max_t_b', 0.0), tb)
        st[b].setdefault('b_avg_t', []).append(r.get('avg_time_black_ms', 0.0))
        if b_to:
            st[b]['to_losses'] += 1
            st[b]['losses'] += 1
            st[b]['diff'] -= 64
        elif adj == 'black':
            st[b]['wins'] += 1
            st[b]['points'] += 1.0
            st[b]['diff'] += r['diff_black']
        elif adj == 'draw':
            st[b]['draws'] += 1
            st[b]['points'] += 0.5
        else:
            st[b]['losses'] += 1
            st[b]['diff'] += r['diff_black']
            
        st[w]['games'] += 1
        st[w]['max_t'] = max(st[w]['max_t'], tw)
        st[w]['max_t_w'] = max(st[w].get('max_t_w', 0.0), tw)
        st[w].setdefault('w_avg_t', []).append(r.get('avg_time_white_ms', 0.0))
        if w_to:
            st[w]['to_losses'] += 1
            st[w]['losses'] += 1
            st[w]['diff'] -= 64
        elif adj == 'white':
            st[w]['wins'] += 1
            st[w]['points'] += 1.0
            st[w]['diff'] -= r['diff_black']
        elif adj == 'draw':
            st[w]['draws'] += 1
            st[w]['points'] += 0.5
        else:
            st[w]['losses'] += 1
            st[w]['diff'] -= r['diff_black']

    sorted_players = sorted(players, key=lambda p: (st[p]['points']/st[p]['games'], st[p]['diff']), reverse=True)

    n = len(players)
    fig = plt.figure(figsize=(50, 38), dpi=200)
    fig.patch.set_facecolor("#090D16")

    plt.suptitle(
        f"Othello AI 総当たり戦 【{limit_s:.1f}秒制限】 ルール適用結果\n"
        f"（1手の最高消費時間が {limit_s:.1f}s 以上の試合はすべて「時間切れ反則負け」として判定）",
        fontsize=28, fontweight="bold", color="#F8FAFC", y=0.97
    )

    gs = fig.add_gridspec(1, 2, left=0.02, right=0.98, top=0.91, bottom=0.04, width_ratios=[1.35, 2.1], wspace=0.07)

    # 1. LEFT: Leaderboard Table
    ax_table = fig.add_subplot(gs[0, 0])
    ax_table.set_facecolor("#0F172A")
    ax_table.axis("off")
    ax_table.set_title(f"【{limit_s:.1f}s 制限】 総合順位表 (Leaderboard)", fontsize=22, fontweight="bold", color="#38BDF8", pad=15)

    headers = ["順位", "モデル", "有効勝率", "勝-敗", "反則負", "得失差", "黒平均", "黒最大", "白平均", "白最大"]
    rows = []
    for i, p in enumerate(sorted_players, 1):
        s = st[p]
        wr = s['wins'] / s['games'] * 100
        b_avg = sum(s.get('b_avg_t', []))/len(s.get('b_avg_t', [])) if s.get('b_avg_t') else 0
        w_avg = sum(s.get('w_avg_t', []))/len(s.get('w_avg_t', [])) if s.get('w_avg_t') else 0
        b_max = s.get('max_t_b', 0.0) / 1000.0
        w_max = s.get('max_t_w', 0.0) / 1000.0
        rows.append([
            f"{i}", p, f"{wr:.1f}%", f"{s['wins']}-{s['losses']}",
            f"{s['to_losses']}回", f"{s['diff']:+d}",
            f"{b_avg:.0f}ms", f"{b_max:.2f}s",
            f"{w_avg:.0f}ms", f"{w_max:.2f}s"
        ])
    
    t_obj = ax_table.table(cellText=rows, colLabels=headers, loc="center", cellLoc="center")
    t_obj.auto_set_font_size(False)
    t_obj.set_fontsize(11.0)
    t_obj.scale(1.0, 2.05)

    for (r, c), cell in t_obj.get_celld().items():
        cell.set_edgecolor("#334155")
        cell.set_linewidth(1.2)
        if r == 0:
            cell.set_facecolor("#0369A1")
            cell.set_text_props(color="#FFFFFF", fontweight="bold", fontsize=13.5)
        else:
            to_cnt = int(rows[r-1][4].replace("回", ""))
            if r <= 3:
                cell.set_facecolor("#1E293B" if r % 2 == 0 else "#283548")
                cell.set_text_props(color="#FDE047" if c == 0 else ("#F87171" if c == 4 and to_cnt > 0 else "#F8FAFC"), fontweight="bold")
            else:
                cell.set_facecolor("#111827" if r % 2 == 0 else "#1A2234")
                cell.set_text_props(color="#F87171" if c == 4 and to_cnt > 0 else "#CBD5E1")

    # 2. RIGHT: Match Matrix with Timeout Highlights
    ax_mat = fig.add_subplot(gs[0, 1])
    ax_mat.set_facecolor("#0F172A")
    
    cell_colors = np.zeros((n, n, 4))
    timeout_rects = []
    
    for i, b in enumerate(players):
        for j, w in enumerate(players):
            if i == j:
                cell_colors[i, j] = [0.15, 0.18, 0.25, 1.0]
            elif (b, w) in matrix:
                m = matrix[(b, w)]
                if m['b_to'] and m['w_to']:
                    # Both timeout: Bright Yellow
                    cell_colors[i, j] = [0.98, 0.85, 0.38, 1.0]
                    timeout_rects.append((j, i, "#EAB308"))
                elif m['b_to']:
                    # Black timed out -> White won: Bright Soft Pink/Rose (High Lightness Contrast!)
                    cell_colors[i, j] = [0.99, 0.72, 0.76, 1.0]
                    timeout_rects.append((j, i, "#F43F5E"))
                elif m['w_to']:
                    # White timed out -> Black won: Bright Mint/Light Green (High Lightness Contrast!)
                    cell_colors[i, j] = [0.65, 0.94, 0.75, 1.0]
                    timeout_rects.append((j, i, "#10B981"))
                elif m['adj_winner'] == "black":
                    # Normal Black win: Dark Deep Forest Green
                    cell_colors[i, j] = [0.03, 0.32, 0.19, 1.0]
                elif m['adj_winner'] == "white":
                    # Normal White win: Dark Deep Crimson Wine
                    cell_colors[i, j] = [0.45, 0.08, 0.16, 1.0]
                else:
                    cell_colors[i, j] = [0.35, 0.30, 0.10, 1.0]
            else:
                cell_colors[i, j] = [0.08, 0.10, 0.16, 1.0]

    ax_mat.imshow(cell_colors, origin="upper")
    ax_mat.set_xticks(np.arange(n) - 0.5, minor=True)
    ax_mat.set_yticks(np.arange(n) - 0.5, minor=True)
    ax_mat.grid(which="minor", color="#334155", linestyle="-", linewidth=2.0)
    ax_mat.tick_params(which="minor", size=0)

    # Draw colored high-visibility borders on timeout cells
    import matplotlib.patches as patches
    for c_x, c_y, border_color in timeout_rects:
        rect = patches.Rectangle(
            (c_x - 0.48, c_y - 0.48), 0.96, 0.96,
            linewidth=3.5, edgecolor=border_color, facecolor="none", zorder=3
        )
        ax_mat.add_patch(rect)

    ax_mat.set_xticks(range(n))
    ax_mat.set_yticks(range(n))
    ax_mat.set_xticklabels(players, fontsize=13.0, fontweight="bold", color="#F1F5F9", rotation=45, ha="left")
    ax_mat.set_yticklabels(players, fontsize=13.0, fontweight="bold", color="#F1F5F9")
    ax_mat.xaxis.tick_top()
    ax_mat.xaxis.set_label_position("top")

    ax_mat.set_xlabel("White Player (Columns) →", fontsize=20, fontweight="bold", color="#38BDF8", labelpad=20)
    ax_mat.set_ylabel("← Black Player (Rows)", fontsize=20, fontweight="bold", color="#F472B6", labelpad=20)

    for i, b in enumerate(players):
        for j, w in enumerate(players):
            if i == j:
                ax_mat.text(j, i, "―\nSelf", ha="center", va="center", color="#64748B", fontsize=11.0, fontweight="bold")
            elif (b, w) in matrix:
                m = matrix[(b, w)]
                tb_s = m['tb'] / 1000.0
                tw_s = m['tw'] / 1000.0
                
                b_str = f"{tb_s:.2f}s" if tb_s >= 1.0 else f"{m['tb']:.0f}ms"
                w_str = f"{tw_s:.2f}s" if tw_s >= 1.0 else f"{m['tw']:.0f}ms"
                
                if m['b_to'] and m['w_to']:
                    win_str = "【両者超過】"
                    win_color = "#854D0E"
                    time_color = "#713F12"
                elif m['b_to']:
                    # Bright pink background -> Dark Burgundy Text for extreme contrast!
                    win_str = "W [黒超過]"
                    win_color = "#881337"
                    time_color = "#4C0519"
                elif m['w_to']:
                    # Bright mint background -> Dark Forest Text for extreme contrast!
                    win_str = "B [白超過]"
                    win_color = "#064E3B"
                    time_color = "#022C22"
                elif m['adj_winner'] == "black":
                    # Dark green background -> Bright Mint Text
                    win_str = f"B {m['black_score']}-{m['white_score']}"
                    win_color = "#86EFAC"
                    time_color = "#E2E8F0"
                elif m['adj_winner'] == "white":
                    # Dark wine background -> Bright Pink Text
                    win_str = f"W {m['black_score']}-{m['white_score']}"
                    win_color = "#FDA4AF"
                    time_color = "#E2E8F0"
                else:
                    win_str = f"D {m['black_score']}-{m['white_score']}"
                    win_color = "#FDE047"
                    time_color = "#E2E8F0"
                
                time_str = f"B:{b_str}\nW:{w_str}"
                ax_mat.text(j, i - 0.20, win_str, ha="center", va="center", color=win_color, fontsize=11.5, fontweight="heavy", zorder=4)
                ax_mat.text(j, i + 0.22, time_str, ha="center", va="center", color=time_color, fontsize=9.8, fontweight="bold", linespacing=1.1, zorder=4)

    out_path = os.path.join(REPORT_DIR, f"round_robin_limit_{limit_s:.1f}s.png")
    plt.savefig(out_path, dpi=200, facecolor=fig.get_facecolor(), edgecolor="none")
    plt.close()
    print(f"Generated: {out_path}")

def main():
    results, players = load_data()
    print(f"Loaded {len(results)} matches for {len(players)} players.")
    
    stats, matrix = compute_base_stats(results, players)
    
    # 1. Overall rankings
    generate_overall_rankings_png(results, players, stats)
    
    # 2. Timeout limit PNGs
    for limit in [1.8, 1.6, 1.4]:
        generate_timeout_limit_png(results, players, limit)

if __name__ == "__main__":
    main()
