import re

with open('players/experiments/exp_051_060/exp_051_fast_eval.py', 'r') as f:
    code = f.read()

# Add counters to MyPlayer class
code = re.sub(
    r'    _accum_eval_hit_time: float = 0\.0',
    r'    _accum_eval_hit_time: float = 0.0\n    _cache_stats = {"EVAL": [0, 0], "MOBILITY": [0, 0], "ADD_KEY": [0, 0], "LEGAL_MOVES": [0, 0], "LEGAL_MASK": [0, 0], "TT_HASH": [0, 0]}',
    code
)

# EVAL_CACHE
code = re.sub(
    r'        t_eval_start = time\.perf_counter\(\)\n        cached = MyPlayer\.EVAL_CACHE\.get\(state\)\n        if cached is not None:\n            MyPlayer\._accum_eval_hit_time \+= time\.perf_counter\(\) - t_eval_start\n            MyPlayer\._accum_eval_time \+= time\.perf_counter\(\) - t_eval_start\n            return cached',
    r'        t_eval_start = time.perf_counter()\n        cached = MyPlayer.EVAL_CACHE.get(state)\n        if cached is not None:\n            MyPlayer._cache_stats["EVAL"][0] += 1\n            MyPlayer._accum_eval_hit_time += time.perf_counter() - t_eval_start\n            MyPlayer._accum_eval_time += time.perf_counter() - t_eval_start\n            return cached\n        MyPlayer._cache_stats["EVAL"][1] += 1',
    code
)

# ADDITIONAL_KEY_CACHE
code = re.sub(
    r'    def _additional_key_bits\(self, state: tuple\[int, int\]\) -> int:\n        cached = MyPlayer\.ADDITIONAL_KEY_CACHE\.get\(state\)\n        if cached is not None:\n            return cached',
    r'    def _additional_key_bits(self, state: tuple[int, int]) -> int:\n        cached = MyPlayer.ADDITIONAL_KEY_CACHE.get(state)\n        if cached is not None:\n            MyPlayer._cache_stats["ADD_KEY"][0] += 1\n            return cached\n        MyPlayer._cache_stats["ADD_KEY"][1] += 1',
    code
)

# MOBILITY_CACHE
code = re.sub(
    r'    def _mobility_diff_bits\(self, state: tuple\[int, int\]\) -> int:\n        cached = MyPlayer\.MOBILITY_CACHE\.get\(state\)\n        if cached is not None:\n            return cached',
    r'    def _mobility_diff_bits(self, state: tuple[int, int]) -> int:\n        cached = MyPlayer.MOBILITY_CACHE.get(state)\n        if cached is not None:\n            MyPlayer._cache_stats["MOBILITY"][0] += 1\n            return cached\n        MyPlayer._cache_stats["MOBILITY"][1] += 1',
    code
)

# LEGAL_MOVES_CACHE
code = re.sub(
    r'        cached = MyPlayer\.LEGAL_MOVES_CACHE\.get\(key\)\n        if cached is not None:\n            MyPlayer\._accum_search_movegen_time \+= time\.perf_counter\(\) - t0\n            return cached',
    r'        cached = MyPlayer.LEGAL_MOVES_CACHE.get(key)\n        if cached is not None:\n            MyPlayer._cache_stats["LEGAL_MOVES"][0] += 1\n            MyPlayer._accum_search_movegen_time += time.perf_counter() - t0\n            return cached\n        MyPlayer._cache_stats["LEGAL_MOVES"][1] += 1',
    code
)

# LEGAL_MOVE_MASK_CACHE
code = re.sub(
    r'        cached = MyPlayer\.LEGAL_MOVE_MASK_CACHE\.get\(key\)\n        if cached is not None:\n            return cached',
    r'        cached = MyPlayer.LEGAL_MOVE_MASK_CACHE.get(key)\n        if cached is not None:\n            MyPlayer._cache_stats["LEGAL_MASK"][0] += 1\n            return cached\n        MyPlayer._cache_stats["LEGAL_MASK"][1] += 1',
    code
)

# TT_HASH (SEARCH_HASH_TABLE)
code = re.sub(
    r'        entry = cls\.SEARCH_HASH_TABLE\[cls\._search_hash_index\(key\)\]\n        if entry is None:\n            return None\n        entry_key, lower, upper, entry_depth, best_move = entry\n        if entry_key != key or entry_depth < depth:\n            return None',
    r'        entry = cls.SEARCH_HASH_TABLE[cls._search_hash_index(key)]\n        if entry is None:\n            cls._cache_stats["TT_HASH"][1] += 1\n            return None\n        entry_key, lower, upper, entry_depth, best_move = entry\n        if entry_key != key or entry_depth < depth:\n            cls._cache_stats["TT_HASH"][1] += 1\n            return None',
    code
)
code = re.sub(
    r'        if lower >= beta:\n            cls\.SEARCH_HASH_GET_COUNT \+= 1\n            return lower\n        if upper <= alpha:\n            cls\.SEARCH_HASH_GET_COUNT \+= 1\n            return upper\n        if lower == upper:\n            cls\.SEARCH_HASH_GET_COUNT \+= 1\n            return lower\n        return None',
    r'        if lower >= beta:\n            cls._cache_stats["TT_HASH"][0] += 1\n            return lower\n        if upper <= alpha:\n            cls._cache_stats["TT_HASH"][0] += 1\n            return upper\n        if lower == upper:\n            cls._cache_stats["TT_HASH"][0] += 1\n            return lower\n        cls._cache_stats["TT_HASH"][1] += 1\n        return None',
    code
)

# Save JSON of stats at end of log
code = re.sub(
    r'        print\(log_str\)',
    r'        print(log_str)\n        if actual_turn in (21, 32):\n            import json\n            with open(f"cache_stats_{actual_turn}.json", "w") as f:\n                json.dump(MyPlayer._cache_stats, f)',
    code
)

with open('players/experiments/exp_051_060/exp_051_fast_eval.py', 'w') as f:
    f.write(code)

print("Instrumented!")
