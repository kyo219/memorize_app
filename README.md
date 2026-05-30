# memorize_app

ターミナルで遊ぶ、Naive な暗記アプリの Python 実装。

日本語を見て英訳を打ち込み、正誤を記録していく英作文クイズです。間違えた問題だけを復習したり、GPT に採点・解説してもらったり、間違えた問題をまとめた学習ノートを Markdown で出力したりできます。問題は手で追加でき、用途ごとに **データセット（問題プール）** を分けて遊べます。音声教材（mp3）から自分だけの問題集を作ることもできます。

> **問題データはこのリポジトリには含まれていません**（`data/` は `.gitignore` 対象）。まず [問題を手動で追加する](#問題を手動で追加する) で自分の問題を登録してから遊ぶ、という流れになります。

---

## 目次

- [必要なもの](#必要なもの)
- [セットアップ](#セットアップ)
- [まず遊んでみる（オフラインモード / APIキー不要）](#まず遊んでみるオフラインモード--apiキー不要)
- [データセット（問題プール）を分ける](#データセット問題プールを分ける)
- [問題を手動で追加する](#問題を手動で追加する)
- [クイズのモード一覧](#クイズのモード一覧)
  - [オフラインモード（自己採点）](#1-オフラインモード自己採点quiz_offlinepy)
  - [GPTモード（自動採点＋解説＋質問）](#2-gptモード自動採点解説質問answer_at_gptpy)
- [学習ノートを作る](#学習ノートを作る)
- [自分の教材を追加する（mp3から）](#自分の教材を追加するmp3から)
- [データの形式](#データの形式)
- [ディレクトリ構成](#ディレクトリ構成)

---

## 必要なもの

- Python 3.10 以上
- [uv](https://docs.astral.sh/uv/)（パッケージ管理・実行に使用）
- OpenAI API キー … **GPTモードと教材の自動生成にのみ必要**。オフラインモードだけなら不要です。

---

## セットアップ

```bash
# 1. リポジトリを取得して移動
git clone git@github.com:kyo219/memorize_app.git
cd memorize_app

# 2. 依存パッケージをインストール
uv sync
```

> **重要:** スクリプトは `data/...` などの相対パスを使うので、**必ずリポジトリのルート（`memorize_app/`）から実行**してください。

### （任意）OpenAI API キーの設定

GPTモードや教材の自動生成を使う場合は、リポジトリのルートに `config.py` を作成します。
このファイルは `.gitignore` 済みなので、コミットされる心配はありません。

```python
# config.py
OPENAI_API_KEY = "sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
```

API キーは [OpenAI のダッシュボード](https://platform.openai.com/api-keys) で取得できます。

---

## まず遊んでみる（オフラインモード / APIキー不要）

APIキー不要で完結する一番手軽な流れです。問題データは同梱されていないので、**まず問題を数問追加してから**プレイします。

```bash
# 1. 問題を追加（データセット名は Enter で default、日本語→英語を数問入れて空Enterで終了）
uv run python scripts/add_question.py

# 2. クイズを開始
uv run python scripts/quiz_offline.py
```

クイズ開始後の流れ:

1. **データセット名を入力**（そのまま Enter で `default`）
2. 出題パターンを選ぶ（`1`: 全問ランダム / `2`: 間違い＋未回答のみ）
3. 表示された日本語を見て、英訳を入力
4. 正解が表示されるので、自分で正誤を判定（`y` / `n`）
5. 成績が記録され、次の問題へ。`q` でいつでも終了

正誤の記録は選んだデータセットの CSV（例: `data/datasets/default.csv`）に自動保存され、次回 `2`（復習モード）で間違えた問題だけを出題できます。

---

## データセット（問題プール）を分ける

問題は `data/datasets/<名前>.csv` という単位（**データセット**）で管理されます。用途ごとに分けておけば、遊ぶときに切り替えられます。

- 名前を指定しないときの標準データセットが `default` です（最初に問題を追加すると作られます）。
- クイズ（オフライン／GPT）や問題追加の最初に **データセット名** を聞かれます。そのまま Enter で `default`、名前を入れればそのデータセットを対象にします。
- 存在しない名前を問題追加で指定すると、その名前で新しいデータセットが作られます。
- `data/` は `.gitignore` 対象なので、追加した問題は手元にのみ保存され、リポジトリには公開されません。

```
data/datasets/
├── default.csv   ← 標準（名前未指定のとき）
├── toeic.csv     ← 例: TOEIC用
└── travel.csv    ← 例: 旅行英会話用
```

---

## 問題を手動で追加する

日本語と英語（答え）を打ち込むだけで、問題をデータセットに追加できます。**APIキー不要。**

```bash
uv run python scripts/add_question.py
```

1. **データセット名を入力**（そのまま Enter で `default`／新しい名前なら新規作成）
2. 日本語 → 英語（答え）の順に入力すると、その都度 CSV に保存される
3. 日本語を空のまま Enter で終了

```
===== 問題の手動追加モード =====
データセット名を入力（そのままEnterで default）: travel
データセット 'travel' (data/datasets/travel.csv) に追加します。（新規作成）
日本語を空のまま Enter で終了します。

日本語: 搭乗券を見せていただけますか？
英語（答え）: May I see your boarding pass?
✓ 記録しました（このセッションで 1 問追加）

日本語:        ← 空Enterで終了
```

追加した問題は `source_file` が `manual` として記録され、そのまま各クイズで出題できます。

---

## クイズのモード一覧

どちらのスクリプトも、起動時にまず **データセット名**（そのまま Enter で `default`）を選び、続いて以下の2つの **出題パターン** を選べます。

| 選択 | 内容 |
|------|------|
| `1` | 全ての問題をランダムに出題 |
| `2` | 前回間違えた問題 ＋ まだ回答していない問題だけをランダムに出題（復習用） |

### 1. オフラインモード（自己採点）`quiz_offline.py`

```bash
uv run python scripts/quiz_offline.py
```

- **APIキー不要・無料**。正解は表示されるので、自分で正誤を判断します。
- 終了時にその回のセッション成績（正答率）が表示されます。

### 2. GPTモード（自動採点＋解説＋質問）`answer_at_gpt.py`

```bash
uv run python scripts/answer_at_gpt.py
```

> ⚠️ `config.py` に OpenAI API キーの設定が必要です（API 利用料がかかります）。

オフラインモードに加えて、GPT が次のことを自動で行います。

- **自動採点** … typo・省略形（`I'm`/`I am`）・大文字小文字の違いは無視し、文法・熟語を理解しているかで正誤判定
- **学習ポイントの抽出** … 各問題から「重要な熟語」「重要な文法」「理解が不足している点」を抽出し、CSV に保存（後述の学習ノートに使われます）
- **GPTへの質問モード** … 各問題のあと「続けますか？」のプロンプトで `gpt` と入力すると、その問題（日本語文・正解英訳）を文脈に渡したまま、文法や表現の違いについて対話形式で質問できます。`exit` で通常モードに戻ります。

```
続けますか？ Yes（そのままEnter）、No（Nと入力）、GPTに質問（gptと入力）: gpt

----- GPT質問モード -----
質問: なんで to spend なんですか？ for spending じゃダメ？
（GPTが文脈を踏まえて解説）
質問: exit
----- 通常モードに戻ります -----
```

---

## 学習ノートを作る

間違えた問題を、文法ポイント・熟語・例文ごとにまとめた Markdown ノートを生成します。
（熟語・文法の解説欄は **GPTモードでプレイしたとき** に埋まります。）

```bash
# これまでに間違えた問題すべてをまとめる
uv run python scripts/generate_study_notes.py --filter all_incorrect

# 今日間違えた問題だけをまとめる
uv run python scripts/generate_study_notes.py --filter today_incorrect
```

`study_notes_<filter>_<日付>.md` が生成されます（例: `study_notes_all_incorrect_2025-03-14.md`）。

| オプション | 説明 | デフォルト |
|-----------|------|-----------|
| `--filter` | `all_incorrect`（全ての間違い）／ `today_incorrect`（今日の間違い） | `all_incorrect` |
| `--output` | 出力ファイルパス | 自動生成 |
| `--dataset` | 対象のデータセット名 | `default` |
| `--table` | 入力 CSV のパスを直接指定（`--dataset` より優先） | なし |

```bash
# 例: travel データセットの間違いをまとめる
uv run python scripts/generate_study_notes.py --dataset travel
```

---

## 自分の教材を追加する（mp3から）

音声教材（mp3）から、自分だけの問題集を作れます。**どちらのステップも OpenAI API キーが必要です。**（手で1問ずつ追加したいだけなら [問題を手動で追加する](#問題を手動で追加する) を使ってください。）

```
mp3ファイル ──(Whisperで文字起こし)──▶ JSON ──(GPTで日英ペアに整形)──▶ CSV(問題集)
   ①scripts/mp3_to_json.py                  ②scripts/rawscripts_to_data.py
```

### ① mp3 → テキスト（文字起こし）

`scripts/mp3_to_json.py` の `INPUT_DIRS` に、mp3 を置いたディレクトリを指定します。

```python
# scripts/mp3_to_json.py
INPUT_DIRS = ["data/eibunpo/21177-1", "data/eibunpo/21177-2"]  # ← 自分のディレクトリに変更
```

```bash
uv run python scripts/mp3_to_json.py
```

各 mp3 を Whisper で日本語・英語それぞれ文字起こしし、`data/eibunpo/text/**/*.json` に保存します。

### ② テキスト → 問題集 CSV

```bash
uv run python scripts/rawscripts_to_data.py
```

`data/eibunpo/text` 以下の JSON を GPT で読み取り、日本語と英語を文単位のペアに整形して `data/eibunpo/dataframe/eibunpo_sentences.csv` に追記します。**処理済みのファイルはスキップ**されるので、教材を足して再実行すれば差分だけが追加されます。

> mp3 がなくても、`{"ja": "...", "en": "..."}` 形式の JSON を `data/eibunpo/text/` に置いて ② を実行すれば問題集を作れます。整った日英ペアの CSV を直接用意して同じカラム（後述）で置くのでも構いません。

> **データセットとして遊ぶには:** このパイプラインの出力 CSV を `data/datasets/<名前>.csv` にコピーすれば、その名前のデータセットとしてクイズで選べます。

---

## データの形式

データセットの CSV（`data/datasets/<名前>.csv`）のカラム:

| カラム | 説明 |
|--------|------|
| `row` | 通し番号 |
| `jp`（または `ja`） | 出題する日本語文 |
| `en` | 正解の英訳 |
| `source_file` | 出典（元 JSON のパス） |
| `wrong_cnt` / `correct_cnt` | 不正解・正解の累計回数 |
| `last_answered` | 最後に回答した日時 |
| `latest_label` | 直近の結果（`Correct` / `Incorrect`） |
| `note_idiom` / `note_grammar` / `note` | GPTモードで抽出した熟語・文法・理解不足点 |

`wrong_cnt` 以降のカラムは、クイズをプレイすると自動で作成・更新されます。最低限 `jp`（または `ja`）と `en` があれば遊べます。

---

## ディレクトリ構成

```
memorize_app/
├── config.py                       # OpenAI APIキー（自分で作成・gitignore済み）
├── scripts/
│   ├── quiz_offline.py             # クイズ：オフライン（自己採点）
│   ├── answer_at_gpt.py            # クイズ：GPT採点＋解説＋質問モード
│   ├── add_question.py             # 問題の手動追加
│   ├── dataset_utils.py            # データセット管理の共通処理
│   ├── generate_study_notes.py     # 間違えた問題の学習ノート生成
│   ├── mp3_to_json.py              # ① mp3 → 文字起こしJSON
│   └── rawscripts_to_data.py       # ② JSON → 問題集CSV
└── data/                          # ★ .gitignore対象（リポジトリには含まれない）
    ├── datasets/                   # 問題プール（クイズの対象・成績もここに記録）
    │   └── default.csv             #   問題を追加すると作られる標準データセット
    └── eibunpo/                    # mp3教材の生成パイプライン用
        ├── 21177-1/, 21177-2/      #   元のmp3教材
        ├── text/                   #   文字起こしJSON
        └── dataframe/
            └── eibunpo_sentences.csv  # ②の出力（datasetsへコピーして使う）
```
