import os, re

source = 'players/experiments/exp_041_050/exp_048_retrained_weights.py'
dest = 'players/experiments/exp_041_050/exp_049_time_profile.py'

with open(source, 'r') as f:
    code = f.read()

# Add import time at the top
if 'import time' not in code:
    code = 'import time\n' + code

# Split the code into 3 parts:
# 1. Before the SECOND next_move
# 2. The second next_move signature and body
parts = code.split('    def next_move(self, board: Board) -> Move:\n')
if len(parts) < 3:
    print("ERROR: Could not find two next_move definitions.")
    exit(1)

# The part before the second next_move
part1 = parts[0] + '    def next_move(self, board: Board) -> Move:\n' + parts[1]

# The body of the second next_move and the rest of the file
part2 = parts[2]

# 1. Inject class variables and _log_profile right before the SECOND next_move
class_vars = '''
    _accum_eval_time = 0.0
    _accum_eval_hit_time = 0.0
    _accum_eval_pattern_time = 0.0
    _accum_eval_mobility_time = 0.0
    _accum_eval_surround_time = 0.0
    _accum_eval_add_mlp_time = 0.0

    def _log_profile(self, total_time: float, is_book: bool, actual_turn: int) -> None:
        total_ms = total_time * 1000
        book_ms = self._t_book * 1000
        search_ms = self._t_search * 1000
        eval_ms = MyPlayer._accum_eval_time * 1000
        other_search_ms = search_ms - eval_ms
        
        book_pct = (book_ms / total_ms) * 100 if total_ms > 0 else 0
        eval_pct = (eval_ms / total_ms) * 100 if total_ms > 0 else 0
        other_pct = (other_search_ms / total_ms) * 100 if total_ms > 0 else 0
        
        prefix = "[BOOK]  " if is_book else "[SEARCH]"
        print(f"{prefix} Turn {actual_turn:2d} | Total: {total_ms:7.2f} ms | Book: {book_ms:6.2f} ms ({book_pct:5.1f}%) | Eval: {eval_ms:7.2f} ms ({eval_pct:5.1f}%) | Search(Other): {other_search_ms:7.2f} ms ({other_pct:5.1f}%)")
        
        if not is_book:
            pat_ms = MyPlayer._accum_eval_pattern_time * 1000
            mob_ms = MyPlayer._accum_eval_mobility_time * 1000
            sur_ms = MyPlayer._accum_eval_surround_time * 1000
            add_ms = MyPlayer._accum_eval_add_mlp_time * 1000
            hit_ms = MyPlayer._accum_eval_hit_time * 1000
            
            pat_pct = (pat_ms / eval_ms) * 100 if eval_ms > 0 else 0
            mob_pct = (mob_ms / eval_ms) * 100 if eval_ms > 0 else 0
            sur_pct = (sur_ms / eval_ms) * 100 if eval_ms > 0 else 0
            add_pct = (add_ms / eval_ms) * 100 if eval_ms > 0 else 0
            hit_pct = (hit_ms / eval_ms) * 100 if eval_ms > 0 else 0
            
            print(f"         └─ [Eval Breakdown] Patterns: {pat_ms:7.2f} ms ({pat_pct:4.1f}%) | Mobility: {mob_ms:7.2f} ms ({mob_pct:4.1f}%) | Surround: {sur_ms:7.2f} ms ({sur_pct:4.1f}%) | AddMLP: {add_ms:7.2f} ms ({add_pct:4.1f}%) | CacheHit: {hit_ms:7.2f} ms ({hit_pct:4.1f}%)")

'''
part1 += class_vars + '    def next_move(self, board: Board) -> Move:\n'

# 2. Inject start_total into the SECOND next_move
new_start = '''        start_total = time.perf_counter()
        MyPlayer._accum_eval_time = 0.0
        MyPlayer._accum_eval_hit_time = 0.0
        MyPlayer._accum_eval_pattern_time = 0.0
        MyPlayer._accum_eval_mobility_time = 0.0
        MyPlayer._accum_eval_surround_time = 0.0
        MyPlayer._accum_eval_add_mlp_time = 0.0\n'''
part2 = new_start + part2

# 3. Modify book move block
old_book = '''        book_move = self._book_move_bits(state)

        if book_move is not None and self._move_to_pos(book_move) in moves:
            return book_move'''
new_book = '''        t0_book = time.perf_counter()
        book_move = self._book_move_bits(state)
        self._t_book = time.perf_counter() - t0_book

        if book_move is not None and self._move_to_pos(book_move) in moves:
            total_time = time.perf_counter() - start_total
            self._log_profile(total_time, is_book=True, actual_turn=actual_turn)
            return book_move

        t0_search = time.perf_counter()'''
part2 = part2.replace(old_book, new_book)

# 4. Modify exact search return
old_exact_ret = '''                alpha = max(alpha, best_score)

            return self._pos_to_move(best_move)'''
new_exact_ret = '''                alpha = max(alpha, best_score)

            self._t_search = time.perf_counter() - t0_search
            total_time = time.perf_counter() - start_total
            self._log_profile(total_time, is_book=False, actual_turn=actual_turn)
            return self._pos_to_move(best_move)'''
