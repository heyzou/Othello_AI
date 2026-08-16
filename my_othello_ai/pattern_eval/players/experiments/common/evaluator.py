"""Evaluation logic, pattern table precomputation, and neural network inference."""

try:
    from othellopy.core import Cell
except ImportError:
    try:
        from othellopy.board import Cell
    except ImportError:
        Cell = int

from .patterns import (
    PATTERN_INDEXES,
    PATTERN_SIZES,
    ACTIVE_PATTERN_NAMES,
    INIT_PRECOMPUTED_PATTERN_NAMES,
    WARM_PATTERN_NAMES,
    WARM_TABLE_CHUNK_SIZE,
    INIT_WARM_TABLE_STEPS,
    WARM_TABLE_STEPS_PER_MOVE,
)
from .weights import WEIGHTS
from .bitboard import (
    legal_move_mask_bits,
    surround_counts_bits,
    flips_bits,
)


class Evaluator:
    PARAMS = None
    PATTERN_CACHE = {}
    ADD_CACHE = {}
    PATTERN_VALUE_TABLES = {}
    PARTIAL_PATTERN_VALUE_TABLES = {}
    PARTIAL_PATTERN_VALUE_INDEXES = {}
    ADDITIONAL_KEY_CACHE = {}
    MOBILITY_CACHE = {}
    EVAL_CACHE = {}
    EVAL_CACHE_MAX_SIZE = 262144

    PATTERN_BIT_SPECS = None
    PATTERN_KEY_META = None

    @classmethod
    def params(cls):
        if cls.PARAMS is not None:
            return cls.PARAMS
        if not WEIGHTS:
            raise RuntimeError("WEIGHTS is empty")

        pos = 0

        def take():
            nonlocal pos
            val = WEIGHTS[pos]
            pos += 1
            return val

        patterns = {}
        for name, size in PATTERN_SIZES.items():
            dense0 = tuple(tuple(take() for _ in range(size * 2)) for _ in range(16))
            bias0 = tuple(take() for _ in range(16))
            dense1 = tuple(tuple(take() for _ in range(16)) for _ in range(16))
            bias1 = tuple(take() for _ in range(16))
            dense2 = tuple(take() for _ in range(16))
            bias2 = take()
            patterns[name] = (size, dense0, bias0, dense1, bias1, dense2, bias2)

        add_dense0 = tuple(tuple(take() for _ in range(3)) for _ in range(8))
        add_bias0 = tuple(take() for _ in range(8))
        add_dense1 = tuple(take() for _ in range(8))
        add_bias1 = take()
        final_dense = tuple(take() for _ in range(len(PATTERN_SIZES) + 1))
        final_bias = take()
        cls.PARAMS = (patterns, (add_dense0, add_bias0, add_dense1, add_bias1), (final_dense, final_bias))
        return cls.PARAMS

    @classmethod
    def pattern_bit_specs(cls):
        if cls.PATTERN_BIT_SPECS is not None:
            return cls.PATTERN_BIT_SPECS

        specs = {}
        for name, patterns in PATTERN_INDEXES.items():
            group_specs = []
            for pattern in patterns:
                weight = 1
                empty_key = 0
                parts = []
                for index in reversed(pattern):
                    bit = 1 << index
                    empty_key += weight + weight
                    parts.append((bit, weight, weight + weight))
                    weight *= 3
                group_specs.append((empty_key, tuple(parts)))
            specs[name] = tuple(group_specs)
        cls.PATTERN_BIT_SPECS = specs
        return specs

    @classmethod
    def pattern_key_meta(cls):
        if cls.PATTERN_KEY_META is not None:
            return cls.PATTERN_KEY_META

        specs = cls.pattern_bit_specs()
        empty_keys = []
        group_infos = []
        position_updates = [[] for _ in range(64)]
        key_index = 0
        for name in ACTIVE_PATTERN_NAMES:
            start = key_index
            for empty_key, parts in specs[name]:
                empty_keys.append(empty_key)
                for bit, white_delta, _ in parts:
                    position = bit.bit_length() - 1
                    position_updates[position].append((key_index, white_delta))
                key_index += 1
            group_infos.append((name, start, key_index))

        cls.PATTERN_KEY_META = (
            tuple(empty_keys),
            tuple(tuple(items) for items in position_updates),
            tuple(group_infos),
        )
        return cls.PATTERN_KEY_META

    @classmethod
    def pattern_key_group_infos(cls):
        return cls.pattern_key_meta()[2]

    @classmethod
    def pattern_name_to_final_index(cls):
        return {
            "diagonal8": 0,
            "diagonal7": 1,
            "diagonal6": 2,
            "diagonal5": 3,
            "edge": 4,
            "edge2X": 5,
            "triangle": 6,
            "corner3x3": 7,
        }

    @classmethod
    def leaky_relu(cls, value: float) -> float:
        return value if value >= 0.0 else 0.01 * value

    @classmethod
    def compute_pattern_value(cls, name: str, key: int) -> float:
        cache_key = (name, key)
        cached = cls.PATTERN_CACHE.get(cache_key)
        if cached is not None:
            return cached

        size, dense0, bias0, dense1, bias1, dense2, bias2 = cls.params()[0][name]
        arr = [0.0] * (size * 2)
        n = key
        for i in range(size - 1, -1, -1):
            digit = n % 3
            n //= 3
            if digit == 0:
                arr[i] = 1.0
            elif digit == 1:
                arr[size + i] = 1.0

        hidden0 = []
        for out_i in range(16):
            value = bias0[out_i]
            row = dense0[out_i]
            for in_i in range(size * 2):
                value += arr[in_i] * row[in_i]
            hidden0.append(cls.leaky_relu(value))

        result = bias2
        for out_i in range(16):
            value = bias1[out_i]
            row = dense1[out_i]
            for in_i in range(16):
                value += hidden0[in_i] * row[in_i]
            result += cls.leaky_relu(value) * dense2[out_i]

        result = cls.leaky_relu(result)
        cls.PATTERN_CACHE[cache_key] = result
        return result

    @classmethod
    def pattern_value_table(cls, name: str):
        cached = cls.PATTERN_VALUE_TABLES.get(name)
        if cached is not None:
            return cached

        size = PATTERN_SIZES[name]
        partial = cls.PARTIAL_PATTERN_VALUE_TABLES.get(name)
        if partial is None:
            table = tuple(cls.compute_pattern_value(name, key) for key in range(3 ** size))
        else:
            for key in range(3 ** size):
                if partial[key] is None:
                    partial[key] = cls.compute_pattern_value(name, key)
            table = tuple(partial)
            cls.PARTIAL_PATTERN_VALUE_TABLES.pop(name, None)
            cls.PARTIAL_PATTERN_VALUE_INDEXES.pop(name, None)
        cls.PATTERN_VALUE_TABLES[name] = table
        cls.PATTERN_CACHE = {}
        return table

    @classmethod
    def compute_add_value(cls, key: int) -> float:
        cached = cls.ADD_CACHE.get(key)
        if cached is not None:
            return cached

        tmp = key
        sur1 = tmp % 51
        tmp //= 51
        sur0 = tmp % 51
        mobility = tmp // 51 - 30
        arr = (mobility / 30.0, (sur0 - 15.0) / 15.0, (sur1 - 15.0) / 15.0)
        dense0, bias0, dense1, bias1 = cls.params()[1]

        hidden = []
        for out_i in range(8):
            value = bias0[out_i]
            row = dense0[out_i]
            for in_i in range(3):
                value += arr[in_i] * row[in_i]
            hidden.append(cls.leaky_relu(value))

        result = bias1
        for i in range(8):
            result += hidden[i] * dense1[i]
        result = cls.leaky_relu(result)
        cls.ADD_CACHE[key] = result
        return result

    @classmethod
    def precompute_init_evaluation_tables(cls) -> None:
        for name in INIT_PRECOMPUTED_PATTERN_NAMES:
            cls.pattern_value_table(name)

    @classmethod
    def warm_init_evaluation_table_steps(cls) -> None:
        for _ in range(INIT_WARM_TABLE_STEPS):
            if not cls.warm_evaluation_table_step():
                return

    @classmethod
    def warm_evaluation_table_steps(cls) -> None:
        for _ in range(WARM_TABLE_STEPS_PER_MOVE):
            if not cls.warm_evaluation_table_step():
                return

    @classmethod
    def warm_evaluation_table_step(cls) -> bool:
        for name in WARM_PATTERN_NAMES:
            if name not in cls.PATTERN_VALUE_TABLES:
                cls.warm_pattern_value_table_chunk(name)
                return True
        return False

    @classmethod
    def warm_pattern_value_table_chunk(cls, name: str) -> None:
        size = PATTERN_SIZES[name]
        total = 3 ** size
        partial = cls.PARTIAL_PATTERN_VALUE_TABLES.get(name)
        if partial is None:
            partial = [None] * total
            cls.PARTIAL_PATTERN_VALUE_TABLES[name] = partial

        start = cls.PARTIAL_PATTERN_VALUE_INDEXES.get(name, 0)
        end = min(total, start + WARM_TABLE_CHUNK_SIZE)
        for key in range(start, end):
            partial[key] = cls.compute_pattern_value(name, key)

        if end >= total:
            cls.PATTERN_VALUE_TABLES[name] = tuple(partial)
            cls.PARTIAL_PATTERN_VALUE_TABLES.pop(name, None)
            cls.PARTIAL_PATTERN_VALUE_INDEXES.pop(name, None)
            cls.PATTERN_CACHE = {}
        else:
            cls.PARTIAL_PATTERN_VALUE_INDEXES[name] = end

    @classmethod
    def pattern_keys_from_state(cls, state: tuple[int, int]) -> tuple[int, ...]:
        empty_keys, position_updates, _ = cls.pattern_key_meta()
        keys = list(empty_keys)
        black_bits, white_bits = state

        bits = black_bits
        while bits:
            bit = bits & -bits
            position = bit.bit_length() - 1
            for key_index, weight in position_updates[position]:
                keys[key_index] -= weight + weight
            bits ^= bit

        bits = white_bits
        while bits:
            bit = bits & -bits
            position = bit.bit_length() - 1
            for key_index, weight in position_updates[position]:
                keys[key_index] -= weight
            bits ^= bit

        return tuple(keys)

    @classmethod
    def additional_key_bits(cls, state: tuple[int, int]) -> int:
        cached = cls.ADDITIONAL_KEY_CACHE.get(state)
        if cached is not None:
            return cached

        mobility = cls.mobility_diff_bits(state)
        surround_black, surround_white = surround_counts_bits(state)
        mobility = max(-30, min(30, mobility))
        surround_black = max(0, min(50, surround_black))
        surround_white = max(0, min(50, surround_white))
        result = ((mobility + 30) * 51 + surround_black) * 51 + surround_white
        cls.ADDITIONAL_KEY_CACHE[state] = result
        return result

    @classmethod
    def mobility_diff_bits(cls, state: tuple[int, int]) -> int:
        cached = cls.MOBILITY_CACHE.get(state)
        if cached is not None:
            return cached

        mobility = (
            legal_move_mask_bits(state, Cell.BLACK).bit_count()
            - legal_move_mask_bits(state, Cell.WHITE).bit_count()
        )
        cls.MOBILITY_CACHE[state] = mobility
        return mobility

    @classmethod
    def apply_move_with_pattern_keys(
        cls,
        state: tuple[int, int],
        pattern_keys: tuple[int, ...] | None,
        pos: int,
        color: Cell,
    ) -> tuple[tuple[int, int], tuple[int, ...]]:
        if pattern_keys is None:
            pattern_keys = cls.pattern_keys_from_state(state)

        flips = flips_bits(state, pos, color)
        move_bit = 1 << pos
        black_bits, white_bits = state
        if color == Cell.BLACK:
            next_state = ((black_bits | flips | move_bit), (white_bits & ~flips))
        else:
            next_state = ((black_bits & ~flips), (white_bits | flips | move_bit))

        _, position_updates, _ = cls.pattern_key_meta()
        keys = list(pattern_keys)

        for key_index, weight in position_updates[pos]:
            if color == Cell.BLACK:
                keys[key_index] -= weight + weight
            else:
                keys[key_index] -= weight

        bits = flips
        while bits:
            bit = bits & -bits
            position = bit.bit_length() - 1
            for key_index, weight in position_updates[position]:
                if color == Cell.BLACK:
                    keys[key_index] -= weight
                else:
                    keys[key_index] += weight
            bits ^= bit

        return next_state, tuple(keys)

    @classmethod
    def evaluate_for_color_bits(
        cls,
        state: tuple[int, int],
        color: Cell,
        pattern_keys: tuple[int, ...] | None = None,
    ) -> float:
        score = cls.evaluate_black_perspective_bits(state, pattern_keys)
        if color == Cell.BLACK:
            return score
        return -score

    @classmethod
    def evaluate_black_perspective_bits(
        cls,
        state: tuple[int, int],
        pattern_keys: tuple[int, ...] | None = None,
    ) -> float:
        cached = cls.EVAL_CACHE.get(state)
        if cached is not None:
            return cached

        if pattern_keys is None:
            pattern_keys = cls.pattern_keys_from_state(state)

        final_dense, final_bias = cls.params()[2]
        pattern_name_to_final_index = cls.pattern_name_to_final_index()
        group_infos = cls.pattern_key_group_infos()
        result = final_bias
        for name, start, end in group_infos:
            group_sum = 0.0
            pattern_table = cls.PATTERN_VALUE_TABLES.get(name)
            for index in range(start, end):
                key = pattern_keys[index]
                if pattern_table is None:
                    group_sum += cls.compute_pattern_value(name, key)
                else:
                    group_sum += pattern_table[key]
            result += group_sum * final_dense[pattern_name_to_final_index[name]]

        add_key = cls.additional_key_bits(state)
        add_value = cls.compute_add_value(add_key)
        result += add_value * final_dense[len(PATTERN_SIZES)]

        cache = cls.EVAL_CACHE
        if len(cache) >= cls.EVAL_CACHE_MAX_SIZE:
            cache.clear()
        cache[state] = result
        return result
