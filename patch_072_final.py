import re

with open('my_othello_ai/pattern_eval/players/experiments/exp_071_080/exp_072.py', 'r') as f:
    code = f.read()

# Variables
class_vars = """
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
"""
code = code.replace("    PATTERN_KEY_META = None\n", "    PATTERN_KEY_META = None\n" + class_vars)

# next_move hook
log_profile = """
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
        
    def next_move(self, board: Board) -> Move:
        import time
        start_total = time.perf_counter()
"""
code = code.replace("    def next_move(self, board: Board) -> Move:\n", log_profile)

# Book return
code = code.replace("""        if book_move is not None and self._move_to_pos(book_move) in moves:
            return book_move""", """        if book_move is not None and self._move_to_pos(book_move) in moves:
            self._t_book = time.perf_counter() - start_total
            total_time = time.perf_counter() - start_total
            self._log_profile(total_time, True, actual_turn)
            return book_move""")

# Endgame return
code = code.replace("""                alpha = max(alpha, best_score)
            return self._pos_to_move(best_move)""", """                alpha = max(alpha, best_score)
            self._t_search = time.perf_counter() - start_total
            total_time = time.perf_counter() - start_total
            self._log_profile(total_time, False, actual_turn)
            return self._pos_to_move(best_move)""")

# Final return
code = code.replace("""            best_move = iter_best_move
            best_score = iter_best_score
        return self._pos_to_move(best_move)""", """            best_move = iter_best_move
            best_score = iter_best_score
        self._t_search = time.perf_counter() - start_total
        total_time = time.perf_counter() - start_total
        self._log_profile(total_time, False, actual_turn)
        return self._pos_to_move(best_move)""")

# _negascout nodes visited
code = code.replace("""        # 葉ノードでは、現在手番から見た盤面評価を返す。
        if depth == 0:""", """        # 葉ノードでは、現在手番から見た盤面評価を返す。
        MyPlayer._nodes_visited += 1
        if depth == 0:""")

# _search_hash_get
code = code.replace("""    def _search_hash_get(cls, key: int, depth: int, alpha: float, beta: float) -> tuple[int, float, float] | None:
        cls.SEARCH_HASH_GET_COUNT += 1
        index = cls._search_hash_index(key)
        entry = cls.SEARCH_HASH_TABLE[index]
        if entry is not None and entry[0] == key:
            if entry[1] >= depth:
                score, flag = entry[2], entry[3]
                if flag == 0:
                    return entry
                if flag == 1 and score <= alpha:
                    return entry
                if flag == 2 and score >= beta:
                    return entry
        return None""", """    def _search_hash_get(cls, key: int, depth: int, alpha: float, beta: float) -> tuple[int, float, float] | None:
        import time
        t0 = time.perf_counter()
        cls._tthash_gets += 1
        cls.SEARCH_HASH_GET_COUNT += 1
        index = cls._search_hash_index(key)
        entry = cls.SEARCH_HASH_TABLE[index]
        res = None
        if entry is not None and entry[0] == key:
            if entry[1] >= depth:
                score, flag = entry[2], entry[3]
                if flag == 0:
                    res = entry
                elif flag == 1 and score <= alpha:
                    res = entry
                elif flag == 2 and score >= beta:
                    res = entry
        if res is not None:
            cls._tthash_hits += 1
        cls._accum_search_tthash_time += time.perf_counter() - t0
        return res""")

# Eval
code = code.replace("""    def _evaluate_black_perspective_bits(
        self,
        state: tuple[int, int],
        pattern_keys: tuple[int, ...] | None = None,
        surrounds: tuple[int, int] | None = None,
    ) -> float:
        cached = MyPlayer.EVAL_CACHE.get(state)
        
        if cached is not None:

            return cached""", """    def _evaluate_black_perspective_bits(
        self,
        state: tuple[int, int],
        pattern_keys: tuple[int, ...] | None = None,
        surrounds: tuple[int, int] | None = None,
    ) -> float:
        import time
        t0 = time.perf_counter()
        MyPlayer._nodes_evaluated += 1
        MyPlayer._eval_cache_gets += 1
        cached = MyPlayer.EVAL_CACHE.get(state)
        
        if cached is not None:
            MyPlayer._eval_cache_hits += 1
            dt = time.perf_counter() - t0
            MyPlayer._accum_eval_time += dt
            MyPlayer._accum_eval_hit_time += dt
            return cached""")

code = code.replace("""        if MyPlayer._ensure_evaluate_patterns_tables():
            result = MyPlayer._evaluate_patterns_func_static(""", """        t_pat = time.perf_counter()
        if MyPlayer._ensure_evaluate_patterns_tables():
            result = MyPlayer._evaluate_patterns_func_static(""")

code = code.replace("""                result += group_sum * final_dense[pattern_name_to_final_index[name]]
        add_key = self._additional_key_bits(state, surrounds)""", """                result += group_sum * final_dense[pattern_name_to_final_index[name]]
        MyPlayer._accum_eval_pattern_time += time.perf_counter() - t_pat
        add_key = self._additional_key_bits(state, surrounds)""")

code = code.replace("""        cache[state] = result

        return result""", """        cache[state] = result
        MyPlayer._accum_eval_time += time.perf_counter() - t0
        return result""")

