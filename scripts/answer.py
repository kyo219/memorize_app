import pandas as pd
import os
import random

class QuizApp:
    def __init__(self, table_path='data/table.csv', output_path='data/output.csv'):
        self.table_path = table_path
        self.output_path = output_path
        self.load_or_create_csv(self.output_path, ['jp', 'eng', 'result', 'note'])
        self.table_df = self.load_table()

    def load_or_create_csv(self, filepath, columns):
        if not os.path.exists(filepath):
            df = pd.DataFrame(columns=columns)
            df.to_csv(filepath, index=False)
        return pd.read_csv(filepath)

    def load_table(self):
        if not os.path.exists(self.table_path) or os.path.getsize(self.table_path) == 0:
            print(f"{self.table_path} が見つかりません、または空です。終了します。")
            exit()
        return pd.read_csv(self.table_path)

    def pick_random_row(self):
        return self.table_df.sample(n=1).iloc[0]

    def ask_to_continue(self):
        answer = input("続けますか？ Yes（そのままEnter）、No（Nと入力）: ").lower()
        return answer in ['', 'y', 'yes']

    def format_answer_section(self, label, content):
        return f"====\n{label}\n{content}\n===="

    def start_quiz(self):
        while True:
            random_row = self.pick_random_row()
            jp_text = random_row['jp']
            correct_eng = random_row['eng']
            note = random_row['note']
            
            print(f"日本語: {jp_text}\n英語訳を入力してください:")
            user_answer = input()
            
            # 正解判定
            if user_answer.strip().lower() == correct_eng.strip().lower():
                print(self.format_answer_section("回答", user_answer))
                print("correct!")
            else:
                print(self.format_answer_section("回答", user_answer))
                print("miss!")
                print(self.format_answer_section("正解", correct_eng))
                if pd.notnull(note) and note != '':
                    print(f"Note: {note}")
            
            if not self.ask_to_continue():
                break

if __name__ == '__main__':
    quiz_app = QuizApp()
    quiz_app.start_quiz()
