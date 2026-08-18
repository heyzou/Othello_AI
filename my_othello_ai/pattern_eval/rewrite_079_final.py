import re

with open('players/experiments/exp_071_080/exp_079.py', 'r') as f:
    content = f.read()

# 1. Add class variables
content = content.replace(
    "    PATTERN_VALUE_TABLES: dict[str, tuple[float, ...]] = {}",
    "    PATTERN_VALUE_TABLES: dict[str, tuple[float, ...]] = {}\n    WHITE_PATTERN_VALUE_TABLES: dict[str, tuple[float, ...]] = {}"
)
content = content.replace(
    "    PARTIAL_PATTERN_VALUE_TABLES = {}",
    "    PARTIAL_PATTERN_VALUE_TABLES = {}\n    PARTIAL_WHITE_PATTERN_VALUE_TABLES = {}"
)

# 2. Update _pattern_value_table
old_pattern_value_table = """    @classmethod
    def _pattern_value_table(cls, name: str):
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
        return table"""

new_pattern_value_table = """    @classmethod
    def _pattern_value_table(cls, name: str):
        cached = cls.PATTERN_VALUE_TABLES.get(name)
        if cached is not None:
            return cached

        size = cls.PATTERN_SIZES[name]
        partial = cls.PARTIAL_PATTERN_VALUE_TABLES.get(name)
        white_partial = cls.PARTIAL_WHITE_PATTERN_VALUE_TABLES.get(name)
        if partial is None:
            table = [0.0] * (3 ** size)
            white_table = [0.0] * (3 ** size)
            for key in range(3 ** size):
                val = cls._compute_pattern_value(name, key)
                table[key] = val
                inv = 0
                mult = 1
                temp_k = key
                for _ in range(size):
                    d = temp_k % 3
                    temp_k //= 3
                    if d == 0: inv += mult
                    elif d == 2: inv += 2 * mult
                    mult *= 3
                white_table[inv] = val
            table = tuple(table)
            white_table = tuple(white_table)
        else:
            for key in range(3 ** size):
                if partial[key] is None:
                    val = cls._compute_pattern_value(name, key)
                    partial[key] = val
                    inv = 0
                    mult = 1
                    temp_k = key
                    for _ in range(size):
                        d = temp_k % 3
                        temp_k //= 3
                        if d == 0: inv += mult
                        elif d == 2: inv += 2 * mult
                        mult *= 3
                    white_partial[inv] = val
            table = tuple(partial)
            white_table = tuple(white_partial)
            cls.PARTIAL_PATTERN_VALUE_TABLES.pop(name, None)
            cls.PARTIAL_WHITE_PATTERN_VALUE_TABLES.pop(name, None)
            cls.PARTIAL_PATTERN_VALUE_INDEXES.pop(name, None)
        cls.PATTERN_VALUE_TABLES[name] = table
        cls.WHITE_PATTERN_VALUE_TABLES[name] = white_table
        cls.PATTERN_CACHE = {}
        return table"""
content = content.replace(old_pattern_value_table, new_pattern_value_table)

# 3. Update _warm_pattern_value_table_chunk
old_warm_chunk = """    @classmethod
    def _warm_pattern_value_table_chunk(cls, name: str) -> None:
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
            cls.PARTIAL_PATTERN_VALUE_INDEXES[name] = end"""

new_warm_chunk = """    @classmethod
    def _warm_pattern_value_table_chunk(cls, name: str) -> None:
        size = cls.PATTERN_SIZES[name]
        total = 3 ** size
        partial = cls.PARTIAL_PATTERN_VALUE_TABLES.get(name)
        white_partial = cls.PARTIAL_WHITE_PATTERN_VALUE_TABLES.get(name)
        if partial is None:
            partial = [None] * total
            white_partial = [None] * total
            cls.PARTIAL_PATTERN_VALUE_TABLES[name] = partial
            cls.PARTIAL_WHITE_PATTERN_VALUE_TABLES[name] = white_partial

        start = cls.PARTIAL_PATTERN_VALUE_INDEXES.get(name, 0)
        end = min(total, start + cls.WARM_TABLE_CHUNK_SIZE)
        for key in range(start, end):
            val = cls._compute_pattern_value(name, key)
            partial[key] = val
            inv = 0
            mult = 1
            temp_k = key
            for _ in range(size):
                d = temp_k % 3
                temp_k //= 3
                if d == 0: inv += mult
                elif d == 2: inv += 2 * mult
                mult *= 3
            white_partial[inv] = val

        if end >= total:
            cls.PATTERN_VALUE_TABLES[name] = tuple(partial)
            cls.WHITE_PATTERN_VALUE_TABLES[name] = tuple(white_partial)
            cls.PARTIAL_PATTERN_VALUE_TABLES.pop(name, None)
            cls.PARTIAL_WHITE_PATTERN_VALUE_TABLES.pop(name, None)
            cls.PARTIAL_PATTERN_VALUE_INDEXES.pop(name, None)
            cls.PATTERN_CACHE = {}
        else:
            cls.PARTIAL_PATTERN_VALUE_INDEXES[name] = end"""
