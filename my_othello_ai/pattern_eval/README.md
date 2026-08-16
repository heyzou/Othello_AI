# Pattern Eval Shared Notebook

`common/pattern_eval_common.ipynb` は MyPlayer 以外のセルを共通化した評価用ノートブックです。

MyPlayer の実装は `players/` に分けています。

```text
players/
  current.py      # 今の提出候補
  baselines/      # 基準版
  experiments/    # 実験版
  archived/       # 使わなくなった退避先
  MANIFEST.md     # 実験内容の対応表

profiles/
  current/         # current.py の next_move ログ
  baselines/       # 基準版の next_move ログ
  experiments/     # 実験版の next_move ログ

generated_kihu/
  vs_AdvancedPlayer/
    current/       # current.py の棋譜
    baselines/     # 基準版の棋譜
    experiments/   # 実験版の棋譜
```

`players/*.py` は提出時に貼りやすいように、`class MyPlayer(BasePlayer):` から始めています。
必要な import は共通ノートブック側の MyPlayer 読み込みセルに置いています。

使う実装を変えるときは、`pattern_eval_common.ipynb` の MyPlayer 読み込みセルにある `MYPLAYER_FILE` だけ変更してください。

```python
MYPLAYER_FILE = "../players/current.py"
```

シェルから実行する場合は次のようにします。第2引数は片側ごとの対戦回数です。
`1` を指定すると、黒番1局・白番1局を実行します。

```bash
./scripts/run_pattern_eval.sh current.py 1
./scripts/run_pattern_eval.sh baselines/my_book_ab.py 1
./scripts/run_pattern_eval.sh experiments/exp_003_weight_order_search_hash.py 1
```

ファイル名が長くなりそうな実験は、`experiments/exp_XXX_short_name.py` に置き、詳細は `players/MANIFEST.md` に書いてください。
`next_move_profile.txt` などの計測ログは、対応する `profiles/` 配下に出力されます。
対戦棋譜は、対応する `generated_kihu/vs_*/` 配下に出力されます。

Webシステムの `TA_Player_v2` と対戦を作る場合は、次を見てください。

```text
docs/WEB_TA_PLAYER_AUTOMATION.md
```

棋譜生成で相手を選ぶ場合は次を使います。

```bash
./scripts/run_kihu_vs_player.sh -test current.py AdvancedPlayer 10
./scripts/run_kihu_vs_player.sh -test current.py exp_030_rounded_weights_5digits.py 10
```
