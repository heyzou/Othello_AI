import sys

with open('my_othello_ai/pattern_eval/players/current.py', 'r') as f:
    lines = f.readlines()

new_lines = []
for i, line in enumerate(lines):
    if "PATTERN_KEY_META = None" in line:
        new_lines.append(line)
        new_lines.append("""
    _accum_eval_time = 0.0
    _accum_eval_hit_time = 0.0
    _accum_eval_pattern_time = 0.0
    _accum_eval_mobility_time = 0.0
    _accum_eval_surround_time = 0.0
    _accum_eval_add_mlp_time = 0.0
    _accum_search_movegen_time = 0.0
    _accum_search_applymove_time = 0.0
    _accum_search_moveorder_time = 0.0
    _accum_search_tthash_time = 0.0
    
    _nodes_evaluated = 0
    _nodes_visited = 0
    _tthash_hits = 0
    _tthash_gets = 0
    _eval_cache_hits = 0
    _eval_cache_gets = 0
    _legal_moves_cache_hits = 0
    _legal_moves_cache_gets = 0
    _legal_move_mask_cache_hits = 0
    _legal_move_mask_cache_gets = 0
    _combined_legal_cache_hits = 0
    _combined_legal_cache_gets = 0
""")
        continue

    if "def next_move(self, board: Board) -> Move:" in line and "    def" in line:
        new_lines.append("""
    def _log_profile(self, total_time: float, is_book: bool, actual_turn: int) -> None:
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

        # Termial print
        print(f"Turn {actual_turn:2d} | My Move Time: {total_time:.3f} s")
        
        # File print
        with open("exp_072_profile.txt", "a", encoding="utf-8") as f:
            f.write(f"{prefix} Turn {actual_turn:2d} | Total: {total_ms:7.2f} ms | Book: {book_ms:6.2f} ms ({book_pct:5.1f}%) | Eval: {eval_ms:7.2f} ms ({eval_pct:5.1f}%) | Search(Other): {other_search_ms:7.2f} ms ({other_pct:5.1f}%)\\n")
            if not is_book:
                f.write(f"         ├─ [Search Breakdown] MoveGen: {mgen_ms:7.2f} ms ({mgen_pct:4.1f}%) | ApplyMove: {app_ms:7.2f} ms ({app_pct:4.1f}%) | MoveOrder: {mord_ms:7.2f} ms ({mord_pct:4.1f}%) | TTHash: {tt_ms:7.2f} ms ({tt_pct:4.1f}%) | Control: {ctrl_ms:7.2f} ms ({ctrl_pct:4.1f}%)\\n")
                f.write(f"         ├─ [Eval Breakdown]   Patterns: {pat_ms:7.2f} ms ({pat_pct:4.1f}%) | Mobility: {mob_ms:7.2f} ms ({mob_pct:4.1f}%) | Surround: {sur_ms:7.2f} ms ({sur_pct:4.1f}%) | AddMLP: {add_ms:7.2f} ms ({add_pct:4.1f}%) | CacheHit: {hit_ms:7.2f} ms ({hit_pct:4.1f}%)\\n")
                
                eval_hit_rate = (MyPlayer._eval_cache_hits / MyPlayer._eval_cache_gets * 100) if MyPlayer._eval_cache_gets > 0 else 0
                tt_hit_rate = (MyPlayer._tthash_hits / MyPlayer._tthash_gets * 100) if MyPlayer._tthash_gets > 0 else 0
                lmoves_hit_rate = (MyPlayer._legal_moves_cache_hits / MyPlayer._legal_moves_cache_gets * 100) if MyPlayer._legal_moves_cache_gets > 0 else 0
                comb_hit_rate = (MyPlayer._combined_legal_cache_hits / MyPlayer._combined_legal_cache_gets * 100) if MyPlayer._combined_legal_cache_gets > 0 else 0
                
                f.write(f"         ├─ [Nodes] Visited: {MyPlayer._nodes_visited} | Evaluated: {MyPlayer._nodes_evaluated}\\n")
                f.write(f"         └─ [Cache] EVAL: {len(MyPlayer.EVAL_CACHE)} ({eval_hit_rate:.1f}%) | TTHash: {MyPlayer.SEARCH_HASH_REG_COUNT} regs ({tt_hit_rate:.1f}%) | LMove: {len(MyPlayer.LEGAL_MOVES_CACHE)} ({lmoves_hit_rate:.1f}%) | CombL: {len(MyPlayer.COMBINED_LEGAL_CACHE)} ({comb_hit_rate:.1f}%)\\n")

        # Reset counters
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

        MyPlayer._nodes_visited = 0
        MyPlayer._nodes_evaluated = 0
        MyPlayer._tthash_hits = 0
        MyPlayer._tthash_gets = 0
        MyPlayer._eval_cache_hits = 0
        MyPlayer._eval_cache_gets = 0
        MyPlayer._legal_moves_cache_hits = 0
        MyPlayer._legal_moves_cache_gets = 0
        MyPlayer._legal_move_mask_cache_hits = 0
        MyPlayer._legal_move_mask_cache_gets = 0
        MyPlayer._combined_legal_cache_hits = 0
        MyPlayer._combined_legal_cache_gets = 0
""")
        new_lines.append(line)
        new_lines.append("        import time\n")
        new_lines.append("        start_total = time.perf_counter()\n")
        continue
        
    if "return book_move" in line and "            return book_move" == line.rstrip("\n"):
        new_lines.append("            self._t_book = time.perf_counter() - start_total\n")
        new_lines.append("            total_time = time.perf_counter() - start_total\n")
        new_lines.append("            self._log_profile(total_time, True, actual_turn)\n")
        new_lines.append(line)
        continue

    # Line 806 return
    if "return self._pos_to_move(best_move)" in line and "            return" in line:
        new_lines.append("            self._t_search = time.perf_counter() - start_total\n")
        new_lines.append("            total_time = time.perf_counter() - start_total\n")
        new_lines.append("            self._log_profile(total_time, False, actual_turn)\n")
        new_lines.append(line)
        continue

    # Line 842 return
    if "return self._pos_to_move(best_move)" in line and "        return" in line:
        new_lines.append("        self._t_search = time.perf_counter() - start_total\n")
        new_lines.append("        total_time = time.perf_counter() - start_total\n")
        new_lines.append("        self._log_profile(total_time, False, actual_turn)\n")
        new_lines.append(line)
        continue

    # _negascout nodes visited
    if "        if depth == 0:" in line and "        # " in lines[i-1]:
        new_lines.append("        MyPlayer._nodes_visited += 1\n")
        new_lines.append(line)
        continue

    # _search_hash_get
    if "def _search_hash_get(cls, key: int, depth: int, alpha: float, beta: float) -> tuple[int, float, float] | None:" in line:
        new_lines.append(line)
        new_lines.append("        import time\n        t0 = time.perf_counter()\n        cls._tthash_gets += 1\n")
        continue

    if "cls.SEARCH_HASH_GET_COUNT += 1" in line:
        new_lines.append(line)
        continue
        
    # We must patch the return of _search_hash_get to capture hit and time.
    if "return entry" in line and "        if entry is not None" in lines[i-1]:
        new_lines.append("            cls._tthash_hits += 1\n")
        new_lines.append("            cls._accum_search_tthash_time += time.perf_counter() - t0\n")
        new_lines.append(line)
        continue
    if "return None" in line and "    def _search_hash_get" in lines[i-6]:
        new_lines.append("        cls._accum_search_tthash_time += time.perf_counter() - t0\n")
        new_lines.append(line)
        continue

    # _evaluate_black_perspective_bits time start
    if "def _evaluate_black_perspective_bits(" in line:
        new_lines.append(line)
        continue
    if "cached = MyPlayer.EVAL_CACHE.get(state)" in line:
        new_lines.append("        import time\n        t0 = time.perf_counter()\n        MyPlayer._nodes_evaluated += 1\n        MyPlayer._eval_cache_gets += 1\n")
        new_lines.append(line)
        continue
    if "            return cached" in line and "        if cached is not None:" in lines[i-2]:
        new_lines.append("            MyPlayer._eval_cache_hits += 1\n")
        new_lines.append("            dt = time.perf_counter() - t0\n")
        new_lines.append("            MyPlayer._accum_eval_time += dt\n")
        new_lines.append("            MyPlayer._accum_eval_hit_time += dt\n")
        new_lines.append(line)
        continue
    
    # Eval pattern start
    if "        if MyPlayer._ensure_evaluate_patterns_tables():" in line:
        new_lines.append("        t_pat = time.perf_counter()\n")
        new_lines.append(line)
        continue
    if "add_key = self._additional_key_bits(state, surrounds)" in line:
        new_lines.append("        MyPlayer._accum_eval_pattern_time += time.perf_counter() - t_pat\n")
        new_lines.append(line)
        continue
    if "cache[state] = result" in line:
        new_lines.append(line)
        new_lines.append("        MyPlayer._accum_eval_time += time.perf_counter() - t0\n")
        continue

    # _add_value
    if "def _add_value(cls, key: int) -> float:" in line:
        new_lines.append(line)
        new_lines.append("        import time\n        t0 = time.perf_counter()\n")
        continue
    if "res = cls._compute_add_value(key)" in line and "def _add_value" in lines[i-2]:
        new_lines.append(line)
        new_lines.append("        cls._accum_eval_add_mlp_time += time.perf_counter() - t0\n")
        continue

    # _additional_key_bits
    if "def _additional_key_bits(" in line:
        new_lines.append(line)
        new_lines.append("        import time\n")
        continue
    if "mobility = self._mobility_diff_bits(state)" in line:
        new_lines.append("        t_mob = time.perf_counter()\n")
        new_lines.append(line)
        new_lines.append("        MyPlayer._accum_eval_mobility_time += time.perf_counter() - t_mob\n")
        new_lines.append("        t_sur = time.perf_counter()\n")
        continue
    if "result = ((mobility + 30) * 51 + surround_black) * 51 + surround_white" in line:
        new_lines.append("        MyPlayer._accum_eval_surround_time += time.perf_counter() - t_sur\n")
        new_lines.append(line)
        continue

    # _combined_legal_cache
    if "cached = MyPlayer.COMBINED_LEGAL_CACHE.get(state)" in line:
        new_lines.append("        MyPlayer._combined_legal_cache_gets += 1\n")
        new_lines.append(line)
        continue
    if "            return cached" in line and "        if cached is not None:" in lines[i-1] and "COMBINED_LEGAL_CACHE" in lines[i-2]:
        new_lines.append("            MyPlayer._combined_legal_cache_hits += 1\n")
        new_lines.append(line)
        continue

    # MoveGen: _legal_moves_bits
    if "def _legal_moves_bits(" in line:
        new_lines.append(line)
        new_lines.append("        import time\n        t0 = time.perf_counter()\n        res = self._legal_moves_bits_inner(state, color)\n        MyPlayer._accum_search_movegen_time += time.perf_counter() - t0\n        return res\n\n    def _legal_moves_bits_inner(self, state: tuple[int, int], color: Cell) -> tuple[int, ...]:\n")
        continue
    if "key = self._legal_moves_cache_key_bits(state, color)" in line and "def _legal_moves_bits" in lines[i-2]:
        new_lines.append("        MyPlayer._legal_moves_cache_gets += 1\n")
        new_lines.append(line)
        continue
    if "            return cached" in line and "        if cached is not None:" in lines[i-1] and "LEGAL_MOVES_CACHE.get" in lines[i-2]:
        new_lines.append("            MyPlayer._legal_moves_cache_hits += 1\n")
        new_lines.append(line)
        continue

    # ApplyMove
    if "def _apply_move_full(" in line:
        new_lines.append(line)
        new_lines.append("        import time\n        t0 = time.perf_counter()\n        res = self._apply_move_full_inner(state, pattern_keys, surrounds, pos, color)\n        MyPlayer._accum_search_applymove_time += time.perf_counter() - t0\n        return res\n\n    def _apply_move_full_inner(\n        self,\n        state: tuple[int, int],\n        pattern_keys: tuple[int, ...] | None,\n        surrounds: tuple[int, int] | None,\n        pos: int,\n        color: Cell,\n    ) -> tuple[tuple[int, int], tuple[int, ...] | None, tuple[int, int] | None]:\n")
        continue

    # MoveOrder
    if "def _order_move_positions_by_weight(" in line:
        new_lines.append(line)
        new_lines.append("        import time\n        t0 = time.perf_counter()\n        res = self._order_move_positions_by_weight_inner(moves)\n        MyPlayer._accum_search_moveorder_time += time.perf_counter() - t0\n        return res\n\n    def _order_move_positions_by_weight_inner(self, moves: tuple[int, ...] | list[int]) -> list[int]:\n")
        continue

    new_lines.append(line)


with open('my_othello_ai/pattern_eval/players/experiments/exp_071_080/exp_072.py', 'w') as f:
    f.writelines(new_lines)
