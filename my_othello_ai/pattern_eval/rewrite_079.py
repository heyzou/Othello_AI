import re

with open('players/current.py', 'r') as f:
    content = f.read()

# 1. Add class variables
content = content.replace(
    "    EVAL_CACHE = {}",
    "    EVAL_CACHE = {}\n    WHITE_EVAL_CACHE = {}"
)
content = content.replace(
    "    ADDITIONAL_KEY_CACHE = {}",
    "    ADDITIONAL_KEY_CACHE = {}\n    WHITE_ADDITIONAL_KEY_CACHE = {}"
)
content = content.replace(
    "    EVALUATE_PATTERNS_TABLES = None",
    "    EVALUATE_PATTERNS_TABLES = None\n    WHITE_EVALUATE_PATTERNS_TABLES = None"
)

# 2. Update _ensure_evaluate_patterns_tables
old_ensure = """    def _ensure_evaluate_patterns_tables(cls) -> bool:
        if cls.EVALUATE_PATTERNS_TABLES is not None:
            return False

        pattern_name_to_final_index = cls._pattern_name_to_final_index()
        tables = []
        for name in pattern_name_to_final_index.keys():
            tables.extend(cls.PATTERN_VALUE_TABLES[name])
        cls.EVALUATE_PATTERNS_TABLES = tuple(tables)
        return True"""

new_ensure = """    def _ensure_evaluate_patterns_tables(cls) -> bool:
        if cls.EVALUATE_PATTERNS_TABLES is not None and cls.WHITE_EVALUATE_PATTERNS_TABLES is not None:
            return False

        pattern_name_to_final_index = cls._pattern_name_to_final_index()
        tables = []
        white_tables = []
        for name in pattern_name_to_final_index.keys():
            black_table = cls.PATTERN_VALUE_TABLES[name]
            tables.extend(black_table)
            
            size = cls.PATTERN_SIZES[name]
            w_tab = [0.0] * (3 ** size)
            for k, val in enumerate(black_table):
                inv = 0
                mult = 1
                temp_k = k
                for _ in range(size):
                    d = temp_k % 3
                    temp_k //= 3
                    if d == 0: inv += mult
                    elif d == 2: inv += 2 * mult
                    mult *= 3
                w_tab[inv] = val
            white_tables.extend(w_tab)
            
        cls.EVALUATE_PATTERNS_TABLES = tuple(tables)
        cls.WHITE_EVALUATE_PATTERNS_TABLES = tuple(white_tables)
        return True"""
content = content.replace(old_ensure, new_ensure)

# 3. Update _evaluate_for_color_bits
old_eval_color = """    def _evaluate_for_color_bits(
        self,
        state: tuple[int, int],
        color: Cell,
        pattern_keys: tuple[int, ...] | None = None,
        surrounds: tuple[int, int] | None = None,
    ) -> float:
        score = self._evaluate_black_perspective_bits(state, pattern_keys, surrounds)
        if color == Cell.BLACK:
            return score
        return -score"""

new_eval_color = """    def _evaluate_for_color_bits(
        self,
        state: tuple[int, int],
        color: Cell,
        pattern_keys: tuple[int, ...] | None = None,
        surrounds: tuple[int, int] | None = None,
    ) -> float:
        if color == Cell.BLACK:
            return self._evaluate_black_perspective_bits(state, pattern_keys, surrounds, is_white=False)
        return self._evaluate_black_perspective_bits(state, pattern_keys, surrounds, is_white=True)"""
content = content.replace(old_eval_color, new_eval_color)

