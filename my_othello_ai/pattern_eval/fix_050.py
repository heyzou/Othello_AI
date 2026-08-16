import re

with open('players/experiments/exp_041_050/exp_050_lazy_eval.py', 'r') as f:
    code = f.read()

# 1. Update _apply_move_with_pattern_keys -> _apply_move_bits
old_apply_def = """    def _apply_move_with_pattern_keys(
        self,
        state: tuple[int, int],
        pattern_keys: tuple[int, ...] | None,
        pos: int,
        color: Cell,
    ) -> tuple[tuple[int, int], tuple[int, ...]]:
        t0 = time.perf_counter()
        if pattern_keys is None:
            pattern_keys = self._pattern_keys_from_state(state)

        flips = self._flips_bits(state, pos, color)
        move_bit = 1 << pos
        black_bits, white_bits = state
        if color == Cell.BLACK:
            next_state = ((black_bits | flips | move_bit), (white_bits & ~flips))
        else:
            next_state = ((black_bits & ~flips), (white_bits | flips | move_bit))

        _, position_updates, _ = MyPlayer._pattern_key_meta()
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

        MyPlayer._accum_search_applymove_time += time.perf_counter() - t0
        return next_state, tuple(keys)"""

new_apply_def = """    def _apply_move_bits(
        self,
        state: tuple[int, int],
        pos: int,
        color: Cell,
    ) -> tuple[int, int]:
        t0 = time.perf_counter()
        flips = self._flips_bits(state, pos, color)
        move_bit = 1 << pos
        black_bits, white_bits = state
        if color == Cell.BLACK:
            next_state = ((black_bits | flips | move_bit), (white_bits & ~flips))
        else:
            next_state = ((black_bits & ~flips), (white_bits | flips | move_bit))
        MyPlayer._accum_search_applymove_time += time.perf_counter() - t0
        return next_state"""

code = code.replace(old_apply_def, new_apply_def)

# 2. Update all calls to _apply_move_with_pattern_keys -> _apply_move_bits
code = re.sub(
    r'next_state,\s*next_pattern_keys\s*=\s*self\._apply_move_with_pattern_keys\(\s*state,\s*pattern_keys,\s*pos,\s*current_color\s*\)',
    r'next_state = self._apply_move_bits(state, pos, current_color)',
    code
)

# 3. Update _evaluate_for_color_bits signature
code = re.sub(
    r'def _evaluate_for_color_bits\(\s*self,\s*state: tuple\[int, int\],\s*pattern_keys: tuple\[int, \.\.\.\] \| None,\s*color: Cell,\s*\) -> float:',
    r'def _evaluate_for_color_bits(self, state: tuple[int, int], color: Cell) -> float:',
    code
)
# And its inner call
code = re.sub(
    r'black_eval\s*=\s*self\._evaluate_black_perspective_bits\(\s*state,\s*pattern_keys\s*\)',
    r'black_eval = self._evaluate_black_perspective_bits(state)',
    code
)

# 4. Update _evaluate_black_perspective_bits signature
code = re.sub(
    r'def _evaluate_black_perspective_bits\(\s*self,\s*state: tuple\[int, int\],\s*pattern_keys: tuple\[int, \.\.\.\] \| None = None,\s*\) -> float:',
    r'def _evaluate_black_perspective_bits(self, state: tuple[int, int]) -> float:',
    code
)
# And its logic
code = re.sub(
    r'if pattern_keys is None:\s*pattern_keys = self\._pattern_keys_from_state\(state\)',
    r'pattern_keys = self._pattern_keys_from_state(state)',
    code
)

