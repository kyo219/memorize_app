"""データセット（問題プール）を管理するための共通ユーティリティ。

各データセットは data/datasets/<名前>.csv として保存される。
データセット名を省略した場合は 'default' を使う。
"""
import os
import pandas as pd

DATASETS_DIR = 'data/datasets'

# 問題そのものを表すカラム
BASE_COLUMNS = ['row', 'jp', 'en', 'source_file']
# プレイ結果・学習メモを記録するカラム
QUIZ_COLUMNS = ['wrong_cnt', 'correct_cnt', 'last_answered', 'latest_label',
                'note_idiom', 'note_grammar', 'note']


def dataset_path(name):
    """データセット名から CSV のパスを返す。空なら 'default'。"""
    name = (name or '').strip() or 'default'
    return os.path.join(DATASETS_DIR, f'{name}.csv')


def list_datasets():
    """利用可能なデータセット名の一覧を返す。"""
    if not os.path.isdir(DATASETS_DIR):
        return []
    return sorted(f[:-4] for f in os.listdir(DATASETS_DIR) if f.endswith('.csv'))


def prompt_dataset_name():
    """データセット名を尋ねる。そのまま Enter で 'default'。"""
    datasets = list_datasets()
    if datasets:
        print(f"\n利用可能なデータセット: {', '.join(datasets)}")
    name = input("データセット名を入力（そのままEnterで default）: ").strip()
    return name or 'default'


def ensure_columns(df):
    """クイズに必要なカラムを揃える（不足分を追加し、ja→jp に統一）。"""
    if 'ja' in df.columns and 'jp' not in df.columns:
        df.rename(columns={'ja': 'jp'}, inplace=True)
    for column in QUIZ_COLUMNS:
        if column not in df.columns:
            df[column] = 0 if column in ['wrong_cnt', 'correct_cnt'] else ''
    return df


def write_out_practice(correct_answer, times=5):
    """不正解時に、正解を指定回数だけ書き取りさせる（内容の一致は問わない）。"""
    print(f"\n----- 書き取り練習（{times}回）-----")
    print(f"正解: {correct_answer}")
    count = 0
    while count < times:
        entry = input(f"書き取り ({count + 1}/{times}) > ").strip()
        if entry == '':
            continue
        count += 1
    print("----- 書き取り完了 -----")


def load_dataset(path, create_if_missing=False):
    """データセットを読み込む。

    create_if_missing=True なら、存在しない場合は空のデータフレームを返す
    （手動追加モード用）。False の場合は見つからなければ終了する（クイズ用）。
    """
    if not os.path.exists(path) or os.path.getsize(path) == 0:
        if create_if_missing:
            return pd.DataFrame(columns=BASE_COLUMNS + QUIZ_COLUMNS)
        print(f"{path} が見つかりません、または空です。終了します。")
        raise SystemExit()
    return ensure_columns(pd.read_csv(path))
