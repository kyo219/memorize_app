import pandas as pd
import os

class CreateMemorizeTable:
    def __init__(self, filepath='data/table.csv'):
        self.filepath = filepath
        if os.path.exists(self.filepath):
            self.df = pd.read_csv(self.filepath)
        else:
            self.df = pd.DataFrame(columns=['jp', 'eng', 'note'])

    def add_table(self, jp, eng, note=None):
        new_row = {'jp': jp, 'eng': eng, 'note': note}
        self.df = pd.concat([self.df, pd.DataFrame([new_row])], ignore_index=True)
        self.save_table()
        self.ask_continue()

    def save_table(self):
        os.makedirs(os.path.dirname(self.filepath), exist_ok=True)
        self.df.to_csv(self.filepath, index=False)

    def input_with_confirmation(self, prompt, language='入力'):
        while True:
            try:
                user_input = input(f'{prompt}（{language}）: ')
                confirmation = input(f'「{user_input}」こちらでよろしいですか？ Yes（そのままenter）、No（Nと入力）: ').lower()
                if confirmation in ['', 'y', 'yes']:
                    return user_input
                elif confirmation == 'n':
                    print("再度入力してください。")
            except UnicodeDecodeError as e:
                print("入力エラーが発生しました。もう一度お試しください。")

    def ask_continue(self):
        continue_input = input('続けますか？ Yes（そのままenter）、No（Nと入力）: ').lower()
        if continue_input in ['', 'y', 'yes']:
            self.run()
        else:
            print("終了します。")

    def run(self):
        jp = self.input_with_confirmation('追加する日本語', '日本語')
        eng = self.input_with_confirmation('追加する英語', '英語')
        note = self.input_with_confirmation('追加するノート', 'ノート')
        self.add_table(jp, eng, note)

# インスタンスの作成と実行
if __name__ == '__main__':
    memorize_table = CreateMemorizeTable()
    memorize_table.run()

    # データフレームの内容を表示（確認用）
    print(memorize_table.df)
