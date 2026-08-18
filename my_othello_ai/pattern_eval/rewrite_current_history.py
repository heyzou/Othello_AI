import re

with open('players/current.py', 'r') as f:
    content = f.read()

# 1. Update depths and cache size back to Depth 7
content = content.replace("SEARCH_DEPTH = 8", "SEARCH_DEPTH = 7")
content = content.replace("ENDGAME_EXACT_EMPTY = 12", "ENDGAME_EXACT_EMPTY = 13")
content = content.replace("LEGAL_MOVES_CACHE_MAX_SIZE = 131072", "LEGAL_MOVES_CACHE_MAX_SIZE = 65536")
content = content.replace("EVAL_CACHE_MAX_SIZE = 524288", "EVAL_CACHE_MAX_SIZE = 262144")
content = content.replace("SEARCH_HASH_TABLE_SIZE = 524288", "SEARCH_HASH_TABLE_SIZE = 131072")

# 2. Add initialization in next_move
repl_next_move = """    def next_move(self, board: Board) -> Move:
        self._killer_moves = [None] * 64
        self._history_table = [0.0] * 64
"""
content = re.sub(r"    def next_move\(self, board: Board\) -> Move:\n", repl_next_move, content)

# 3. Add History/Killer move ordering logic
repl_ordering = """        # 置換表（TT）から前回の最善手を抽出
        tt_entry = MyPlayer.SEARCH_HASH_TABLE[MyPlayer._search_hash_index(search_key)]
        tt_best_move = None
        if tt_entry is not None and tt_entry[0] == search_key:
            tt_best_move = tt_entry[4]

        killer_move = self._killer_moves[depth] if depth < 64 else None

        moves = self._order_move_positions_by_weight(moves)
        children = []
        for move in moves:
            child = self._apply_move_full(
                state, pattern_keys, surrounds, move, current_color
            )
            next_state, next_pattern_keys, next_surrounds = child
            
            order_score = 0.0
            if move == tt_best_move:
                order_score = 1000000.0
            elif move == killer_move:
                order_score = 500000.0
            else:
                pos = move  # Fallback just in case
                history_bonus = self._history_table[pos] if pos < 64 else 0.0
                
                if depth >= 2 and len(moves) > 1:
                    eval_score = self._evaluate_for_color_bits(next_state, current_color, next_pattern_keys, next_surrounds)
                    order_score = eval_score + history_bonus * 0.1
                else:
                    order_score = history_bonus

            children.append((move, next_state, next_pattern_keys, next_surrounds, order_score))

        if depth >= 2 and len(children) > 1:
            children.sort(key=lambda child: child[4], reverse=True)"""

content = re.sub(
    r"        # 置換表（TT）から前回の最善手を抽出.*?if depth >= 2 and len\(children\) > 1:\n            children\.sort\(key=lambda child: child\[4\], reverse=True\)",
    repl_ordering,
    content,
    flags=re.DOTALL
)

# 4. Remove LMR and add History/Killer update
repl_loop = """            if index == 0 or depth <= 1:
                score = -self._negascout(
                    next_state, next_pattern_keys, next_surrounds, depth - 1, next_color, -beta, -alpha, allow_probcut
                )
            else:
                score = -self._negascout(
                    next_state, next_pattern_keys, next_surrounds, depth - 1, next_color, -search_window, -alpha, allow_probcut
                )
                if alpha < score < beta:
                    score = -self._negascout(
                        next_state, next_pattern_keys, next_surrounds, depth - 1, next_color, -beta, -score, allow_probcut
                    )

            if score > best_score:
                best_score = score
                best_child_move = move

            alpha = max(alpha, score)
            if alpha >= beta:
                if move != tt_best_move and depth < 64:
                    self._killer_moves[depth] = move
                
                pos = move
                if pos < 64:
                    self._history_table[pos] += depth * depth
                break
            search_window = alpha + 1"""

content = re.sub(
    r"            # --- LMR \(Late Move Reductions\) ---.*?search_window = alpha \+ 1",
    repl_loop,
    content,
    flags=re.DOTALL
)

with open('players/current.py', 'w') as f:
    f.write(content)

print("Rewrote current.py to add History and Killer Moves, and remove LMR.")
