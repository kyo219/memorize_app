import pandas as pd
import os
from datetime import datetime
import openai
import json
import sys
from pathlib import Path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import OPENAI_API_KEY


class QuizApp:
    def __init__(self, table_path='data/eibunpo/dataframe/eibunpo_sentences.csv', api_key=None):
        self.table_path = table_path
        self.table_df = self.load_table()
        # OpenAI APIキーの設定
        self.api_key = api_key
        if not self.api_key:
            print("OpenAI APIキーが設定されていません。環境変数OPENAI_API_KEYを設定するか、初期化時に指定してください。")
            exit()
        openai.api_key = self.api_key

    def load_table(self):
        if not os.path.exists(self.table_path) or os.path.getsize(self.table_path) == 0:
            print(f"{self.table_path} が見つかりません、または空です。終了します。")
            exit()
        df = pd.read_csv(self.table_path)
        # カラム名を確認して適切に処理
        if 'ja' in df.columns and 'en' in df.columns:
            # eibunpo_sentences.csvの形式に合わせる
            df.rename(columns={'ja': 'jp'}, inplace=True)
            
        # 必要なカラムを追加
        for column in ['wrong_cnt', 'correct_cnt', 'last_answered', 'latest_label', 'note_idiom', 'note_grammar', 'note']:
            if column not in df.columns:
                if column in ['wrong_cnt', 'correct_cnt']:
                    df[column] = 0
                else:
                    df[column] = ''
        return df

    def update_counts_time_and_label(self, index, is_correct):
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.table_df.loc[index, 'correct_cnt'] += int(is_correct)
        self.table_df.loc[index, 'wrong_cnt'] += int(not is_correct)
        self.table_df.loc[index, 'last_answered'] = now
        self.table_df.loc[index, 'latest_label'] = "Correct" if is_correct else "Incorrect"
        self.table_df.to_csv(self.table_path, index=False)

    def update_notes(self, index, idiom_note, grammar_note, understanding_note):
        """熟語、文法、理解度のノートを更新する"""
        self.table_df.loc[index, 'note_idiom'] = idiom_note
        self.table_df.loc[index, 'note_grammar'] = grammar_note
        self.table_df.loc[index, 'note'] = understanding_note
        self.table_df.to_csv(self.table_path, index=False)

    def ask_for_correctness(self):
        answer = input("正答としますか？ はい（default）、いいえ(n): ").lower()
        return not answer in ['n', 'no']

    def ask_to_continue(self):
        answer = input("続けますか？ Yes（そのままEnter）、No（Nと入力）: ").lower()
        return answer in ['', 'y', 'yes']

    def evaluate_with_gpt(self, user_answer, correct_answer, jp_text):
        """OpenAI APIを使用して回答を評価し、同時に熟語と文法も抽出する"""
        try:
            response = openai.chat.completions.create(
                model="gpt-4o-mini",
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": """
                    あなたは英語の翻訳評価を行う専門家です。
                    ユーザーの英訳と模範解答を比較し、正答とするか否かを判定してください. 
                    注意）typoだったり、省略後(I'mと I am)の有無や、大文字小文字の違い等は、無視して正答としてください. 
                    あくまで熟語や文法を理解しているかを評価してください.
                    
                    また、正解の英文から重要な熟語（イディオム）と文法構文を抽出し、ユーザーの理解が不足している点も分析してください。
                    
                    以下の形式でJSON形式で回答してください:
                    {
                        "is_correct": true/false,
                        "idiom": "最も重要な熟語または表現を1つ抽出し、その意味と使い方を簡潔に日本語で説明",
                        "grammar": "重要な文法構文を抽出し、その使い方と規則を簡潔に日本語で説明",
                        "understanding_gap": "ユーザーの回答から見て、理解が不足していると思われる点を簡潔に日本語で分析（あれば）"
                    }
                    """}, 
                    {"role": "user", "content": f"""
                    日本語: {jp_text}
                    ユーザーの英訳: {user_answer}
                    模範解答: {correct_answer}
                    
                    この英訳を評価し、また、重要な熟語と文法を抽出、理解が不足している点を分析してください。
                    """}
                ]
            )
            
            result = json.loads(response.choices[0].message.content)
            return result
        except Exception as e:
            print(f"APIエラー: {e}")
            return {
                "is_correct": False, 
                "feedback": "APIエラーが発生しました", 
                "idiom": "APIエラーが発生しました", 
                "grammar": "APIエラーが発生しました", 
                "understanding_gap": "APIエラーが発生しました"
            }

    def format_answer_section(self, label, content):
        return f"\n【{label}】\n{content}"
    
    def select_mode(self):
        mode = input("ゲームモードを選択してください。\n1. 全ての問題をランダムに並び替えて出題\n2. 最後に間違えた問題+回答していない問題をランダムに並び替えて出題\n選択: ")
        if mode == '2':
            self.table_df = self.table_df[self.table_df['latest_label'] != 'Correct'].sample(frac=1).reset_index(drop=True)
        else:
            self.table_df = self.table_df.sample(frac=1).reset_index(drop=True)

    def start_quiz(self):
        self.select_mode()
        total_questions = len(self.table_df)
        for index, row in self.table_df.iterrows():
            remaining_questions = total_questions - (index + 1)
            
            print(f"\n===== 問題 {index + 1}/{total_questions} - 残り{remaining_questions}問 =====")
            # eibunpo_sentences.csvの形式に合わせる
            jp_text = row['jp'] if 'jp' in row else row['ja']
            correct_eng = row['en'] if 'en' in row else row['eng']
            source_note = row.get('source_file', '')
            
            print(f"\n日本語: {jp_text}")
            print("英語訳を入力してください:")
            user_answer = input()
            
            print("\n----- 結果 -----")
            print(self.format_answer_section("あなたの回答", user_answer))
            print(self.format_answer_section("正解", correct_eng))
            
            if pd.notnull(source_note) and source_note != '':
                print(f"\n出典: {source_note}")
            
            # GPTによる自動評価と熟語・文法の抽出を一度に行う
            evaluation = self.evaluate_with_gpt(user_answer, correct_eng, jp_text)
            is_correct = evaluation["is_correct"]
            if evaluation.get("feedback", ""):
                print(f"\nフィードバック: {evaluation['feedback']}")
            
            print(f"\n【判定】: {'✓ 正解' if is_correct else '✗ 不正解'}")
            
            print("\n----- 学習ポイント -----")
            # 熟語と文法の情報を表示
            idiom_note = evaluation.get("idiom", "")
            grammar_note = evaluation.get("grammar", "")
            understanding_note = evaluation.get("understanding_gap", "")
            
            print(self.format_answer_section("重要な熟語/表現", idiom_note))
            print(self.format_answer_section("重要な文法", grammar_note))
            print(self.format_answer_section("理解が必要な点", understanding_note))
            
            # 分析結果をデータフレームに保存
            self.update_notes(index, idiom_note, grammar_note, understanding_note)
            
            # GPTの判定を使用して記録
            print(f"\n{'正解' if is_correct else '不正解'}として記録しました。")
            self.update_counts_time_and_label(index, is_correct)
            
            print("\n" + "-" * 50)
            if not self.ask_to_continue():
                break

if __name__ == "__main__":
    app = QuizApp(api_key=OPENAI_API_KEY)
    app.start_quiz()
