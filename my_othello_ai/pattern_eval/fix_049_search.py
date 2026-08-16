import os

source = 'players/experiments/exp_041_050/exp_049_time_profile.py'

with open(source, 'r') as f:
    code = f.read()

# 1. Add class variables for search breakdown
new_class_vars = '''    _accum_search_movegen_time = 0.0
    _accum_search_applymove_time = 0.0
    _accum_search_moveorder_time = 0.0
    _accum_search_tthash_time = 0.0\n'''

code = code.replace('    _accum_eval_add_mlp_time = 0.0\n', '    _accum_eval_add_mlp_time = 0.0\n' + new_class_vars, 1)

# 2. Reset them in next_move
new_resets = '''        MyPlayer._accum_search_movegen_time = 0.0
        MyPlayer._accum_search_applymove_time = 0.0
        MyPlayer._accum_search_moveorder_time = 0.0
        MyPlayer._accum_search_tthash_time = 0.0\n'''

code = code.replace('        MyPlayer._accum_eval_add_mlp_time = 0.0\n', '        MyPlayer._accum_eval_add_mlp_time = 0.0\n' + new_resets)

# 3. Add to _log_profile
old_log = '''        if not is_book:
            pat_ms = MyPlayer._accum_eval_pattern_time * 1000'''

new_log = '''        if not is_book:
            mgen_ms = MyPlayer._accum_search_movegen_time * 1000
            app_ms = MyPlayer._accum_search_applymove_time * 1000
            mord_ms = MyPlayer._accum_search_moveorder_time * 1000
            tt_ms = MyPlayer._accum_search_tthash_time * 1000
            ctrl_ms = max(0, other_search_ms - (mgen_ms + app_ms + mord_ms + tt_ms))
            
            mgen_pct = (mgen_ms / other_search_ms) * 100 if other_search_ms > 0 else 0
            app_pct = (app_ms / other_search_ms) * 100 if other_search_ms > 0 else 0
            mord_pct = (mord_ms / other_search_ms) * 100 if other_search_ms > 0 else 0
            tt_pct = (tt_ms / other_search_ms) * 100 if other_search_ms > 0 else 0
            ctrl_pct = (ctrl_ms / other_search_ms) * 100 if other_search_ms > 0 else 0
            
            print(f"         ├─ [Search Breakdown] MoveGen: {mgen_ms:7.2f} ms ({mgen_pct:4.1f}%) | ApplyMove: {app_ms:7.2f} ms ({app_pct:4.1f}%) | MoveOrder: {mord_ms:7.2f} ms ({mord_pct:4.1f}%) | TTHash: {tt_ms:7.2f} ms ({tt_pct:4.1f}%) | Control: {ctrl_ms:7.2f} ms ({ctrl_pct:4.1f}%)")
            
            pat_ms = MyPlayer._accum_eval_pattern_time * 1000'''

code = code.replace(old_log, new_log)

# Also update the print format to match the tree view: └─ for eval breakdown
code = code.replace('         └─ [Eval Breakdown]', '         └─ [Eval Breakdown]') # It's already doing this

# 4. Inject tracking in the actual methods

# MoveGen
old_movegen = '''    def _legal_moves_bits(self, state: tuple[int, int], color: int) -> tuple[int, ...]:
        cached = MyPlayer.LEGAL_MOVES_CACHE.get((state, color))
        if cached is not None:
            return cached'''
new_movegen = '''    def _legal_moves_bits(self, state: tuple[int, int], color: int) -> tuple[int, ...]:
        t0 = time.perf_counter()
        cached = MyPlayer.LEGAL_MOVES_CACHE.get((state, color))
        if cached is not None:
            MyPlayer._accum_search_movegen_time += time.perf_counter() - t0
            return cached'''
code = code.replace(old_movegen, new_movegen)

old_movegen_end = '''        MyPlayer.LEGAL_MOVES_CACHE[(state, color)] = moves
        return moves'''
new_movegen_end = '''        MyPlayer.LEGAL_MOVES_CACHE[(state, color)] = moves
        MyPlayer._accum_search_movegen_time += time.perf_counter() - t0
        return moves'''
code = code.replace(old_movegen_end, new_movegen_end)

