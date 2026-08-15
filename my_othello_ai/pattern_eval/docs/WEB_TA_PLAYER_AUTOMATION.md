# TA_Player_v2 自動対戦メモ

## 結論

`TA_Player_v2` はWebシステムの対戦APIで使える。

```text
TA_Player_v2 ID: qZ61Xg3cdvQevP66EEVq
```

ただしローカルの `othellopy` から直接呼ぶのではなく、Webシステムにログインした状態の認証トークンが必要。
パスワードをスクリプトに保存しない。

## 実行コマンド

自分の提出済みPlayer IDを指定して実行する。
黒番・白番はスクリプト側で交互に入れ替える。

```bash
cd /home/nakai/Othello_AI
bash my_othello_ai/pattern_eval/scripts/run_web_ta_matches.sh 自分のPlayerID 10
```

トークンは次のファイルに貼り付ける。
このフォルダは `.gitignore` に入れている。

```text
my_othello_ai/pattern_eval/secrets/othellopy_token.env
```

書き方:

```bash
OTHELLOPY_AUTH_TOKEN="eyJ..."
```

TA_Player_v2 と6,000局作る場合は、`players/random_opening/` の3種類をWebに別Playerとして提出し、それぞれのIDで分けて作る。

```bash
cd /home/nakai/Othello_AI

bash my_othello_ai/pattern_eval/scripts/run_web_ta_matches.sh current_random_r4のPlayerID 2500
bash my_othello_ai/pattern_eval/scripts/run_web_ta_matches.sh current_random_r8のPlayerID 2500
bash my_othello_ai/pattern_eval/scripts/run_web_ta_matches.sh current_random_r10のPlayerID 1000
```

出力先:

```text
my_othello_ai/pattern_eval/generated_kihu/for_training/vs_TA_Player_v2_web/YYYYMMDD_HHMMSS/
  requests.jsonl
  created_matches.jsonl
  polled_matches.jsonl
  summary.json
```

## トークンの扱い

- `OTHELLOPY_AUTH_TOKEN` はGitに保存しない。
- `.env` にも残さない方が安全。
- トークンは短時間だけ使い、不要になったらターミナルを閉じる。
- パスワードをスクリプトやNotebookに書かない。

## 必要な値の取り方

自分のPlayer IDは、Webシステムで提出済みPlayerの詳細や対戦ページの選択欄から確認する。

`OTHELLOPY_AUTH_TOKEN` は、ログイン済みブラウザから短時間だけ使う値を取る。
一番分かりやすい方法は次の通り。

```text
1. https://othellopy.com にログインする。
2. ブラウザの開発者ツールを開く。
3. Network タブを開く。
4. 対戦ページで1局だけ手動で作る。
5. /api/matches のリクエストを選ぶ。
6. Request Headers の Authorization: Bearer ... を見る。
7. Bearer の後ろだけを OTHELLOPY_AUTH_TOKEN に入れる。
```

例:

```bash
export OTHELLOPY_AUTH_TOKEN="eyJ..."
```

この値はログイン権限そのものなので、人に送らない。

## まだ確認が必要なこと

対戦作成APIは確認済みだが、棋譜本文がどのJSONキーで返るかは、実際に1局作った後の `polled_matches.jsonl` を見る必要がある。
その形が分かれば、Webの結果JSONから `records.txt` へ変換する処理を追加する。
