import re

with open('players/experiments/exp_081_090/exp_082.py', 'r') as f:
    content = f.read()

# 1. Add _update_patterns_and_surrounds method
method_to_add = """
    def _update_patterns_and_surrounds(
        self,
        state: tuple[int, int],
        pattern_keys: tuple[int, ...],
        surrounds: tuple[int, int],
        pos: int,
        color: Cell,
        flips: int,
    ) -> tuple[tuple[int, ...], tuple[int, int]]:
        next_surrounds = MyPlayer._update_surround(state, surrounds, pos, color, flips)
        keys = list(pattern_keys)
        bits = flips
        if color == Cell.BLACK:
            MyPlayer.UPDATE_POS_BLACK_FUNCS_STATIC[pos](keys)
            while bits:
                bit = bits & -bits
                MyPlayer.UPDATE_FLIP_BLACK_FUNCS_STATIC[bit.bit_length() - 1](keys)
                bits ^= bit
        else:
            MyPlayer.UPDATE_POS_WHITE_FUNCS_STATIC[pos](keys)
            while bits:
                bit = bits & -bits
                MyPlayer.UPDATE_FLIP_WHITE_FUNCS_STATIC[bit.bit_length() - 1](keys)
                bits ^= bit
        return tuple(keys), next_surrounds

    def _apply_move_full("""

content = content.replace("    def _apply_move_full(", method_to_add)

# 2. Modify _order_moves and TT Best Move logic inside _negascout
repl_ordering = """        # 置換表（TT）から前回の最善手を抽出
        tt_entry = MyPlayer.SEARCH_HASH_TABLE[MyPlayer._search_hash_index(search_key)]
        tt_best_move = None
        if tt_entry is not None and tt_entry[0] == search_key:
            tt_best_move = tt_entry[4]

        moves = self._order_move_positions_by_weight(moves)
        children = []
        for move in moves:
            flips = self._flips_bits(state, move, current_color)
            move_bit = 1 << move
            black_bits, white_bits = state
            if current_color == Cell.BLACK:
                next_state = ((black_bits | flips | move_bit), (white_bits & ~flips))
            else:
                next_state = ((black_bits & ~flips), (white_bits | flips | move_bit))

            if move == tt_best_move:
                children.append([move, next_state, flips, None, None, 1000000.0])
                continue

            order_score = 0.0
            next_pattern_keys = None
            next_surrounds = None
            
            if depth >= 2 and len(moves) > 1:
                cached_eval = MyPlayer.EVAL_CACHE.get(next_state)
                if cached_eval is not None:
                    order_score = cached_eval if current_color == Cell.BLACK else -cached_eval
                else:
                    next_pattern_keys, next_surrounds = self._update_patterns_and_surrounds(
                        state, pattern_keys, surrounds, move, current_color, flips
                    )
                    order_score = self._evaluate_for_color_bits(next_state, current_color, next_pattern_keys, next_surrounds)

            children.append([move, next_state, flips, next_pattern_keys, next_surrounds, order_score])

        if depth >= 2 and len(children) > 1:
            children.sort(key=lambda child: child[5], reverse=True)"""

content = re.sub(
    r"        # 置換表（TT）から前回の最善手を抽出.*?if depth >= 2 and len\(children\) > 1:\n            children\.sort\(key=lambda child: child\[4\], reverse=True\)",
    repl_ordering,
    content,
    flags=re.DOTALL
)

# 3. Modify search loop to lazily compute patterns
repl_loop = """        search_window = beta
        best_score = float("-inf")
        best_child_move = children[0][0] if children else None

        for index, child in enumerate(children):
            move = child[0]
            next_state = child[1]
            flips = child[2]
            
            if child[3] is None:
                child[3], child[4] = self._update_patterns_and_surrounds(
                    state, pattern_keys, surrounds, move, current_color, flips
                )
            next_pattern_keys = child[3]
            next_surrounds = child[4]"""

content = re.sub(
    r"        search_window = beta\n        best_score = float\(\"-inf\"\)\n        best_child_move = children\[0\]\[0\] if children else None\n\n        for index, child in enumerate\(children\):\n            move = child\[0\]\n            next_state = child\[1\]\n            next_pattern_keys = child\[2\]\n            next_surrounds = child\[3\]",
    repl_loop,
    content,
    flags=re.DOTALL
)

with open('players/experiments/exp_081_090/exp_082.py', 'w') as f:
    f.write(content)

print("Rewrote exp_082.py to add Lazy ApplyMove and TT Move Fast-Path.")
