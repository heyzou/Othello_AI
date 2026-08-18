import re

with open('players/experiments/exp_071_080/exp_079.py', 'r') as f:
    content = f.read()

# 1. Class level variables
repl = """    PATTERN_CACHE = {}
    ADD_CACHE = {}
    PATTERN_VALUE_TABLES: dict[str, tuple[float, ...]] = {}
    WHITE_PATTERN_VALUE_TABLES: dict[str, tuple[float, ...]] = {}
    PARTIAL_PATTERN_VALUE_TABLES = {}
    PARTIAL_WHITE_PATTERN_VALUE_TABLES = {}
    PARTIAL_PATTERN_VALUE_INDEXES = {}
    PARTIAL_WHITE_PATTERN_VALUE_INDEXES = {}
    ADD_VALUE_TABLE = None
    ADDITIONAL_KEY_CACHE = {}
    WHITE_ADDITIONAL_KEY_CACHE = {}
    COMBINED_LEGAL_CACHE = {}
    LEGAL_MOVES_CACHE = {}
    EVAL_CACHE = {}
    WHITE_EVAL_CACHE = {}
    EVAL_TABLE_WARM_INDEX = 0
    SEARCH_HASH_TABLE = [None] * SEARCH_HASH_TABLE_SIZE
    SEARCH_HASH_GET_COUNT = 0
    SEARCH_HASH_REG_COUNT = 0

    UPDATE_FLIP_BLACK_FUNCS_STATIC = None
    UPDATE_FLIP_WHITE_FUNCS_STATIC = None
    UPDATE_POS_BLACK_FUNCS_STATIC = None
    UPDATE_POS_WHITE_FUNCS_STATIC = None
    
    EVALUATE_PATTERNS_FUNC = None
    EVALUATE_PATTERNS_TABLES = None
    WHITE_EVALUATE_PATTERNS_TABLES = None
    BOOK_CACHE = None"""

content = re.sub(r"    PATTERN_CACHE = {}.*?BOOK_CACHE = None", repl, content, flags=re.DOTALL)

# 2. __init__ method
repl_init = """    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        MyPlayer._pattern_bit_specs()
        MyPlayer._pattern_key_meta()
        if self.color == Cell.WHITE:
            MyPlayer._precompute_init_evaluation_tables_white()
            MyPlayer._warm_init_evaluation_table_steps_white()
        else:
            MyPlayer._precompute_init_evaluation_tables_black()
            MyPlayer._warm_init_evaluation_table_steps_black()"""
content = re.sub(r"    def __init__\(self, color: Cell\):\n        super\(\)\.__init__\(color\)", repl_init, content)

# 3. next_move method
repl_next = """    def next_move(self, board: Board) -> Move:

        self._pattern_bit_specs()

        state = self._board_to_bits(board)
        actual_turn = (state[0] | state[1]).bit_count() - 3
        pattern_keys = self._pattern_keys_from_state(state)
        moves = self._legal_moves_bits(state, self.color)
        if not moves:
            return None
            
        if self.color == Cell.WHITE:
            MyPlayer._warm_evaluation_table_steps_white(actual_turn)
        else:
            MyPlayer._warm_evaluation_table_steps_black(actual_turn)"""
content = re.sub(r"    def next_move\(self, board: Board\) -> Move:.*?(?=        book_move = self\._book_move_bits\(state\))", repl_next + "\n", content, flags=re.DOTALL)

# 4. _evaluate_for_color_bits
repl_eval_color = """    def _evaluate_for_color_bits(
        self,
        state: tuple[int, int],
        color: Cell,
        pattern_keys: tuple[int, ...] | None = None,
        surrounds: tuple[int, int] | None = None,
    ) -> float:
        if color == Cell.BLACK:
            return self._evaluate_black_perspective_bits(state, pattern_keys, surrounds, is_white=False)
        return self._evaluate_black_perspective_bits(state, pattern_keys, surrounds, is_white=True)"""
