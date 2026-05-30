# memorize_app

ターミナルで遊ぶ、Naive な暗記アプリの Python 実装。

日本語を見て英訳を打ち込み、正誤を記録していく英作文クイズです。間違えた問題だけを復習したり、GPT に採点・解説してもらったり、間違えた問題をまとめた学習ノートを Markdown で出力したりできます。音声教材（mp3）から自分だけの問題集を作ることもできます。

---

## 目次

- [必要なもの](#必要なもの)
- [セットアップ](#セットアップ)
- [まず遊んでみる（オフラインモード / APIキー不要）](#まず遊んでみるオフラインモード--apiキー不要)
- [クイズのモード一覧](#クイズのモード一覧)
  - [オフラインモード（自己採点）](#1-オフラインモード自己採点quiz_offlinepy)
  - [GPTモード（自動採点＋解説＋質問）](#2-gptモード自動採点解説質問answer_at_gptpy)
- [学習ノートを作る](#学習ノートを作る)
- [自分の教材を追加する](#自分の教材を追加する)
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

一番手軽な遊び方です。サンプルの英文法問題（約 760 問）が同梱されているので、セットアップ後すぐに始められます。

```bash
uv run python scripts/quiz_offline.py
```

1. モードを選ぶ（`1`: 全問ランダム / `2`: 間違い＋未回答のみ）
2. 表示された日本語を見て、英訳を入力
3. 正解が表示されるので、自分で正誤を判定（`y` / `n`）
4. 成績が記録され、次の問題へ。`q` でいつでも終了

正誤の記録は `data/eibunpo/dataframe/eibunpo_sentences.csv` に自動保存され、次回 `2`（復習モード）で間違えた問題だけを出題できます。

---

## クイズのモード一覧

どちらのスクリプトも、出題時に以下の2つの **出題パターン** を選べます。

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
| `--table` | 入力 CSV のパス | `data/eibunpo/dataframe/eibunpo_sentences.csv` |

---

## 自分の教材を追加する

音声教材（mp3）から、自分だけの問題集を作れます。**どちらのステップも OpenAI API キーが必要です。**

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

---

## データの形式

問題集 CSV（`data/eibunpo/dataframe/eibunpo_sentences.csv`）のカラム:

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
│   ├── generate_study_notes.py     # 間違えた問題の学習ノート生成
│   ├── mp3_to_json.py              # ① mp3 → 文字起こしJSON
│   └── rawscripts_to_data.py       # ② JSON → 問題集CSV
└── data/eibunpo/
    ├── 21177-1/, 21177-2/          # 元のmp3教材
    ├── text/                       # 文字起こしJSON
    └── dataframe/
        └── eibunpo_sentences.csv   # 問題集（成績もここに記録）
```
