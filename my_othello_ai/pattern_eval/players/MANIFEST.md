# MyPlayer Implementations

`current.py` is the current submission candidate. Baseline files keep stable reference versions, and experiment files use short IDs so feature names do not keep growing.

Profile logs are stored outside `players/`:

| player type | profile directory |
|---|---|
| current | `../profiles/current/` |
| baseline | `../profiles/baselines/` |
| experiment | `../profiles/experiments/` |

Game records are stored in `../generated_kihu/vs_<opponent>/<player type>/`.

| file | base | features |
|---|---|---|
| `current.py` | exp_038 | bitboard_search, 8_pattern_weights, 8_active_patterns, rounded_weights, depth6, state_eval_cache, incremental_pattern_keys, endgame_exact_search, init_48s_triangle_chunks, incremental_remaining_table_warmup |
| `baselines/my_base.py` | base | pattern evaluation |
| `baselines/my_book.py` | base | opening book |
| `baselines/my_book_ab.py` | book | alpha-beta endgame search |
| `experiments/exp_001_add_hash.py` | book_ab | additional hash |
| `experiments/exp_002_weight_order.py` | book_ab | weight-based move ordering |
| `experiments/exp_003_weight_order_search_hash.py` | book_ab | weight_order, search_hash |
| `experiments/exp_004_strong_weight_search_hash.py` | book_ab | strong_weight, search_hash |
| `experiments/exp_005_qweight_search_hash.py` | book_ab | qweight, search_hash |
| `experiments/exp_006_precomputed_eval_search_hash.py` | book_ab | precomputed_eval, search_hash |
| `experiments/exp_007_precomputed_eval_addkey_cache.py` | book_ab | precomputed_eval, addkey_cache |
| `experiments/exp_008_no_eval_sort_endgame.py` | book_ab | no_eval_sort_endgame |
| `experiments/exp_009_legal_moves_hash.py` | current | legal_moves_hash, get_moves_profile |
| `experiments/exp_010_bitboard.py` | exp_009 | bitboard_search, legal_moves_hash |
| `experiments/exp_011_profile_hotspots.py` | exp_010 | hotspot_profile |
| `experiments/exp_012_additional_key_cache.py` | exp_011 | additional_key_cache, no_open_getattr |
| `experiments/exp_013_fast_surround.py` | exp_012 | bitshift_surround_counts |
| `experiments/exp_014_mobility_mask.py` | exp_013 | mobility_bit_count |
| `experiments/exp_015_fast_pattern_key.py` | exp_014 | fast_pattern_key |
| `experiments/exp_016_mobility_cache.py` | exp_015 | mobility_cache |
| `experiments/exp_017_precomputed_value_tables.py` | exp_016 | precomputed_value_tables |
| `experiments/exp_018_legal_mask_cache.py` | exp_017 | legal_move_mask_cache |
| `experiments/exp_019_endgame_exact_search.py` | exp_018 | endgame_exact_search, fastest_first_ordering |
| `experiments/exp_020_8patterns.py` | exp_019 | 8_pattern_weights |
| `experiments/exp_021_direct_pattern_value.py` | exp_020 | inline_direct_pattern_value |
| `experiments/exp_022_eval_cache.py` | exp_021 | state_eval_cache |
| `experiments/exp_023_6patterns_eval_cache.py` | exp_022 | 6_active_patterns |
| `experiments/exp_024_rounded_weights_init_tables.py` | exp_023 | rounded_weights, init_pattern_tables, depth6 |
| `experiments/exp_025_eval_cache_262144.py` | exp_023 | eval_cache_262144 |
| `experiments/exp_026_incremental_pattern_keys.py` | exp_025 | incremental_pattern_keys |
| `experiments/exp_027_8patterns_incremental_keys.py` | exp_026 | 8_active_patterns |
| `experiments/exp_028_endgame12_incremental_keys.py` | exp_027 | endgame_exact_empty12 |
| `experiments/exp_029_endgame13_incremental_keys.py` | exp_028 | endgame_exact_empty13 |
| `experiments/exp_030_rounded_weights_5digits.py` | current | rounded_weights_5digits, init_time_check |
| `experiments/exp_031_incremental_table_warmup.py` | current | lazy_init, incremental_pattern_table_warmup |
| `experiments/exp_032_init5s_table_warmup.py` | exp_031 | init_edge_tables, incremental_remaining_table_warmup |
| `experiments/exp_033_init3s_table_warmup.py` | exp_032 | shorter_init_edge_edge2x, incremental_remaining_table_warmup |
| `experiments/exp_034_init3s_plus_triangle_warmup.py` | exp_033 | init_edge_edge2x_plus_triangle_chunks, incremental_remaining_table_warmup |
| `experiments/exp_035_init_more_triangle_warmup.py` | exp_034 | init_more_triangle_chunks, incremental_remaining_table_warmup |
| `experiments/exp_036_init_even_more_triangle_warmup.py` | exp_035 | init_even_more_triangle_chunks, incremental_remaining_table_warmup |
| `experiments/exp_037_init45s_triangle_warmup.py` | exp_036 | init_45s_triangle_chunks, incremental_remaining_table_warmup |
| `experiments/exp_038_init48s_triangle_warmup.py` | exp_037 | init_48s_triangle_chunks, incremental_remaining_table_warmup |
| `experiments/exp_039_corner_x_penalty.py` | current | corner_empty_x_square_penalty, x_square_move_order_penalty |
| `experiments/exp_040_depth7_fast_probcut.py` | current | depth7, larger_search_hash, stronger_probcut, root_late_move_reduction |