content = re.sub(r"    def _evaluate_for_color_bits\(.*?\)\s*->\s*float:.*?return -score", repl_eval_color, content, flags=re.DOTALL)

# 5. _evaluate_black_perspective_bits
repl_eval_black = """    def _evaluate_black_perspective_bits(
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
        
        ready = MyPlayer._ensure_evaluate_patterns_tables_white() if is_white else MyPlayer._ensure_evaluate_patterns_tables_black()
        
        if ready:
            tables = MyPlayer.WHITE_EVALUATE_PATTERNS_TABLES if is_white else MyPlayer.EVALUATE_PATTERNS_TABLES
            result = MyPlayer._evaluate_patterns_func_static(
                pattern_keys,
                tables,
                final_bias
            )
        else:
            pattern_name_to_final_index = MyPlayer._pattern_name_to_final_index()
            group_infos = MyPlayer._pattern_key_group_infos()
            result = final_bias
            for name, start, end in group_infos:
                group_sum = 0.0
                pattern_table = MyPlayer.WHITE_PATTERN_VALUE_TABLES.get(name) if is_white else MyPlayer.PATTERN_VALUE_TABLES.get(name)
                for index in range(start, end):
                    key = pattern_keys[index]
                    if pattern_table is None:
                        # Fallback for keys not even computed yet
                        if is_white:
                            size = MyPlayer.PATTERN_SIZES[name]
                            inv = 0
                            mult = 1
                            temp_k = key
                            for _ in range(size):
                                d = temp_k % 3
                                temp_k //= 3
                                if d == 0: inv += mult
                                elif d == 2: inv += 2 * mult
                                mult *= 3
                            group_sum += MyPlayer._compute_pattern_value(name, inv)
                        else:
                            group_sum += MyPlayer._compute_pattern_value(name, key)
                    else:
                        group_sum += pattern_table[key]
                result += group_sum * final_dense[pattern_name_to_final_index[name]]
        
        add_key = self._additional_key_bits(state, surrounds, is_white)
        add_value = self._add_value(add_key)
        result += add_value * final_dense[len(self.PATTERN_SIZES)]
        
        if len(cache) >= self.EVAL_CACHE_MAX_SIZE:
            cache.clear()
        cache[state] = result

        return result"""
content = re.sub(r"    def _evaluate_black_perspective_bits\(.*?\)\s*->\s*float:.*?return result", repl_eval_black, content, flags=re.DOTALL)

