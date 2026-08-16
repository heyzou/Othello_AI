import re
import ast

with open('players/experiments/exp_041_050/exp_047_iterative_deepening.py') as f:
    exp_code = f.read()

with open('players/current.py') as f:
    cur_code = f.read()

def extract_block(code, start_marker, end_marker):
    start_idx = code.find(start_marker)
    if start_idx == -1: return None
    end_idx = code.find(end_marker, start_idx) + len(end_marker)
    return code[start_idx:end_idx]

pattern_indexes = extract_block(cur_code, '    PATTERN_INDEXES = {', '    }')
pattern_sizes = extract_block(cur_code, '    PATTERN_SIZES = {', '    }')
active_patterns = extract_block(cur_code, '    ACTIVE_PATTERN_NAMES = (', '    )')
precomputed = extract_block(cur_code, '    PRECOMPUTED_PATTERN_NAMES = (', '    )')
init_precomputed = extract_block(cur_code, '    INIT_PRECOMPUTED_PATTERN_NAMES = (', '    )')
warm_patterns = extract_block(cur_code, '    WARM_PATTERN_NAMES = (', '    )')
warm_chunk = '    WARM_TABLE_CHUNK_SIZE = 1024\n    INIT_WARM_TABLE_STEPS = 50\n    WARM_TABLE_STEPS_PER_MOVE = 5'
weights = extract_block(cur_code, '    WEIGHTS = (', '    )')
book_lines = extract_block(cur_code, '    BOOK_LINES = (', '    )')

exp_lines = exp_code.split('\n')
exp_body = []
in_class = False
skip_log_profile = False

for line in exp_lines:
    if line.startswith('class MyPlayer(BasePlayer):'):
        in_class = True
        exp_body.append(line)
        exp_body.append(pattern_indexes)
        exp_body.append(pattern_sizes)
        exp_body.append(active_patterns)
        exp_body.append(precomputed)
        exp_body.append(init_precomputed)
        exp_body.append(warm_patterns)
        exp_body.append(warm_chunk)
        exp_body.append(weights)
        exp_body.append(book_lines)
        continue
    if in_class:
        if 'WEIGHTS = WEIGHTS' in line: continue
        if 'BOOK_LINES = BOOK_LINES' in line: continue
        if 'PATTERN_INDEXES = PATTERN_INDEXES' in line: continue
        if 'PATTERN_SIZES = PATTERN_SIZES' in line: continue
        if 'ACTIVE_PATTERN_NAMES = ACTIVE_PATTERN_NAMES' in line: continue
        if 'PRECOMPUTED_PATTERN_NAMES = PRECOMPUTED_PATTERN_NAMES' in line: continue
        if 'WARM_PATTERN_NAMES = WARM_PATTERN_NAMES' in line: continue
        if 'INIT_PRECOMPUTED_PATTERN_NAMES = INIT_PRECOMPUTED_PATTERN_NAMES' in line: continue
        if 'INIT_WARM_TABLE_STEPS = INIT_WARM_TABLE_STEPS' in line: continue
        if 'WARM_TABLE_CHUNK_SIZE = WARM_TABLE_CHUNK_SIZE' in line: continue
        if 'WARM_TABLE_STEPS_PER_MOVE = WARM_TABLE_STEPS_PER_MOVE' in line: continue
        
        # Remove getattr and profiling logic
        if 'def _log_profile' in line:
            skip_log_profile = True
            continue
        if skip_log_profile:
            if line.startswith('    ') and not line.startswith('        '):
                skip_log_profile = False
            else:
                continue
                
        # Remove time module references
        if 'time.perf_counter()' in line: continue
        if 'import time' in line: continue
        if 'MyPlayer._accum' in line: continue
        if 'self._log_profile' in line: continue
        
        exp_body.append(line)

new_code = '\n'.join(exp_body)

# Fix SEARCH_HASH_TABLE_SIZE
new_code = new_code.replace('    SEARCH_HASH_TABLE_SIZE = 16384', '    SEARCH_HASH_TABLE_SIZE = 131072')

# Fix SEARCH_DEPTH
new_code = new_code.replace('    SEARCH_DEPTH = 6', '    SEARCH_DEPTH = 7')