# ApplyMove
old_apply = '''    def _apply_move_with_pattern_keys(
        self,
        state: tuple[int, int],
        pattern_keys: tuple[int, ...],
        move: int,
        color: int,
    ) -> tuple[tuple[int, int], tuple[int, ...]]:
        flips = self._flips_bits(state, move, color)'''
new_apply = '''    def _apply_move_with_pattern_keys(
        self,
        state: tuple[int, int],
        pattern_keys: tuple[int, ...],
        move: int,
        color: int,
    ) -> tuple[tuple[int, int], tuple[int, ...]]:
        t0 = time.perf_counter()
        flips = self._flips_bits(state, move, color)'''
code = code.replace(old_apply, new_apply)

old_apply_end = '''        return new_state, tuple(new_keys)'''
new_apply_end = '''        MyPlayer._accum_search_applymove_time += time.perf_counter() - t0
        return new_state, tuple(new_keys)'''
code = code.replace(old_apply_end, new_apply_end)

# MoveOrder
old_order = '''    def _order_move_positions_by_weight(self, moves: tuple[int, ...]) -> tuple[int, ...]:
        return tuple(sorted(moves, key=self._order_weight, reverse=True))'''
new_order = '''    def _order_move_positions_by_weight(self, moves: tuple[int, ...]) -> tuple[int, ...]:
        t0 = time.perf_counter()
        res = tuple(sorted(moves, key=self._order_weight, reverse=True))
        MyPlayer._accum_search_moveorder_time += time.perf_counter() - t0
        return res'''
code = code.replace(old_order, new_order)

# TT Hash (negascout start)
old_tt_get = '''    def _negascout(
        self,
        state: tuple[int, int],
        pattern_keys: tuple[int, ...],
        depth: int,
        current_color: int,
        alpha: float,
        beta: float,
    ) -> float:
        hash_index = state[0] & MyPlayer.SEARCH_HASH_MASK
        entry = MyPlayer.SEARCH_HASH_TABLE[hash_index]
        if entry is not None and entry[0] == state and entry[1] >= depth:
            if entry[2] == 0:
                return entry[3]
            elif entry[2] == 1 and entry[3] <= alpha:
                return entry[3]
            elif entry[2] == 2 and entry[3] >= beta:
                return entry[3]'''
new_tt_get = '''    def _negascout(
        self,
        state: tuple[int, int],
        pattern_keys: tuple[int, ...],
        depth: int,
        current_color: int,
        alpha: float,
        beta: float,
    ) -> float:
        t0_tt = time.perf_counter()
        hash_index = state[0] & MyPlayer.SEARCH_HASH_MASK
        entry = MyPlayer.SEARCH_HASH_TABLE[hash_index]
        if entry is not None and entry[0] == state and entry[1] >= depth:
            if entry[2] == 0:
                MyPlayer._accum_search_tthash_time += time.perf_counter() - t0_tt
                return entry[3]
            elif entry[2] == 1 and entry[3] <= alpha:
                MyPlayer._accum_search_tthash_time += time.perf_counter() - t0_tt
                return entry[3]
            elif entry[2] == 2 and entry[3] >= beta:
                MyPlayer._accum_search_tthash_time += time.perf_counter() - t0_tt
                return entry[3]
        MyPlayer._accum_search_tthash_time += time.perf_counter() - t0_tt'''
code = code.replace(old_tt_get, new_tt_get)

# TT Hash (negascout end)
old_tt_set = '''        flag = 0
        if best_score <= original_alpha:
            flag = 1
        elif best_score >= beta:
            flag = 2
        MyPlayer.SEARCH_HASH_TABLE[hash_index] = (state, depth, flag, best_score)
        return best_score'''
new_tt_set = '''        t0_tt2 = time.perf_counter()
        flag = 0
        if best_score <= original_alpha:
            flag = 1
        elif best_score >= beta:
            flag = 2
        MyPlayer.SEARCH_HASH_TABLE[hash_index] = (state, depth, flag, best_score)
        MyPlayer._accum_search_tthash_time += time.perf_counter() - t0_tt2
        return best_score'''
code = code.replace(old_tt_set, new_tt_set)

with open(source, 'w') as f:
    f.write(code)

print('SUCCESS')