# 6. warmup logic methods
repl_warmups = """    @classmethod
    def _precompute_init_evaluation_tables_black(cls) -> None:
        for name in cls.INIT_PRECOMPUTED_PATTERN_NAMES:
            cls._pattern_value_table_black(name)

    @classmethod
    def _precompute_init_evaluation_tables_white(cls) -> None:
        for name in cls.INIT_PRECOMPUTED_PATTERN_NAMES:
            cls._pattern_value_table_white(name)

    @classmethod
    def _warm_init_evaluation_table_steps_black(cls) -> None:
        for _ in range(cls.INIT_WARM_TABLE_STEPS):
            if not cls._warm_evaluation_table_step_black():
                return

    @classmethod
    def _warm_init_evaluation_table_steps_white(cls) -> None:
        for _ in range(cls.INIT_WARM_TABLE_STEPS):
            if not cls._warm_evaluation_table_step_white():
                return

    @classmethod
    def _warm_evaluation_table_steps_black(cls, actual_turn: int) -> None:
        steps = max(10, 40 - actual_turn * 2)
        for _ in range(steps):
            if not cls._warm_evaluation_table_step_black():
                return

    @classmethod
    def _warm_evaluation_table_steps_white(cls, actual_turn: int) -> None:
        steps = max(10, 40 - actual_turn * 2)
        for _ in range(steps):
            if not cls._warm_evaluation_table_step_white():
                return

    @classmethod
    def _warm_evaluation_table_step_black(cls) -> bool:
        for name in cls.WARM_PATTERN_NAMES:
            if name not in cls.PATTERN_VALUE_TABLES:
                cls._warm_pattern_value_table_chunk_black(name)
                return True
        return False

    @classmethod
    def _warm_evaluation_table_step_white(cls) -> bool:
        for name in cls.WARM_PATTERN_NAMES:
            if name not in cls.WHITE_PATTERN_VALUE_TABLES:
                cls._warm_pattern_value_table_chunk_white(name)
                return True
        return False

    @classmethod
    def _warm_pattern_value_table_chunk_black(cls, name: str) -> None:
        size = cls.PATTERN_SIZES[name]
        total = 3 ** size
        partial = cls.PARTIAL_PATTERN_VALUE_TABLES.get(name)
        if partial is None:
            partial = [None] * total
            cls.PARTIAL_PATTERN_VALUE_TABLES[name] = partial

        start = cls.PARTIAL_PATTERN_VALUE_INDEXES.get(name, 0)
        end = min(total, start + cls.WARM_TABLE_CHUNK_SIZE)
        for key in range(start, end):
            partial[key] = cls._compute_pattern_value(name, key)

        if end >= total:
            cls.PATTERN_VALUE_TABLES[name] = tuple(partial)
            cls.PARTIAL_PATTERN_VALUE_TABLES.pop(name, None)
            cls.PARTIAL_PATTERN_VALUE_INDEXES.pop(name, None)
            cls.PATTERN_CACHE = {}
        else:
            cls.PARTIAL_PATTERN_VALUE_INDEXES[name] = end

    @classmethod
    def _warm_pattern_value_table_chunk_white(cls, name: str) -> None:
        size = cls.PATTERN_SIZES[name]
        total = 3 ** size
        partial = cls.PARTIAL_WHITE_PATTERN_VALUE_TABLES.get(name)
        if partial is None:
            partial = [None] * total
            cls.PARTIAL_WHITE_PATTERN_VALUE_TABLES[name] = partial

        start = cls.PARTIAL_WHITE_PATTERN_VALUE_INDEXES.get(name, 0)
        end = min(total, start + cls.WARM_TABLE_CHUNK_SIZE)
        for key in range(start, end):
            inv = 0
            mult = 1
            temp_k = key
            for _ in range(size):
                d = temp_k % 3
                temp_k //= 3
                if d == 0: inv += mult
                elif d == 2: inv += 2 * mult
                mult *= 3
            partial[key] = cls._compute_pattern_value(name, inv)

        if end >= total:
            cls.WHITE_PATTERN_VALUE_TABLES[name] = tuple(partial)
            cls.PARTIAL_WHITE_PATTERN_VALUE_TABLES.pop(name, None)
            cls.PARTIAL_WHITE_PATTERN_VALUE_INDEXES.pop(name, None)
            cls.PATTERN_CACHE = {}
        else:
            cls.PARTIAL_WHITE_PATTERN_VALUE_INDEXES[name] = end

    @classmethod
    def _pattern_value_table_black(cls, name: str):
        cached = cls.PATTERN_VALUE_TABLES.get(name)
        if cached is not None:
            return cached

        size = cls.PATTERN_SIZES[name]
        partial = cls.PARTIAL_PATTERN_VALUE_TABLES.get(name)
        if partial is None:
            table = tuple(cls._compute_pattern_value(name, key) for key in range(3 ** size))
        else:
            for key in range(3 ** size):
                if partial[key] is None:
                    partial[key] = cls._compute_pattern_value(name, key)
            table = tuple(partial)
            cls.PARTIAL_PATTERN_VALUE_TABLES.pop(name, None)
            cls.PARTIAL_PATTERN_VALUE_INDEXES.pop(name, None)
        cls.PATTERN_VALUE_TABLES[name] = table
        cls.PATTERN_CACHE = {}
        return table

    @classmethod
    def _pattern_value_table_white(cls, name: str):
        cached = cls.WHITE_PATTERN_VALUE_TABLES.get(name)
        if cached is not None:
            return cached

        size = cls.PATTERN_SIZES[name]
        partial = cls.PARTIAL_WHITE_PATTERN_VALUE_TABLES.get(name)
        if partial is None:
            table = [0.0] * (3 ** size)
            for key in range(3 ** size):
                inv = 0
                mult = 1
                temp_k = key
                for _ in range(size):
                    d = temp_k % 3
                    temp_k //= 3
                    if d == 0: inv += mult
                    elif d == 2: inv += 2 * mult
                    mult *= 3
                table[key] = cls._compute_pattern_value(name, inv)
            table = tuple(table)
        else:
            for key in range(3 ** size):
                if partial[key] is None:
                    inv = 0
                    mult = 1
                    temp_k = key
                    for _ in range(size):
                        d = temp_k % 3
                        temp_k //= 3
                        if d == 0: inv += mult
                        elif d == 2: inv += 2 * mult
                        mult *= 3
                    partial[key] = cls._compute_pattern_value(name, inv)
            table = tuple(partial)
            cls.PARTIAL_WHITE_PATTERN_VALUE_TABLES.pop(name, None)
            cls.PARTIAL_WHITE_PATTERN_VALUE_INDEXES.pop(name, None)
        cls.WHITE_PATTERN_VALUE_TABLES[name] = table
        cls.PATTERN_CACHE = {}
        return table"""