content = content.replace(old_warm_chunk, new_warm_chunk)

# 4. Update _ensure_evaluate_patterns_tables
old_ensure = """    @classmethod
    def _ensure_evaluate_patterns_tables(cls):
        if cls.EVALUATE_PATTERNS_TABLES is not None and cls.WHITE_EVALUATE_PATTERNS_TABLES is not None:
            return True
            
        for name in cls.ACTIVE_PATTERN_NAMES:
            if name not in cls.PATTERN_VALUE_TABLES:
                return False
                
        final_dense, final_bias = cls._params()[2]
        
        tables = []
        white_tables = []
        for name in cls.ACTIVE_PATTERN_NAMES:
            original_table = cls.PATTERN_VALUE_TABLES[name]
            weight = final_dense[cls._pattern_name_to_final_index()[name]]
            size = cls.PATTERN_SIZES[name]
            
            multiplied_table = [0.0] * (3 ** size)
            w_table = [0.0] * (3 ** size)
            
            for k, val in enumerate(original_table):
                w_val = val * weight
                multiplied_table[k] = w_val
                
                inv = 0
                mult = 1
                temp_k = k
                for _ in range(size):
                    d = temp_k % 3
                    temp_k //= 3
                    if d == 0: inv += mult
                    elif d == 2: inv += 2 * mult
                    mult *= 3
                w_table[inv] = w_val
                
            tables.append(tuple(multiplied_table))
            white_tables.append(tuple(w_table))
            
        cls.EVALUATE_PATTERNS_TABLES = tuple(tables)
        cls.WHITE_EVALUATE_PATTERNS_TABLES = tuple(white_tables)
        return True"""

new_ensure = """    @classmethod
    def _ensure_evaluate_patterns_tables(cls):
        if cls.EVALUATE_PATTERNS_TABLES is not None and cls.WHITE_EVALUATE_PATTERNS_TABLES is not None:
            return True
            
        for name in cls.ACTIVE_PATTERN_NAMES:
            if name not in cls.PATTERN_VALUE_TABLES:
                return False
                
        final_dense, final_bias = cls._params()[2]
        
        tables = []
        white_tables = []
        for name in cls.ACTIVE_PATTERN_NAMES:
            original_table = cls.PATTERN_VALUE_TABLES[name]
            white_original_table = cls.WHITE_PATTERN_VALUE_TABLES[name]
            weight = final_dense[cls._pattern_name_to_final_index()[name]]
            
            multiplied_table = tuple(val * weight for val in original_table)
            w_table = tuple(val * weight for val in white_original_table)
            
            tables.append(multiplied_table)
            white_tables.append(w_table)
            
        cls.EVALUATE_PATTERNS_TABLES = tuple(tables)
        cls.WHITE_EVALUATE_PATTERNS_TABLES = tuple(white_tables)
        return True"""
content = content.replace(old_ensure, new_ensure)

# 5. Update _evaluate_black_perspective_bits fallback logic
old_fallback = """            for name, start, end in group_infos:
                group_sum = 0.0
                pattern_table = MyPlayer.PATTERN_VALUE_TABLES.get(name)
                size = MyPlayer.PATTERN_SIZES[name]
                for index in range(start, end):
                    key = pattern_keys[index]
                    if is_white:
                        inv = 0
                        mult = 1
                        temp_k = key
                        for _ in range(size):
                            d = temp_k % 3
                            temp_k //= 3
                            if d == 0: inv += mult
                            elif d == 2: inv += 2 * mult
                            mult *= 3
                        key = inv
                        
                    if pattern_table is None:
                        group_sum += MyPlayer._compute_pattern_value(name, key)
                    else:
                        group_sum += pattern_table[key]
                result += group_sum * final_dense[pattern_name_to_final_index[name]]"""

new_fallback = """            for name, start, end in group_infos:
                group_sum = 0.0
                pattern_table = MyPlayer.WHITE_PATTERN_VALUE_TABLES.get(name) if is_white else MyPlayer.PATTERN_VALUE_TABLES.get(name)
                size = MyPlayer.PATTERN_SIZES[name]
                for index in range(start, end):
                    key = pattern_keys[index]
                    if pattern_table is None:
                        if is_white:
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
                result += group_sum * final_dense[pattern_name_to_final_index[name]]"""
content = content.replace(old_fallback, new_fallback)

with open('players/experiments/exp_071_080/exp_079.py', 'w') as f:
    f.write(content)

print("Generated exp_079.py with synchronous white table warming")
