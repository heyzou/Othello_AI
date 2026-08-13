# Pattern Eval Shared Notebook

`common/pattern_eval_common.ipynb` は MyPlayer 以外のセルを共通化した評価用ノートブックです。

MyPlayer の実装は `players/` に分けています。

- `players/myplayer_base.py`: 定石なしの元のパターン評価版
- `players/myplayer_with_book.py`: 定石確認つきのパターン評価版

使う実装を変えるときは、`pattern_eval_common.ipynb` の MyPlayer 読み込みセルにある `MYPLAYER_FILE` だけ変更してください。

```python
MYPLAYER_FILE = "../players/myplayer_with_book.py"
```

これで、ノートブック全体をコピーせずに MyPlayer だけ差し替えて評価できます。

シェルから実行する場合は次のようにします。第2引数は片側ごとの対戦回数です。
`1` を指定すると、黒番1局・白番1局を実行します。

```bash
./run_pattern_eval.sh myplayer_with_book.py 1
```
