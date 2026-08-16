# 棋譜データ構成メモ

## 基本方針

20,000局程度作るなら、1種類の相手・1種類の設定だけで作らない。
同じAI同士や固定設定だけだと、似た局面が増えて学習データが偏る。

おすすめは、強い棋譜を中心にしつつ、少し崩れた棋譜も混ぜること。

```text
70%: 先生AI・上級AI・強い自作AIとの対戦
20%: 自作players同士、または深さ違いの自作AI同士
10%: 序盤ランダム性を強めた対戦
```

## 誰と戦わせるべきか

両方使う。

先生が用意しているAIや `AdvancedPlayer` との対戦は、データの基準品質を上げやすい。
自作 `players/` 同士の対戦は、自分のAIが実際に出しやすい局面を増やせる。

ただし、自作AI同士だけで20,000局作るのは避ける。
自分の評価関数や探索の癖に寄りすぎるため。

先生が用意した強いAIとして、Webシステムの対戦ページで使える `TA_Player_v2` がある。

```text
TA_Player_v2 ID: qZ61Xg3cdvQevP66EEVq
```

このIDはWebシステム用なので、ローカルの `othellopy` には直接指定できない。
Webシステムから棋譜を出力できる場合は、`TA_Player_v2` との棋譜も学習データに混ぜる。

自動で対戦を作る場合は、次のメモを見る。

```text
my_othello_ai/pattern_eval/docs/WEB_TA_PLAYER_AUTOMATION.md
```

## ランダム性

完全ランダム手を大量に入れない。
弱すぎる棋譜が増えると、学習が悪い手も真似しやすくなる。

おすすめは序盤だけランダムにする。

```text
序盤 6〜10手: 合法手からランダム、または上位候補からランダム
中盤: ほぼ通常AI
終盤: 通常AI、できれば最善寄り
```

まずは `RANDOM_OPENING_PLIES=8` くらいでよい。
棋譜がまだ似るなら 10〜12 に増やす。
弱くなりすぎるなら 4〜6 に減らす。

## 20,000局の具体構成

```text
合計 20,000局

1. random_opening/current_random_r4.py vs TA_Player_v2: 2,500局
2. random_opening/current_random_r8.py vs TA_Player_v2: 2,500局
3. random_opening/current_random_r10.py vs TA_Player_v2: 1,000局
4. current.py vs AdvancedPlayer: 4,000局
5. current.py vs baselines/my_book_ab.py: 4,000局
6. current.py vs baselines/my_book.py: 2,000局
7. current.py vs baselines/my_base.py: 2,000局
8. current.py vs experiments/exp_019_endgame_exact_search.py: 1,000局
9. current.py vs experiments/exp_029_endgame13_incremental_keys.py: 1,000局
```

黒番・白番はなるべく半分ずつにする。
例えば8,000局なら、自分側Playerを黒番4,000局、白番4,000局にする。

## 自分AIの中身

`players/current.py` 本体は基本的に変更しない。
提出候補の強さを壊さないため、ランダム性は対戦用ラッパー側で入れる。

Webシステムに提出するランダム序盤版は、次に置く。

```text
my_othello_ai/pattern_eval/players/random_opening/
  current_random_r4.py
  current_random_r8.py
  current_random_r10.py
```

棋譜生成時の `current.py` は次の設定にする。

```text
序盤: ランダムあり
中盤: current.py の通常探索
終盤: current.py の通常探索、時間切れなし
```

具体的には、序盤だけ合法手からランダムに選ぶ。

```text
通常生成: RANDOM_OPENING_PLIES=8
多様性を増やす生成: RANDOM_OPENING_PLIES=10
品質重視の生成: RANDOM_OPENING_PLIES=4〜6
```

まずは20,000局のうち、次の比率にする。

```text
14,000局: RANDOM_OPENING_PLIES=8
4,000局: RANDOM_OPENING_PLIES=4
2,000局: RANDOM_OPENING_PLIES=10
```

完全ランダムAI同士の棋譜は入れない。
ランダムにするのは序盤だけにする。

## 対戦相手の考え方

`AdvancedPlayer` や先生AIは、棋譜の品質を上げるために多めに使う。
自作 `players/` は、自分のAIが出しやすい局面を増やすために混ぜる。

おすすめの優先順位は次の通り。

```text
優先1: TA_Player_v2
優先2: AdvancedPlayer / 先生AI
優先3: baselines/my_book_ab.py
優先4: current.py に近い強さの experiments
優先5: my_book.py / my_base.py
```

弱い相手は入れすぎない。
`my_base.py` などは「相手のミスを咎める局面」を作る目的で少量だけ使う。

