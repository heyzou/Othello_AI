import re

with open('players/experiments/exp_081_090/exp_081.py', 'r') as f:
    content = f.read()

# 1. Add initialization in next_move
repl_next_move = """    def next_move(self, board: Board) -> Move:
        self._killer_moves = [None] * 64
        self._history_table = [0.0] * 64
"""
content = re.sub(r"    def next_move\(self, board: Board\) -> Move:\n", repl_next_move, content)

# 2. Replace the move ordering logic in _negascout
repl_ordering = """        # 置換表（TT）から前回の最善手を抽出
        tt_entry = MyPlayer.SEARCH_HASH_TABLE[MyPlayer._search_hash_index(search_key)]
        tt_best_move = None
        if tt_entry is not None and tt_entry[0] == search_key:
            tt_best_move = tt_entry[4]

        killer_move = self._killer_moves[depth] if depth < 64 else None

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
                pos = self._move_to_pos(move)
                order_score = self._history_table[pos] + self.ORDER_WEIGHTS[pos // 8][pos % 8]

            children.append((move, next_state, next_pattern_keys, next_surrounds, order_score))

        children.sort(key=lambda child: child[4], reverse=True)"""
content = re.sub(
    r"        # 置換表（TT）から前回の最善手を抽出.*?if depth >= 2 and len\(children\) > 1:\n            children\.sort\(key=lambda child: child\[4\], reverse=True\)",
    repl_ordering,
    content,
    flags=re.DOTALL
)

# 3. Replace the LMR and NegaScout call in _negascout loop
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
                pos = self._move_to_pos(move)
                self._history_table[pos] += depth * depth
                break
            search_window = alpha + 1"""

content = re.sub(
    r"            # --- LMR \(Late Move Reductions\) ---.*?search_window = alpha \+ 1",
    repl_loop,
    content,
    flags=re.DOTALL
)

with open('players/experiments/exp_081_090/exp_081.py', 'w') as f:
    f.write(content)

print("Rewrote exp_081.py to add History and Killer Moves, remove LMR, and optimize Move Ordering.")