# 5. Update _negascout signature and calls
code = re.sub(
    r'def _negascout\(\s*self,\s*state: tuple\[int, int\],\s*pattern_keys: tuple\[int, \.\.\.\],\s*depth: int,\s*current_color: Cell,\s*alpha: float,\s*beta: float,\s*\) -> float:',
    r'def _negascout(\n        self,\n        state: tuple[int, int],\n        depth: int,\n        current_color: Cell,\n        alpha: float,\n        beta: float,\n    ) -> float:',
    code
)
# Fix the evaluate call inside _negascout
code = re.sub(
    r'return self\._evaluate_for_color_bits\(state, pattern_keys, current_color\)',
    r'return self._evaluate_for_color_bits(state, current_color)',
    code
)
# Fix the recursive calls in _negascout
code = re.sub(
    r'self\._negascout\(\s*state,\s*pattern_keys,\s*shallow_depth,\s*current_color,\s*bound - 0\.001,\s*bound\s*\)',
    r'self._negascout(state, shallow_depth, current_color, bound - 0.001, bound)',
    code
)
code = re.sub(
    r'self\._negascout\(\s*next_state,\s*next_pattern_keys,\s*depth - 1,\s*self\._opponent_of\(current_color\),\s*-beta,\s*-alpha\s*\)',
    r'self._negascout(next_state, depth - 1, self._opponent_of(current_color), -beta, -alpha)',
    code
)
code = re.sub(
    r'self\._negascout\(\s*next_state,\s*next_pattern_keys,\s*depth - 1,\s*self\._opponent_of\(current_color\),\s*-alpha - 0\.001,\s*-alpha\s*\)',
    r'self._negascout(next_state, depth - 1, self._opponent_of(current_color), -alpha - 0.001, -alpha)',
    code
)
code = re.sub(
    r'self\._negascout\(\s*next_state,\s*next_pattern_keys,\s*depth - 1,\s*self\._opponent_of\(current_color\),\s*-beta,\s*-iter_best_score\s*\)',
    r'self._negascout(next_state, depth - 1, self._opponent_of(current_color), -beta, -iter_best_score)',
    code
)
# The pass call in _negascout
code = re.sub(
    r'next_pattern_keys = pattern_keys\s*score = -self\._negascout\(\s*next_state,\s*next_pattern_keys,\s*depth - 1,\s*self\._opponent_of\(current_color\),\s*-beta,\s*-alpha\s*\)',
    r'score = -self._negascout(next_state, depth - 1, self._opponent_of(current_color), -beta, -alpha)',
    code
)

# 6. Update _alpha_beta_simple signature and calls
code = re.sub(
    r'def _alpha_beta_simple\(\s*self,\s*state: tuple\[int, int\],\s*pattern_keys: tuple\[int, \.\.\.\],\s*depth: int,\s*current_color: Cell,\s*alpha: float,\s*beta: float,\s*\) -> float:',
    r'def _alpha_beta_simple(\n        self,\n        state: tuple[int, int],\n        depth: int,\n        current_color: Cell,\n        alpha: float,\n        beta: float,\n    ) -> float:',
    code
)
code = re.sub(
    r'self\._alpha_beta_simple\(\s*next_state,\s*next_pattern_keys,\s*depth - 1,\s*self\._opponent_of\(current_color\),\s*-beta,\s*-alpha\s*\)',
    r'self._alpha_beta_simple(next_state, depth - 1, self._opponent_of(current_color), -beta, -alpha)',
    code
)
# Pass in alpha_beta_simple
code = re.sub(
    r'next_pattern_keys = pattern_keys\s*score = -self\._alpha_beta_simple\(\s*next_state,\s*next_pattern_keys,\s*depth - 1,\s*self\._opponent_of\(current_color\),\s*-beta,\s*-alpha\s*\)',
    r'score = -self._alpha_beta_simple(next_state, depth - 1, self._opponent_of(current_color), -beta, -alpha)',
    code
)

# 7. Clean up next_move
# In next_move, we had:
# pattern_keys = self._pattern_keys_from_state(state)
code = re.sub(r'\s*pattern_keys = self\._pattern_keys_from_state\(state\)\s*', '\n', code, count=1)
code = re.sub(
    r'score = -self\._negascout\(\s*next_state,\s*next_pattern_keys,\s*iter_depth - 1,\s*self\._opponent_of\(self\.color\),\s*-beta,\s*-alpha\s*\)',
    r'score = -self._negascout(next_state, iter_depth - 1, self._opponent_of(self.color), -beta, -alpha)',
    code
)

with open('players/experiments/exp_041_050/exp_050_lazy_eval.py', 'w') as f:
    f.write(code)
print("SUCCESS")