# Add value
code = code.replace("""    def _add_value(cls, key: int) -> float:
        res = cls._compute_add_value(key)
        return res""", """    def _add_value(cls, key: int) -> float:
        import time
        t0 = time.perf_counter()
        res = cls._compute_add_value(key)
        cls._accum_eval_add_mlp_time += time.perf_counter() - t0
        return res""")

# Additional key
code = code.replace("""    def _additional_key_bits(self, state: tuple[int, int], surrounds: tuple[int, int] | None) -> int:
        cached = MyPlayer.ADDITIONAL_KEY_CACHE.get(state)
        if cached is not None:
            return cached

        mobility = self._mobility_diff_bits(state)
        
        if surrounds is None:
            surround_black, surround_white = self._surround_counts_bits(state)
        else:
            surround_black, surround_white = surrounds""", """    def _additional_key_bits(self, state: tuple[int, int], surrounds: tuple[int, int] | None) -> int:
        import time
        cached = MyPlayer.ADDITIONAL_KEY_CACHE.get(state)
        if cached is not None:
            return cached
            
        t_mob = time.perf_counter()
        mobility = self._mobility_diff_bits(state)
        MyPlayer._accum_eval_mobility_time += time.perf_counter() - t_mob
        
        t_sur = time.perf_counter()
        if surrounds is None:
            surround_black, surround_white = self._surround_counts_bits(state)
        else:
            surround_black, surround_white = surrounds
        MyPlayer._accum_eval_surround_time += time.perf_counter() - t_sur""")

# Combined legal cache
code = code.replace("""        cached = MyPlayer.COMBINED_LEGAL_CACHE.get(state)
        if cached is not None:
            return cached""", """        MyPlayer._combined_legal_cache_gets += 1
        cached = MyPlayer.COMBINED_LEGAL_CACHE.get(state)
        if cached is not None:
            MyPlayer._combined_legal_cache_hits += 1
            return cached""")

# Move gen
code = code.replace("""    def _legal_moves_bits(self, state: tuple[int, int], color: Cell) -> tuple[int, ...]:
        key = self._legal_moves_cache_key_bits(state, color)
        cached = MyPlayer.LEGAL_MOVES_CACHE.get(key)
        if cached is not None:
            return cached""", """    def _legal_moves_bits(self, state: tuple[int, int], color: Cell) -> tuple[int, ...]:
        import time
        t0 = time.perf_counter()
        MyPlayer._legal_moves_cache_gets += 1
        key = self._legal_moves_cache_key_bits(state, color)
        cached = MyPlayer.LEGAL_MOVES_CACHE.get(key)
        if cached is not None:
            MyPlayer._legal_moves_cache_hits += 1
            MyPlayer._accum_search_movegen_time += time.perf_counter() - t0
            return cached
            
        res = self._legal_moves_bits_inner(state, color)
        MyPlayer._accum_search_movegen_time += time.perf_counter() - t0
        return res
        
    def _legal_moves_bits_inner(self, state: tuple[int, int], color: Cell) -> tuple[int, ...]:
        key = self._legal_moves_cache_key_bits(state, color)""")

# Apply move full
code = code.replace("""    def _apply_move_full(
        self,
        state: tuple[int, int],
        pattern_keys: tuple[int, ...] | None,
        surrounds: tuple[int, int] | None,
        pos: int,
        color: Cell,
    ) -> tuple[tuple[int, int], tuple[int, ...] | None, tuple[int, int] | None]:
        if pattern_keys is None:""", """    def _apply_move_full(
        self,
        state: tuple[int, int],
        pattern_keys: tuple[int, ...] | None,
        surrounds: tuple[int, int] | None,
        pos: int,
        color: Cell,
    ) -> tuple[tuple[int, int], tuple[int, ...] | None, tuple[int, int] | None]:
        import time
        t0 = time.perf_counter()
        res = self._apply_move_full_inner(state, pattern_keys, surrounds, pos, color)
        MyPlayer._accum_search_applymove_time += time.perf_counter() - t0
        return res
        
    def _apply_move_full_inner(
        self,
        state: tuple[int, int],
        pattern_keys: tuple[int, ...] | None,
        surrounds: tuple[int, int] | None,
        pos: int,
        color: Cell,
    ) -> tuple[tuple[int, int], tuple[int, ...] | None, tuple[int, int] | None]:
        if pattern_keys is None:""")

# Order move positions
code = code.replace("""    def _order_move_positions_by_weight(self, moves: tuple[int, ...] | list[int]) -> list[int]:
        res = sorted(moves, key=lambda pos: self.ORDER_WEIGHTS[pos // 8][pos % 8], reverse=True)
        return res""", """    def _order_move_positions_by_weight(self, moves: tuple[int, ...] | list[int]) -> list[int]:
        import time
        t0 = time.perf_counter()
        res = sorted(moves, key=lambda pos: self.ORDER_WEIGHTS[pos // 8][pos % 8], reverse=True)
        MyPlayer._accum_search_moveorder_time += time.perf_counter() - t0
        return res""")

with open('my_othello_ai/pattern_eval/players/experiments/exp_071_080/exp_072.py', 'w') as f:
    f.write(code)
