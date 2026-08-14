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
| `current.py` | exp_014 | bitboard_search, additional_key_cache, fast_surround, mobility_bit_count |
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