## 生成バッチ例

一度に20,000局を作らず、設定ごとに分けて保存する。

```text
batch_ta_v2_random_6000/
  current_random_r4.py vs TA_Player_v2: 2,500局
  current_random_r8.py vs TA_Player_v2: 2,500局
  current_random_r10.py vs TA_Player_v2: 1,000局
  opponent_id=qZ61Xg3cdvQevP66EEVq

batch_advanced_r8_4000/
  current.py vs AdvancedPlayer
  4,000局
  RANDOM_OPENING_PLIES=8

batch_book_ab_r8_4000/
  current.py vs baselines/my_book_ab.py
  4,000局
  RANDOM_OPENING_PLIES=8

batch_book_r4_2000/
  current.py vs baselines/my_book.py
  2,000局
  RANDOM_OPENING_PLIES=4

batch_base_r4_2000/
  current.py vs baselines/my_base.py
  2,000局
  RANDOM_OPENING_PLIES=4

batch_exp019_r10_1000/
  current.py vs experiments/exp_019_endgame_exact_search.py
  1,000局
  RANDOM_OPENING_PLIES=10

batch_exp029_r10_1000/
  current.py vs experiments/exp_029_endgame13_incremental_keys.py
  1,000局
  RANDOM_OPENING_PLIES=10
```

各バッチで `summary.json` を残し、あとで勝敗・途中終了・平均手数を確認する。

## 偏りの確認

棋譜が生成されたら、勝率だけで判断しない。
次の項目を確認する。

```text
1. 色の偏り
   黒番・白番がほぼ半分か。

2. 勝率の偏り
   current.py が勝ちすぎ、負けすぎになっていないか。
   目安として、全体で勝率30〜70%くらいなら使いやすい。
   90%以上勝つ棋譜や10%以下しか勝てない棋譜が多すぎると偏る。

3. 手数の偏り
   途中終了や短すぎる棋譜が多くないか。
   40手未満が多いバッチは要確認。

4. 序盤の偏り
   最初の8〜12手が同じ形ばかりになっていないか。
   同じ序盤文字列が大量に重複していたら、乱数seedやランダム手数を変える。

5. 棋譜の重複
   `records.txt` 内で同一行が多くないか。
   重複が多い場合は相手・seed・RANDOM_OPENING_PLIESを変える。

6. 相手の偏り
   TA_Player_v2 だけ、AdvancedPlayer だけ、などに寄せすぎない。
   強い相手を中心にしつつ、別タイプのAIも混ぜる。
```

勝率は確認するが、目的は「勝てる棋譜を集めること」ではない。
学習用には、勝ち・負け・接戦・不利局面がある程度混ざっている方がよい。

## 保存場所

学習用に使う棋譜は、他の評価ログと混ぜない。

```text
my_othello_ai/pattern_eval/generated_kihu/for_training/
  vs_AdvancedPlayer_10games/
  batch_20000/
```

棋譜本体は `records.txt` に1行1局で保存する。
設定や勝敗は `summary.json` に保存する。

## 実行コマンド

棋譜生成では `-test` を付ける。
時間切れで途中終了した棋譜を作らないため、`MOVE_TIMEOUT_SECONDS=none` で実行する。

```bash
cd /home/nakai/Othello_AI
bash my_othello_ai/pattern_eval/scripts/run_kihu_generation.sh -test current.py 10
```

相手を選んで棋譜生成する場合は、次を使う。
第1引数が自分側Player、第2引数が相手、第3引数が局数。

```bash
cd /home/nakai/Othello_AI/my_othello_ai/pattern_eval
bash scripts/run_kihu_vs_player.sh -test current.py AdvancedPlayer 10
bash scripts/run_kihu_vs_player.sh -test current.py exp_030_rounded_weights_5digits.py 10
bash scripts/run_kihu_vs_player.sh -test random_opening/current_random_r4.py exp_038_init48s_triangle_warmup.py 10
```

Webシステム上の `TA_Player_v2` と自動対戦を作る場合は、ログイン後の短時間トークンを環境変数に入れて実行する。

```bash
cd /home/nakai/Othello_AI
export OTHELLOPY_AUTH_TOKEN="ログイン後に取得した短時間トークン"
bash my_othello_ai/pattern_eval/scripts/run_web_ta_matches.sh 自分のPlayerID 10
```

## 注意

- 途中終了、時間切れ、反則の棋譜は学習に入れない。
- 60手未満でもパスで正常終了することはあるが、短すぎる棋譜は確認する。
- 同じ乱数 seed だけで大量生成しない。
- 生成設定ごとにフォルダを分ける。
