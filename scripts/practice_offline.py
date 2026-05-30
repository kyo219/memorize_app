import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from dataset_utils import dataset_path, prompt_dataset_name, write_out_practice
from quiz_offline import QuizAppOffline

# 1回の練習で扱う問題数と、書き取りの回数
PRACTICE_SIZE = 10
WRITE_TIMES = 5


class PracticeAppOffline(QuizAppOffline):
    """練習モード：数問を覚えてから（書き取り）、ランダム順でテストする。

    QuizAppOffline を継承し、テストフェーズでは 1 問分の出題・採点・記録を
    そのまま再利用する。成績はデータセット全体に記録される。
    """

    def ask_practice_size(self, default=PRACTICE_SIZE):
        raw = input(f"\n何問を練習しますか？（そのまま Enter で {default}）: ").strip()
        if raw.isdigit() and int(raw) > 0:
            return int(raw)
        return default

    def select_practice_set(self, size):
        print("\n===== 練習の出題範囲を選択 =====")
        print("1. 全ての問題から選ぶ")
        print("2. 間違えた問題 + 未回答の問題から選ぶ")
        mode = input("選択 [1/2]: ").strip()

        pool = self.table_df
        if mode == '2':
            pool = pool[pool['latest_label'] != 'Correct']

        if len(pool) == 0:
            return pool

        n = min(size, len(pool))
        return pool.sample(n=n)

    def study_phase(self, practice_df):
        total = len(practice_df)
        print("\n" + "=" * 50)
        print(f"📝 練習フェーズ：{total}問を覚えます")
        print(f"日本語と英語を見ながら、英語を{WRITE_TIMES}回書き取りましょう。")
        print("=" * 50)

        for position, (_, row) in enumerate(practice_df.iterrows(), start=1):
            jp_text = row['jp'] if 'jp' in row else row['ja']
            correct_eng = row['en'] if 'en' in row else row['eng']

            print(f"\n{'-' * 50}")
            print(f"練習 {position}/{total}")
            print(f"\n【日本語】{jp_text}")
            print(f"【英語】  {correct_eng}")
            print('-' * 50)

            write_out_practice(correct_eng, times=WRITE_TIMES)

            input("\n[Enter で次へ] ")

    def test_phase(self, practice_df):
        test_df = practice_df.sample(frac=1)
        total = len(test_df)
        print("\n" + "=" * 50)
        print(f"🎯 テストフェーズ：{total}問をランダム順で出題します")
        print("=" * 50)

        correct_count = 0
        for position, (index, row) in enumerate(test_df.iterrows(), start=1):
            is_correct = self.run_question(index, row, position, total)
            if is_correct:
                correct_count += 1
            print(f"\n現在の成績: {correct_count}/{position} ({correct_count / position * 100:.1f}%)")

        print("\n" + "=" * 50)
        print("テスト終了")
        print(f"最終成績: {correct_count}/{total} ({correct_count / total * 100:.1f}%)")
        print("=" * 50)

    def start_practice(self):
        size = self.ask_practice_size()
        practice_df = self.select_practice_set(size)

        if len(practice_df) == 0:
            print("対象の問題がありません。")
            return

        print(f"\n{len(practice_df)}問で練習を始めます。")
        self.study_phase(practice_df)
        self.test_phase(practice_df)


if __name__ == "__main__":
    name = prompt_dataset_name()
    print(f"\nデータセット '{name}' で練習を開始します。")
    app = PracticeAppOffline(table_path=dataset_path(name))
    app.start_practice()