# 4. Update _evaluate_black_perspective_bits
old_eval_black = """    def _evaluate_black_perspective_bits(
        self,
        state: tuple[int, int],
        pattern_keys: tuple[int, ...] | None = None,
        surrounds: tuple[int, int] | None = None,
    ) -> float:
        cached = MyPlayer.EVAL_CACHE.get(state)
        
        if cached is not None:

            return cached

        if pattern_keys is None:
            pattern_keys = self._pattern_keys_from_state(state)
        final_dense, final_bias = self._params()[2]
        
        if MyPlayer._ensure_evaluate_patterns_tables():
            result = MyPlayer._evaluate_patterns_func_static(
                pattern_keys,
                MyPlayer.EVALUATE_PATTERNS_TABLES,
                final_bias
            )
        else:
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
        add_key = self._additional_key_bits(state, surrounds)
        add_val = MyPlayer.ADD_MLP_TABLE[add_key]
        result += add_val

        cache = MyPlayer.EVAL_CACHE
        if len(cache) >= self.EVAL_CACHE_MAX_SIZE:
            cache.clear()
        cache[state] = result
        return result"""

new_eval_black = """    def _evaluate_black_perspective_bits(
        self,
        state: tuple[int, int],
        pattern_keys: tuple[int, ...] | None = None,
        surrounds: tuple[int, int] | None = None,
        is_white: bool = False,
    ) -> float:
        cache = MyPlayer.WHITE_EVAL_CACHE if is_white else MyPlayer.EVAL_CACHE
        cached = cache.get(state)
        
        if cached is not None:
            return cached

        if pattern_keys is None:
            pattern_keys = self._pattern_keys_from_state(state)
        final_dense, final_bias = self._params()[2]
        
        MyPlayer._ensure_evaluate_patterns_tables()
        tables = MyPlayer.WHITE_EVALUATE_PATTERNS_TABLES if is_white else MyPlayer.EVALUATE_PATTERNS_TABLES
        
        result = MyPlayer._evaluate_patterns_func_static(
            pattern_keys,
            tables,
            final_bias
        )
        
        add_key = self._additional_key_bits(state, surrounds, is_white)
        add_val = MyPlayer.ADD_MLP_TABLE[add_key]
        result += add_val

        if len(cache) >= self.EVAL_CACHE_MAX_SIZE:
            cache.clear()
        cache[state] = result
        return result"""
content = content.replace(old_eval_black, new_eval_black)

# 5. Update _additional_key_bits
old_add_key = """    def _additional_key_bits(self, state: tuple[int, int], surrounds: tuple[int, int] | None) -> int:
        cached = MyPlayer.ADDITIONAL_KEY_CACHE.get(state)
        if cached is not None:
            return cached
        mobility = self._mobility_diff_bits(state)
        if surrounds is None:
            surround_black, surround_white = self._surround_counts_bits(state)
        else:
            surround_black, surround_white = surrounds

        mobility = max(-30, min(30, mobility))
        surround_black = max(0, min(50, surround_black))
        surround_white = max(0, min(50, surround_white))
        result = ((mobility + 30) * 51 + surround_black) * 51 + surround_white
        MyPlayer.ADDITIONAL_KEY_CACHE[state] = result
        return result"""

new_add_key = """    def _additional_key_bits(self, state: tuple[int, int], surrounds: tuple[int, int] | None, is_white: bool = False) -> int:
        cache = MyPlayer.WHITE_ADDITIONAL_KEY_CACHE if is_white else MyPlayer.ADDITIONAL_KEY_CACHE
        cached = cache.get(state)
        if cached is not None:
            return cached
            
        mobility = self._mobility_diff_bits(state)
        if surrounds is None:
            surround_black, surround_white = self._surround_counts_bits(state)
        else:
            surround_black, surround_white = surrounds

        if is_white:
            mobility = -mobility
            surround_black, surround_white = surround_white, surround_black

        mobility = max(-30, min(30, mobility))
        surround_black = max(0, min(50, surround_black))
        surround_white = max(0, min(50, surround_white))
        result = ((mobility + 30) * 51 + surround_black) * 51 + surround_white
        
        cache[state] = result
        return result"""
content = content.replace(old_add_key, new_add_key)

with open('players/experiments/exp_071_080/exp_079.py', 'w') as f:
    f.write(content)

print("Generated exp_079.py")