# Fix 6-stone flip
new_code = new_code.replace(
    'c |= opp & ((c & NOT_A) >> 9); c |= opp & ((c & NOT_A) >> 9); c |= opp & ((c & NOT_A) >> 9); c |= opp & ((c & NOT_A) >> 9)',
    'c |= opp & ((c & NOT_A) >> 9); c |= opp & ((c & NOT_A) >> 9); c |= opp & ((c & NOT_A) >> 9); c |= opp & ((c & NOT_A) >> 9); c |= opp & ((c & NOT_A) >> 9)'
)
new_code = new_code.replace(
    'c |= opp & (c >> 8); c |= opp & (c >> 8); c |= opp & (c >> 8); c |= opp & (c >> 8)',
    'c |= opp & (c >> 8); c |= opp & (c >> 8); c |= opp & (c >> 8); c |= opp & (c >> 8); c |= opp & (c >> 8)'
)
new_code = new_code.replace(
    'c |= opp & ((c & NOT_H) >> 7); c |= opp & ((c & NOT_H) >> 7); c |= opp & ((c & NOT_H) >> 7); c |= opp & ((c & NOT_H) >> 7)',
    'c |= opp & ((c & NOT_H) >> 7); c |= opp & ((c & NOT_H) >> 7); c |= opp & ((c & NOT_H) >> 7); c |= opp & ((c & NOT_H) >> 7); c |= opp & ((c & NOT_H) >> 7)'
)
new_code = new_code.replace(
    'c |= opp & ((c & NOT_A) >> 1); c |= opp & ((c & NOT_A) >> 1); c |= opp & ((c & NOT_A) >> 1); c |= opp & ((c & NOT_A) >> 1)',
    'c |= opp & ((c & NOT_A) >> 1); c |= opp & ((c & NOT_A) >> 1); c |= opp & ((c & NOT_A) >> 1); c |= opp & ((c & NOT_A) >> 1); c |= opp & ((c & NOT_A) >> 1)'
)
new_code = new_code.replace(
    'c |= opp & ((c & NOT_H) << 1); c |= opp & ((c & NOT_H) << 1); c |= opp & ((c & NOT_H) << 1); c |= opp & ((c & NOT_H) << 1)',
    'c |= opp & ((c & NOT_H) << 1); c |= opp & ((c & NOT_H) << 1); c |= opp & ((c & NOT_H) << 1); c |= opp & ((c & NOT_H) << 1); c |= opp & ((c & NOT_H) << 1)'
)
new_code = new_code.replace(
    'c |= opp & ((c & NOT_A) << 7); c |= opp & ((c & NOT_A) << 7); c |= opp & ((c & NOT_A) << 7); c |= opp & ((c & NOT_A) << 7)',
    'c |= opp & ((c & NOT_A) << 7); c |= opp & ((c & NOT_A) << 7); c |= opp & ((c & NOT_A) << 7); c |= opp & ((c & NOT_A) << 7); c |= opp & ((c & NOT_A) << 7)'
)
new_code = new_code.replace(
    'c |= opp & (c << 8); c |= opp & (c << 8); c |= opp & (c << 8); c |= opp & (c << 8)',
    'c |= opp & (c << 8); c |= opp & (c << 8); c |= opp & (c << 8); c |= opp & (c << 8); c |= opp & (c << 8)'
)
new_code = new_code.replace(
    'c |= opp & ((c & NOT_H) << 9); c |= opp & ((c & NOT_H) << 9); c |= opp & ((c & NOT_H) << 9); c |= opp & ((c & NOT_H) << 9)',
    'c |= opp & ((c & NOT_H) << 9); c |= opp & ((c & NOT_H) << 9); c |= opp & ((c & NOT_H) << 9); c |= opp & ((c & NOT_H) << 9); c |= opp & ((c & NOT_H) << 9)'
)

# Fix ProbCut bounds
probcut_bug = '''        if estimate + margin >= beta:
            high = beta + margin
            high_score = self._negascout(
                state, pattern_keys, probe_depth, current_color, high - 0.001, high, allow_probcut=False
            )
            if high_score >= high:
                return beta

        if estimate - margin <= alpha:
            low = alpha - margin
            low_score = self._negascout(
                state, pattern_keys, probe_depth, current_color, low, low + 0.001, allow_probcut=False
            )
            if low_score <= low:
                return alpha'''

probcut_fix = '''        if beta < float("inf") and estimate + margin >= beta:
            high = beta + margin
            high_score = self._negascout(
                state, pattern_keys, probe_depth, current_color, high - 0.001, high, allow_probcut=False
            )
            if high_score >= high:
                return beta

        if alpha > float("-inf") and estimate - margin <= alpha:
            low = alpha - margin
            low_score = self._negascout(
                state, pattern_keys, probe_depth, current_color, low, low + 0.001, allow_probcut=False
            )
            if low_score <= low:
                return alpha'''

new_code = new_code.replace(probcut_bug, probcut_fix)

# Fix book return type
book_bug = '''        book_move = self._book_move_bits(state)
        if book_move is not None and self._move_to_pos(book_move) in moves:
            return book_move'''
book_fix = '''        book_move = self._book_move_bits(state)
        if book_move is not None and self._move_to_pos(book_move) in moves:
            return self._pos_to_move(self._move_to_pos(book_move))'''
new_code = new_code.replace(book_bug, book_fix)

with open('players/current.py', 'w') as f:
    f.write(new_code)
