# Random Opening Players

`current.py` を元にした、棋譜生成用の派生Player。
提出候補の `players/current.py` 本体は変更しない。

```text
current_random_r4.py   最初の4手だけ合法手からランダム
current_random_r8.py   最初の8手だけ合法手からランダム
current_random_r10.py  最初の10手だけ合法手からランダム
```

序盤ランダム後は、`current.py` と同じ探索・評価で着手する。
TA_Player_v2との棋譜生成では、これらをWebシステムに別Playerとして提出し、それぞれのPlayer IDで対戦を作る。
