"""問題を手動で追加するモード。

1. データセット名を入力（そのまま Enter で default）
2. 日本語 → 英語（答え）の順に入力すると、そのデータセットの CSV に記録される
3. 日本語を空のまま Enter で終了

使い方:
    uv run python scripts/add_question.py
"""
import os
import sys
import pandas as pd

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from dataset_utils import dataset_path, load_dataset, prompt_dataset_name, DATASETS_DIR


def add_questions():
    print("===== 問題の手動追加モード =====")
    name = prompt_dataset_name()
    path = dataset_path(name)

    os.makedirs(DATASETS_DIR, exist_ok=True)
    df = load_dataset(path, create_if_missing=True)

    is_new = not os.path.exists(path)
    print(f"\nデータセット '{name}' ({path}) に追加します。"
          f"{'（新規作成）' if is_new else f'（現在 {len(df)} 問）'}")
    print("日本語を空のまま Enter で終了します。\n")

    MAX_REWRITES = 5
    added = 0
    while True:
        jp_text = input("日本語: ").strip()
        if jp_text == '':
            break
        en_text = input("英語（答え）: ").strip()
        if en_text == '':
            print("英語が空のためスキップしました。\n")
            continue

        # 入力内容を確認。ダメなら最大5回まで書き直せる
        rewrites = 0
        while True:
            print(f"\n  日本語: {jp_text}")
            print(f"  英語  : {en_text}")
            ans = input("これで登録しますか？ [Enter: OK / r: 書き直し]: ").strip().lower()
            if ans in ['', 'y', 'yes', 'ok']:
                break
            if rewrites >= MAX_REWRITES:
                print(f"書き直し上限（{MAX_REWRITES}回）に達しました。最後の入力で登録します。")
                break
            rewrites += 1
            print(f"書き直してください（あと {MAX_REWRITES - rewrites + 1} 回）。"
                  f"そのまま Enter で前の入力を残します。")
            jp_text = input("日本語: ").strip() or jp_text
            en_text = input("英語（答え）: ").strip() or en_text

        new_row = {
            'row': len(df) + 1,
            'jp': jp_text,
            'en': en_text,
            'source_file': 'manual',
            'wrong_cnt': 0,
            'correct_cnt': 0,
            'last_answered': '',
            'latest_label': '',
            'note_idiom': '',
            'note_grammar': '',
            'note': '',
        }
        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
        df.to_csv(path, index=False)
        added += 1
        print(f"✓ 記録しました（このセッションで {added} 問追加）\n")

    print(f"\n終了します。'{name}' に {added} 問追加しました（合計 {len(df)} 問）。")


if __name__ == "__main__":
    add_questions()
