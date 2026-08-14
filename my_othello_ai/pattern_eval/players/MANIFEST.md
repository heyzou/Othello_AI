# MyPlayer Implementations

`current.py` is the current submission candidate. Baseline files keep stable reference versions, and experiment files use short IDs so feature names do not keep growing.

Profile logs are stored outside `players/`:

| player type | profile directory |
|---|---|
| current | `../profiles/current/` |
| baseline | `../profiles/baselines/` |
| experiment | `../profiles/experiments/` |

Game records are stored in `../generated_kihu/vs_<opponent>/<player type>/`.

| file | old name | base | features |
|---|---|---|---|
| `current.py` | `my_book_ab_weight_order_search_hash.py` | book_ab | weight_order, search_hash |
| `baselines/my_base.py` | `my_base.py` | base | pattern evaluation |
| `baselines/my_book.py` | `my_book.py` | base | opening book |
| `baselines/my_book_ab.py` | `my_book_ab.py` | book | alpha-beta endgame search |
| `experiments/exp_001_add_hash.py` | `my_book_ab_add_hash.py` | book_ab | additional hash |
| `experiments/exp_002_weight_order.py` | `my_book_ab_weight_order.py` | book_ab | weight-based move ordering |
| `experiments/exp_003_weight_order_search_hash.py` | `my_book_ab_weight_order_search_hash.py` | book_ab | weight_order, search_hash |
| `experiments/exp_004_strong_weight_search_hash.py` | `my_book_ab_strong_weight_search_hash.py` | book_ab | strong_weight, search_hash |
| `experiments/exp_005_qweight_search_hash.py` | `my_book_ab_qweight_search_hash.py` | book_ab | qweight, search_hash |
| `experiments/exp_006_precomputed_eval_search_hash.py` | `my_book_ab_precomputed_eval_search_hash.py` | book_ab | precomputed_eval, search_hash |
| `experiments/exp_007_precomputed_eval_addkey_cache.py` | `my_book_ab_precomputed_eval_addkey_cache.py` | book_ab | precomputed_eval, addkey_cache |
| `experiments/exp_008_no_eval_sort_endgame.py` | `my_book_ab_no_eval_sort_endgame.py` | book_ab | no_eval_sort_endgame |
