import pandas as pd
import os
from datetime import datetime

class QuizApp:
    def __init__(self, table_path='data/table.csv'):
        self.table_path = table_path
        self.table_df = self.load_table()

    def load_table(self):
        if not os.path.exists(self.table_path) or os.path.getsize(self.table_path) == 0:
            print(f"{self.table_path} が見つかりません、または空です。終了します。")
            exit()
        df = pd.read_csv(self.table_path)
        for column in ['wrong_cnt', 'correct_cnt', 'last_answered', 'latest_label']:
            if column not in df.columns:
                df[column] = 0 if column in ['wrong_cnt', 'correct_cnt'] else ''
        return df

    def update_counts_time_and_label(self, index, is_correct):
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.table_df.loc[index, 'correct_cnt'] += int(is_correct)
        self.table_df.loc[index, 'wrong_cnt'] += int(not is_correct)
        self.table_df.loc[index, 'last_answered'] = now
        self.table_df.loc[index, 'latest_label'] = "Correct" if is_correct else "Incorrect"
        self.table_df.to_csv(self.table_path, index=False)

    def ask_for_correctness(self):
        answer = input("正答としますか？ はい（default）、いいえ(n): ").lower()
        return not answer in ['n', 'no']

    def ask_to_continue(self):
        answer = input("続けますか？ Yes（そのままEnter）、No（Nと入力）: ").lower()
        return answer in ['', 'y', 'yes']

    def format_answer_section(self, label, content):
        return f"====\n{label}\n{content}\n===="
    
    def select_mode(self):
        mode = input("ゲームモードを選択してください。\n1. 全ての問題をランダムに並び替えて出題\n2. 最後に間違えた問題+回答していない問題をランダムに並び替えて出題\n 選択: ")
        if mode == '2':
            self.table_df = self.table_df[self.table_df['latest_label'] != 'Correct'].sample(frac=1).reset_index(drop=True)
        else:
            self.table_df = self.table_df.sample(frac=1).reset_index(drop=True)

    def start_quiz(self):
        self.select_mode()
        total_questions = len(self.table_df)
        for index, row in self.table_df.iterrows():
            remaining_questions = total_questions - (index + 1)
            
            print(f"問題 {index + 1}/{total_questions} - 残り{remaining_questions}問")
            jp_text = row['jp']
            correct_eng = row['eng']
            note = row['note']
            
            print(f"日本語: {jp_text}\n英語訳を入力してください:")
            user_answer = input()
            print(self.format_answer_section("回答", user_answer))
            print(self.format_answer_section("正解", correct_eng))
            if pd.notnull(note) and note != '':
                print(f"Note: {note}")
            is_correct = self.ask_for_correctness()
            if is_correct:
                print("正答として記録します。")
            else:
                print("不正解として記録します。")
            self.update_counts_time_and_label(index, is_correct)
            
            if not self.ask_to_continue():
                break

if __name__ == "__main__":
    app = QuizApp()
    app.start_quiz()
