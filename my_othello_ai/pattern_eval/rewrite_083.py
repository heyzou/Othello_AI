import re

with open('players/experiments/exp_081_090/exp_083.py', 'r') as f:
    content = f.read()

# 1. Update SEARCH_DEPTH and Cache sizes
content = content.replace("SEARCH_DEPTH = 6", "SEARCH_DEPTH = 8")
content = content.replace("SEARCH_DEPTH = 7", "SEARCH_DEPTH = 8")
content = content.replace("LEGAL_MOVES_CACHE_MAX_SIZE = 65536", "LEGAL_MOVES_CACHE_MAX_SIZE = 131072")
content = content.replace("EVAL_CACHE_MAX_SIZE = 262144", "EVAL_CACHE_MAX_SIZE = 524288")
content = content.replace("SEARCH_HASH_TABLE_SIZE = 131072", "SEARCH_HASH_TABLE_SIZE = 524288")

# 2. Add Killer Moves logic into _negascout (if missing, but wait, the prompt doesn't explicitly ask for Killer Moves. The user specifically asked for Aspiration Windows. Let's just do Aspiration Windows to be safe and clean, and see if it drops under 1.5s).
# Actually, I suggested Killer Moves too, but the user explicitly quoted Aspiration Windows and said "Please do this in 083." So I will focus on Aspiration Windows.

# 3. Replace Iterative Deepening loop in next_move
repl_id = """        # 反復深化（Iterative Deepening: 深さ 1 から SEARCH_DEPTH - 1 まで段階的に探索）
        for current_depth in range(1, self.SEARCH_DEPTH + 1):
            if current_depth >= 4:
                # Aspiration Window
                alpha = best_score - 1.5
                beta = best_score + 1.5
            else:
                alpha = float("-inf")
                beta = float("inf")
            
            while True:
                iter_best_move = best_move
                iter_best_score = float("-inf")
                current_alpha = alpha
                
                ordered_moves = self._order_move_positions_by_weight(moves)
                if iter_best_move in ordered_moves:
                    ordered_moves.remove(iter_best_move)
                    ordered_moves.insert(0, iter_best_move)

                for index, move in enumerate(ordered_moves):
                    child = self._apply_move_full(
                        state, pattern_keys, None, move, self.color
                    )
                    next_state, next_pattern_keys, next_surrounds = child
                    
                    if index == 0 or current_depth <= 1:
                        score = -self._negascout(
                            next_state, next_pattern_keys, next_surrounds, depth=current_depth,
                            current_color=self._opponent_of(self.color),
                            alpha=-beta, beta=-current_alpha
                        )
                    else:
                        # PVS / NegaScout root search
                        score = -self._negascout(
                            next_state, next_pattern_keys, next_surrounds, depth=current_depth,
                            current_color=self._opponent_of(self.color),
                            alpha=-current_alpha - 1.0, beta=-current_alpha
                        )
                        if current_alpha < score < beta:
                            score = -self._negascout(
                                next_state, next_pattern_keys, next_surrounds, depth=current_depth,
                                current_color=self._opponent_of(self.color),
                                alpha=-beta, beta=-score
                            )
                            
                    if score > iter_best_score:
                        iter_best_score = score
                        iter_best_move = move
                    current_alpha = max(current_alpha, iter_best_score)
                    if current_alpha >= beta:
                        break

                # Fail low or fail high checks for Aspiration Window
                if iter_best_score <= alpha:
                    # Failed low: true score is <= alpha. Open window downwards.
                    alpha = float("-inf")
                    continue
                elif iter_best_score >= beta:
                    # Failed high: true score is >= beta. Open window upwards.
                    beta = float("inf")
                    continue
                else:
                    # Score is within window!
                    break

            best_move = iter_best_move
            best_score = iter_best_score
        return self._pos_to_move(best_move)"""

content = re.sub(
    r"        # 反復深化（Iterative Deepening: 深さ 1 から SEARCH_DEPTH - 1 まで段階的に探索）.*?return self\._pos_to_move\(best_move\)",
    repl_id,
    content,
    flags=re.DOTALL
)

with open('players/experiments/exp_081_090/exp_083.py', 'w') as f:
    f.write(content)

print("Rewrote exp_083.py to add Aspiration Windows.")
