import pandas as pd
import os
import sys
from datetime import datetime

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from dataset_utils import dataset_path, prompt_dataset_name


class QuizAppOffline:
    def __init__(self, table_path='data/datasets/default.csv'):
        self.table_path = table_path
        self.table_df = self.load_table()
        self.current_question_index = None

    def load_table(self):
        if not os.path.exists(self.table_path) or os.path.getsize(self.table_path) == 0:
            print(f"データセットが見つかりません: {self.table_path}")
            print("先に `uv run python scripts/add_question.py` で問題を追加してください。")
            exit()
        df = pd.read_csv(self.table_path)
        if 'ja' in df.columns and 'en' in df.columns:
            df.rename(columns={'ja': 'jp'}, inplace=True)

        for column in ['wrong_cnt', 'correct_cnt', 'last_answered', 'latest_label']:
            if column not in df.columns:
                if column in ['wrong_cnt', 'correct_cnt']:
                    df[column] = 0
                else:
                    df[column] = ''
        # 文字列カラムが空のとき float 扱いになり、後で文字列を書くと警告が出るため object に統一
        for column in ['last_answered', 'latest_label']:
            df[column] = df[column].astype('object')
        return df

    def update_counts_time_and_label(self, index, is_correct):
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.table_df.loc[index, 'correct_cnt'] += int(is_correct)
        self.table_df.loc[index, 'wrong_cnt'] += int(not is_correct)
        self.table_df.loc[index, 'last_answered'] = now
        self.table_df.loc[index, 'latest_label'] = "Correct" if is_correct else "Incorrect"
        self.table_df.to_csv(self.table_path, index=False)

    def ask_for_correctness(self):
        while True:
            answer = input("\n正解でしたか？ [y/n]: ").lower().strip()
            if answer in ['y', 'yes', '']:
                return True
            elif answer in ['n', 'no']:
                return False
            print("y または n で回答してください。")

    def ask_to_continue(self):
        answer = input("\n続けますか？ [Enter: 続ける / q: 終了]: ").lower().strip()
        return answer not in ['q', 'quit', 'exit']

    def select_mode(self):
        print("\n===== クイズモード選択 =====")
        print("1. 全ての問題をランダムに出題")
        print("2. 間違えた問題 + 未回答の問題をランダムに出題")
        mode = input("選択 [1/2]: ").strip()

        if mode == '2':
            self.table_df = self.table_df[self.table_df['latest_label'] != 'Correct'].sample(frac=1).reset_index(drop=True)
        else:
            self.table_df = self.table_df.sample(frac=1).reset_index(drop=True)

        print(f"\n対象問題数: {len(self.table_df)}問")

    def start_quiz(self):
        self.select_mode()

        if len(self.table_df) == 0:
            print("対象の問題がありません。")
            return

        total_questions = len(self.table_df)
        correct_count = 0
        answered_count = 0

        for index, row in self.table_df.iterrows():
            self.current_question_index = index
            remaining_questions = total_questions - (index + 1)

            print(f"\n{'='*50}")
            print(f"問題 {index + 1}/{total_questions} (残り {remaining_questions}問)")
            print('='*50)

            jp_text = row['jp'] if 'jp' in row else row['ja']
            correct_eng = row['en'] if 'en' in row else row['eng']
            source_note = row.get('source_file', '')

            print(f"\n【日本語】{jp_text}")
            print("\n英訳を入力してください:")
            user_answer = input("> ")

            print("\n" + "-"*50)
            print("【あなたの回答】")
            print(f"  {user_answer}")
            print("\n【正解】")
            print(f"  {correct_eng}")

            if pd.notnull(source_note) and source_note != '':
                print(f"\n出典: {source_note}")
            print("-"*50)

            is_correct = self.ask_for_correctness()
            self.update_counts_time_and_label(index, is_correct)

            answered_count += 1
            if is_correct:
                correct_count += 1
                print("✓ 正解として記録しました。")
            else:
                print("✗ 不正解として記録しました。")

            print(f"\n現在の成績: {correct_count}/{answered_count} ({correct_count/answered_count*100:.1f}%)")

            if not self.ask_to_continue():
                break

        print("\n" + "="*50)
        print("クイズ終了")
        print(f"最終成績: {correct_count}/{answered_count} ({correct_count/answered_count*100:.1f}%)")
        print("="*50)


if __name__ == "__main__":
    name = prompt_dataset_name()
    print(f"\nデータセット '{name}' で開始します。")
    app = QuizAppOffline(table_path=dataset_path(name))
    app.start_quiz()
