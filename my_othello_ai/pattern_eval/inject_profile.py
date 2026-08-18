import re

with open('players/experiments/exp_071_080/exp_079.py', 'r') as f:
    content = f.read()

# 1. Add accumulators to class level
accums = """    _accum_eval_time = 0.0
    _accum_eval_hit_time = 0.0
    _accum_eval_pattern_time = 0.0
    _accum_eval_mobility_time = 0.0
    _accum_eval_surround_time = 0.0
    _accum_eval_add_mlp_time = 0.0
    _accum_search_movegen_time = 0.0
    _accum_search_applymove_time = 0.0
    _accum_search_moveorder_time = 0.0
    _accum_search_tthash_time = 0.0

"""
content = content.replace("    PATTERN_CACHE = {}", accums + "    PATTERN_CACHE = {}")

# 2. Inject _log_profile method
log_profile_method = """    def _log_profile(self, total_time: float, is_book: bool, actual_turn: int) -> None:
        import time
        total_ms = total_time * 1000
        book_ms = getattr(self, '_t_book', 0.0) * 1000
        search_ms = getattr(self, '_t_search', 0.0) * 1000
        eval_ms = MyPlayer._accum_eval_time * 1000
        other_search_ms = max(0, search_ms - eval_ms)
        
        book_pct = (book_ms / total_ms) * 100 if total_ms > 0 else 0
        eval_pct = (eval_ms / total_ms) * 100 if total_ms > 0 else 0
        other_pct = (other_search_ms / total_ms) * 100 if total_ms > 0 else 0
        
        prefix = "[BOOK]  " if is_book else "[SEARCH]"
        
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

        print(f"Turn {actual_turn:2d} | My Move Time: {total_time:.3f} s")
        
        with open("076_profile.txt", "a", encoding="utf-8") as f:
            f.write(f"{prefix} Turn {actual_turn:2d} | Total: {total_ms:7.2f} ms | Book: {book_ms:6.2f} ms ({book_pct:5.1f}%) | Eval: {eval_ms:7.2f} ms ({eval_pct:5.1f}%) | Search(Other): {other_search_ms:7.2f} ms ({other_pct:5.1f}%)\\n")
            if not is_book:
                f.write(f"         ├─ [Search Breakdown] MoveGen: {mgen_ms:7.2f} ms ({mgen_pct:4.1f}%) | ApplyMove: {app_ms:7.2f} ms ({app_pct:4.1f}%) | MoveOrder: {mord_ms:7.2f} ms ({mord_pct:4.1f}%) | TTHash: {tt_ms:7.2f} ms ({tt_pct:4.1f}%) | Control: {ctrl_ms:7.2f} ms ({ctrl_pct:4.1f}%)\\n")
                f.write(f"         ├─ [Eval Breakdown]   Patterns: {pat_ms:7.2f} ms ({pat_pct:4.1f}%) | Mobility: {mob_ms:7.2f} ms ({mob_pct:4.1f}%) | Surround: {sur_ms:7.2f} ms ({sur_pct:4.1f}%) | AddMLP: {add_ms:7.2f} ms ({add_pct:4.1f}%) | CacheHit: {hit_ms:7.2f} ms ({hit_pct:4.1f}%)\\n")

    def next_move(self, board: Board) -> Move:
        import time
        t_start_all = time.perf_counter()
        
        MyPlayer._accum_eval_time = 0.0
        MyPlayer._accum_eval_hit_time = 0.0
        MyPlayer._accum_eval_pattern_time = 0.0
        MyPlayer._accum_eval_mobility_time = 0.0
        MyPlayer._accum_eval_surround_time = 0.0
        MyPlayer._accum_eval_add_mlp_time = 0.0
        MyPlayer._accum_search_movegen_time = 0.0
        MyPlayer._accum_search_applymove_time = 0.0
        MyPlayer._accum_search_moveorder_time = 0.0
        MyPlayer._accum_search_tthash_time = 0.0
        self._t_book = 0.0
        self._t_search = 0.0
"""
content = re.sub(r"    def next_move\(self, board: Board\) -> Move:", log_profile_method, content)

content = content.replace("        return book_move", "        self._t_book = time.perf_counter() - t_start_all\n        self._log_profile(time.perf_counter() - t_start_all, True, actual_turn)\n        return book_move")

end_next_move = """            if time_passed > self.TIME_LIMIT:
                break
        self._t_search = time.perf_counter() - t_start_all
        self._log_profile(time.perf_counter() - t_start_all, False, actual_turn)
        return self._pos_to_move(best_move)"""
content = re.sub(r"            if time_passed > self\.TIME_LIMIT:\n                break\n        return self\._pos_to_move\(best_move\)", end_next_move, content)

# 3. Inject eval times
eval_color = """    def _evaluate_for_color_bits(
        self,
        state: tuple[int, int],
        color: Cell,
        pattern_keys: tuple[int, ...] | None = None,
        surrounds: tuple[int, int] | None = None,
    ) -> float:
        import time
        t0 = time.perf_counter()
        if color == Cell.BLACK:
            res = self._evaluate_black_perspective_bits(state, pattern_keys, surrounds, is_white=False)
        else:
            res = self._evaluate_black_perspective_bits(state, pattern_keys, surrounds, is_white=True)
        MyPlayer._accum_eval_time += time.perf_counter() - t0
        return res"""
content = re.sub(r"    def _evaluate_for_color_bits\(.*?return self\._evaluate_black_perspective_bits\(state, pattern_keys, surrounds, is_white=True\)", eval_color, content, flags=re.DOTALL)

with open('players/experiments/exp_071_080/exp_079.py', 'w') as f:
    f.write(content)

print("Profile hooks injected.")