content = re.sub(r"    @classmethod\n    def _precompute_evaluation_tables\(cls\).*?(?=    @staticmethod\n    def _leaky_relu)", repl_warmups + "\n", content, flags=re.DOTALL)

# 7. ensure evaluate patterns tables
repl_ensure = """    @classmethod
    def _ensure_evaluate_patterns_tables_black(cls):
        if cls.EVALUATE_PATTERNS_TABLES is not None:
            return True
            
        for name in cls.ACTIVE_PATTERN_NAMES:
            if name not in cls.PATTERN_VALUE_TABLES:
                return False
                
        final_dense, final_bias = cls._params()[2]
        
        tables = []
        for name in cls.ACTIVE_PATTERN_NAMES:
            original_table = cls.PATTERN_VALUE_TABLES[name]
            weight = final_dense[cls._pattern_name_to_final_index()[name]]
            tables.append(tuple(val * weight for val in original_table))
            
        cls.EVALUATE_PATTERNS_TABLES = tuple(tables)
        return True

    @classmethod
    def _ensure_evaluate_patterns_tables_white(cls):
        if cls.WHITE_EVALUATE_PATTERNS_TABLES is not None:
            return True
            
        for name in cls.ACTIVE_PATTERN_NAMES:
            if name not in cls.WHITE_PATTERN_VALUE_TABLES:
                return False
                
        final_dense, final_bias = cls._params()[2]
        
        tables = []
        for name in cls.ACTIVE_PATTERN_NAMES:
            original_table = cls.WHITE_PATTERN_VALUE_TABLES[name]
            weight = final_dense[cls._pattern_name_to_final_index()[name]]
            tables.append(tuple(val * weight for val in original_table))
            
        cls.WHITE_EVALUATE_PATTERNS_TABLES = tuple(tables)
        return True"""
content = re.sub(r"    @classmethod\n    def _ensure_evaluate_patterns_tables\(cls\).*?(?=    def _pattern_keys_from_state)", repl_ensure + "\n", content, flags=re.DOTALL)

# 8. additional key bits
repl_add_key = """    def _additional_key_bits(self, state: tuple[int, int], surrounds: tuple[int, int] | None = None, is_white: bool = False) -> int:
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
content = re.sub(r"    def _additional_key_bits\(.*?\)\s*->\s*int:.*?return result", repl_add_key, content, flags=re.DOTALL)


with open('players/experiments/exp_071_080/exp_079.py', 'w') as f:
    f.write(content)

print("Generated exp_079.py with complete color splitting logic")
