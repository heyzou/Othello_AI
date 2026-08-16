import re

with open('players/experiments/exp_041_050/exp_050_lazy_eval.py', 'r') as f:
    code = f.read()

# _negascout signature
code = re.sub(
    r'def _negascout\(\s*self,\s*state: tuple\[int, int\],\s*pattern_keys: tuple\[int, \.\.\.\] \| None,\s*depth: int,\s*current_color: Cell,\s*alpha: float,\s*beta: float,\s*allow_probcut: bool = True,\s*\) -> float:',
    r'def _negascout(\n        self,\n        state: tuple[int, int],\n        depth: int,\n        current_color: Cell,\n        alpha: float,\n        beta: float,\n        allow_probcut: bool = True,\n    ) -> float:',
    code
)

# _alpha_beta_simple signature
code = re.sub(
    r'def _alpha_beta_simple\(\s*self,\s*state: tuple\[int, int\],\s*pattern_keys: tuple\[int, \.\.\.\] \| None,\s*depth: int,\s*current_color: Cell,\s*alpha: float,\s*beta: float,\s*\) -> float:',
    r'def _alpha_beta_simple(\n        self,\n        state: tuple[int, int],\n        depth: int,\n        current_color: Cell,\n        alpha: float,\n        beta: float,\n    ) -> float:',
    code
)

# _evaluate_for_color_bits signature
code = re.sub(
    r'def _evaluate_for_color_bits\(\s*self,\s*state: tuple\[int, int\],\s*current_color: Cell,\s*pattern_keys: tuple\[int, \.\.\.\] \| None = None\s*\) -> float:',
    r'def _evaluate_for_color_bits(self, state: tuple[int, int], current_color: Cell) -> float:',
    code
)
code = re.sub(
    r'def _evaluate_for_color_bits\(\s*self,\s*state: tuple\[int, int\],\s*color: Cell,\s*pattern_keys: tuple\[int, \.\.\.\] \| None = None\s*\) -> float:',
    r'def _evaluate_for_color_bits(self, state: tuple[int, int], color: Cell) -> float:',
    code
)

# Replace passing pattern_keys to _evaluate_for_color_bits
code = re.sub(
    r'return self\._evaluate_for_color_bits\(state, current_color, pattern_keys\)',
    r'return self._evaluate_for_color_bits(state, current_color)',
    code
)
code = re.sub(
    r'return self\._evaluate_for_color_bits\(state, color, pattern_keys\)',
    r'return self._evaluate_for_color_bits(state, color)',
    code
)
code = re.sub(
    r'self\._evaluate_for_color_bits\(next_state, current_color, next_pattern_keys\)',
    r'self._evaluate_for_color_bits(next_state, current_color)',
    code
)

# Remove next_pattern_keys from _negascout and _alpha_beta_simple calls
code = re.sub(
    r'self\._negascout\(\s*state,\s*pattern_keys,\s*depth,\s*next_color,\s*-beta,\s*-alpha,\s*allow_probcut\s*\)',
    r'self._negascout(state, depth, next_color, -beta, -alpha, allow_probcut)',
    code
)
code = re.sub(
    r'self\._probcut\(\s*state,\s*pattern_keys,\s*depth,\s*current_color,\s*alpha,\s*beta\s*\)',
    r'self._probcut(state, depth, current_color, alpha, beta)',
    code
)
code = re.sub(
    r'next_state, next_pattern_keys = self\._apply_move_with_pattern_keys\(\s*state,\s*pattern_keys,\s*move,\s*current_color\s*\)',
    r'next_state = self._apply_move_bits(state, move, current_color)',
    code
)
code = re.sub(
    r'children\.append\(\(move, next_state, next_pattern_keys, order_score\)\)',
    r'children.append((move, next_state, order_score))',
    code
)
code = re.sub(
    r'next_pattern_keys = child\[2\]',
    r'',
    code
)
code = re.sub(
    r'self\._negascout\(\s*next_state,\s*next_pattern_keys,\s*depth - 1,\s*next_color,\s*-search_window,\s*-alpha,\s*allow_probcut\s*\)',
    r'self._negascout(next_state, depth - 1, next_color, -search_window, -alpha, allow_probcut)',
    code
)
code = re.sub(
    r'self\._negascout\(\s*next_state,\s*next_pattern_keys,\s*depth - 1,\s*next_color,\s*-beta,\s*-score,\s*allow_probcut\s*\)',
    r'self._negascout(next_state, depth - 1, next_color, -beta, -score, allow_probcut)',
    code
)
code = re.sub(
    r'self\._alpha_beta_simple\(\s*state,\s*pattern_keys,\s*depth,\s*current_color,\s*alpha,\s*beta\s*\)',
    r'self._alpha_beta_simple(state, depth, current_color, alpha, beta)',
    code
)
code = re.sub(
    r'self\._alpha_beta_simple\(\s*state,\s*pattern_keys,\s*depth,\s*next_color,\s*-beta,\s*-alpha\s*\)',
    r'self._alpha_beta_simple(state, depth, next_color, -beta, -alpha)',
    code
)
code = re.sub(
    r'self\._alpha_beta_simple\(\s*next_state,\s*next_pattern_keys,\s*depth - 1,\s*next_color,\s*-beta,\s*-alpha\s*\)',
    r'self._alpha_beta_simple(next_state, depth - 1, next_color, -beta, -alpha)',
    code
)

# _probcut signature
code = re.sub(
    r'def _probcut\(\s*self,\s*state: tuple\[int, int\],\s*pattern_keys: tuple\[int, \.\.\.\] \| None,\s*depth: int,\s*current_color: Cell,\s*alpha: float,\s*beta: float,\s*\) -> float \| None:',
    r'def _probcut(\n        self,\n        state: tuple[int, int],\n        depth: int,\n        current_color: Cell,\n        alpha: float,\n        beta: float,\n    ) -> float | None:',
    code
)
code = re.sub(
    r'self\._negascout\(\s*state,\s*pattern_keys,\s*shallow_depth,\s*current_color,\s*bound - 0\.001,\s*bound,\s*allow_probcut=False,\s*\)',
    r'self._negascout(state, shallow_depth, current_color, bound - 0.001, bound, allow_probcut=False)',
    code
)

with open('players/experiments/exp_041_050/exp_050_lazy_eval.py', 'w') as f:
    f.write(code)

print("SUCCESS")
