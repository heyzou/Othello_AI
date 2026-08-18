import re

with open('my_othello_ai/pattern_eval/players/experiments/exp_071_080/exp_072.py', 'r') as f:
    code = f.read()

replacement = """            self._t_search = time.perf_counter() - start_total
            total_time = time.perf_counter() - start_total
            self._log_profile(total_time, False, actual_turn)
            return self._pos_to_move(best_move)"""

code = code.replace("            return self._pos_to_move(best_move)", replacement)

replacement2 = """        self._t_search = time.perf_counter() - start_total
        total_time = time.perf_counter() - start_total
        self._log_profile(total_time, False, actual_turn)
        return self._pos_to_move(best_move)"""

code = code.replace("        return self._pos_to_move(best_move)", replacement2)

with open('my_othello_ai/pattern_eval/players/experiments/exp_071_080/exp_072.py', 'w') as f:
    f.write(code)