part2 = part2.replace(old_exact_ret, new_exact_ret)

# 5. Modify regular search return
old_reg_ret = '''            best_score = iter_best_score

        return self._pos_to_move(best_move)'''
new_reg_ret = '''            best_score = iter_best_score

        self._t_search = time.perf_counter() - t0_search
        total_time = time.perf_counter() - start_total
        self._log_profile(total_time, is_book=False, actual_turn=actual_turn)
        return self._pos_to_move(best_move)'''
part2 = part2.replace(old_reg_ret, new_reg_ret)

# Now combine the parts
code = part1 + part2

# 6. Replace eval for profiling (this is outside next_move, so global replace)
old_eval = '''    def _evaluate_black_perspective_bits(
        self,
        state: tuple[int, int],
        pattern_keys: tuple[int, ...] | None = None,
    ) -> float:
        cached = MyPlayer.EVAL_CACHE.get(state)
        if cached is not None:
            return cached'''
new_eval = '''    def _evaluate_black_perspective_bits(
        self,
        state: tuple[int, int],
        pattern_keys: tuple[int, ...] | None = None,
    ) -> float:
        t_eval_start = time.perf_counter()
        cached = MyPlayer.EVAL_CACHE.get(state)
        if cached is not None:
            MyPlayer._accum_eval_hit_time += time.perf_counter() - t_eval_start
            MyPlayer._accum_eval_time += time.perf_counter() - t_eval_start
            return cached'''
code = code.replace(old_eval, new_eval)

old_eval2 = '''        if pattern_keys is None:
            pattern_keys = self._pattern_keys_from_state(state)

        final_dense, final_bias = self._params()[2]
        pattern_name_to_final_index = MyPlayer._pattern_name_to_final_index()
        group_infos = MyPlayer._pattern_key_group_infos()
        result = final_bias
        for name, start, end in group_infos:
            group_sum = 0.0
            pattern_table = MyPlayer.PATTERN_VALUE_TABLES.get(name)
            for index in range(start, end):
                key = pattern_keys[index]
                if pattern_table is None:
                    group_sum += MyPlayer._compute_pattern_value(name, key)
                else:
                    group_sum += pattern_table[key]
            result += group_sum * final_dense[pattern_name_to_final_index[name]]'''
new_eval2 = '''        if pattern_keys is None:
            pattern_keys = self._pattern_keys_from_state(state)

        t_pat_start = time.perf_counter()
        final_dense, final_bias = self._params()[2]
        pattern_name_to_final_index = MyPlayer._pattern_name_to_final_index()
        group_infos = MyPlayer._pattern_key_group_infos()
        result = final_bias
        for name, start, end in group_infos:
            group_sum = 0.0
            pattern_table = MyPlayer.PATTERN_VALUE_TABLES.get(name)
            for index in range(start, end):
                key = pattern_keys[index]
                if pattern_table is None:
                    group_sum += MyPlayer._compute_pattern_value(name, key)
                else:
                    group_sum += pattern_table[key]
            result += group_sum * final_dense[pattern_name_to_final_index[name]]
        MyPlayer._accum_eval_pattern_time += time.perf_counter() - t_pat_start'''
code = code.replace(old_eval2, new_eval2)

old_eval3 = '''        add_key = self._additional_key_bits(state)
        add_value = self._add_value(add_key)
        result += add_value * final_dense[len(self.PATTERN_SIZES)]

        cache = MyPlayer.EVAL_CACHE
        if len(cache) >= self.EVAL_CACHE_MAX_SIZE:
            cache.clear()
        cache[state] = result
        return result'''
new_eval3 = '''        t_add_start = time.perf_counter()
        add_key = self._additional_key_bits(state)
        add_value = self._add_value(add_key)
        result += add_value * final_dense[len(self.PATTERN_SIZES)]
        MyPlayer._accum_eval_add_mlp_time += time.perf_counter() - t_add_start

        cache = MyPlayer.EVAL_CACHE
        if len(cache) >= self.EVAL_CACHE_MAX_SIZE:
            cache.clear()
        cache[state] = result
        MyPlayer._accum_eval_time += time.perf_counter() - t_eval_start
        return result'''
code = code.replace(old_eval3, new_eval3)

# Additional Key tracking
old_add = '''    def _additional_key_bits(self, state: tuple[int, int]) -> int:
        cached = MyPlayer.ADDITIONAL_KEY_CACHE.get(state)
        if cached is not None:
            return cached

        mobility = self._mobility_diff_bits(state)

        surround_black, surround_white = self._surround_counts_bits(state)'''
new_add = '''    def _additional_key_bits(self, state: tuple[int, int]) -> int:
        cached = MyPlayer.ADDITIONAL_KEY_CACHE.get(state)
        if cached is not None:
            return cached

        t0 = time.perf_counter()
        mobility = self._mobility_diff_bits(state)
        MyPlayer._accum_eval_mobility_time += time.perf_counter() - t0

        t1 = time.perf_counter()
        surround_black, surround_white = self._surround_counts_bits(state)
        MyPlayer._accum_eval_surround_time += time.perf_counter() - t1'''
code = code.replace(old_add, new_add)

with open(dest, 'w') as f:
    f.write(code)

print('SUCCESS')
