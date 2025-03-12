import os
import json
import glob
import pandas as pd
import openai
from tqdm import tqdm
import sys
import time
from pathlib import Path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import OPENAI_API_KEY

# OpenAI APIキーの設定
openai.api_key = OPENAI_API_KEY

# 入力ディレクトリと出力ディレクトリの設定
INPUT_DIR = "data/eibunpo/text"
OUTPUT_DIR = "data/eibunpo/dataframe"

# 出力ディレクトリが存在しない場合は作成
os.makedirs(OUTPUT_DIR, exist_ok=True)

def read_file_content(file_path):
    """ファイルの内容をそのまま読み込む"""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except Exception as e:
        print(f"ファイル読み込みエラー ({file_path}): {e}")
        return None

def process_file_with_openai(file_content):
    """
    OpenAI APIを使用してファイル内容を処理し、文単位で分割する
    """
    try:
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system", 
                    "content": """
                    あなたは日本語と英語のテキストを正確に文単位で分割するアシスタントです。
                    与えられたJSONファイルから日本語と英語の対応する文を抽出し、リスト形式で返してください。
                    
                    以下の点に注意してください：
                    - JSONファイル内の"ja"と"en"フィールドから内容を抽出してください
                    - 複数の文が含まれています
                    - 書き起こしが汚く、jaとenが入り混じっていたり、jaが繰り返されていたりする可能性もありますが、柔軟に対応してください
                    - テキスト内の「Chapter」や「Unit」などの不要な部分は除外してください
                    - 日本語文と対応する英語文を正確に対応づけてください
                    - 出力は[{"ja": "日本語文", "en": "対応する英語文"}, ...]の形式にしてください
                    """
                },
                {
                    "role": "user",
                    "content": f"以下のJSONファイルの内容から、日本語と英語の対応する文をペアで抽出してください：\n\n{file_content}"
                }
            ],
            response_format={"type": "json_object"}
        )
        
        result = json.loads(response.choices[0].message.content)
        
        # 結果がリストであることを確認
        if "pairs" in result:
            return result["pairs"]
        else:
            # 標準的な形式ではない場合、適切なキーを見つけるか、結果そのものを返す
            for key, value in result.items():
                if isinstance(value, list):
                    return value
            return []  # フォールバック
            
    except Exception as e:
        print(f"Error in OpenAI API call: {e}")
        return []

def process_json_files():
    """すべてのJSONファイルを処理してデータフレームに変換"""
    # 出力CSVファイルパス
    output_csv = os.path.join(OUTPUT_DIR, "eibunpo_sentences.csv")
    
    # すでに存在するCSVファイルを読み込むか、新規作成
    if os.path.exists(output_csv):
        df = pd.read_csv(output_csv)
        processed_files = set(df['source_file'].unique())
        print(f"既存のCSVファイルから{len(processed_files)}件のファイルデータを読み込みました")
    else:
        df = pd.DataFrame(columns=['row', 'ja', 'en', 'source_file'])
        processed_files = set()
        print("新規CSVファイルを作成します")
    
    # 処理対象のJSONファイルを取得
    json_files = glob.glob(os.path.join(INPUT_DIR, "**", "*.json"), recursive=True)
    print(f"処理対象のJSONファイル: {len(json_files)}件")
    
    # まだ処理していないファイルをフィルタリング
    files_to_process = [f for f in json_files if os.path.relpath(f, INPUT_DIR) not in processed_files]
    print(f"未処理のJSONファイル: {len(files_to_process)}件")
    
    # 処理済みのカウント
    processed_count = 0
    
    # 各JSONファイルを処理
    for json_file in tqdm(files_to_process):
        relative_path = os.path.relpath(json_file, INPUT_DIR)
        
        try:
            # ファイル内容をそのまま読み込む
            file_content = read_file_content(json_file)
            
            if not file_content:
                print(f"警告: {json_file} の内容を読み込めませんでした")
                continue
            
            # OpenAI APIで処理
            sentence_pairs = process_file_with_openai(file_content)
            
            if not sentence_pairs:
                print(f"警告: {json_file} の処理結果が空でした")
                continue
            
            # データフレームに追加
            for i, pair in enumerate(sentence_pairs):
                new_row = {
                    'row': len(df) + 1,
                    'ja': pair.get('ja', ''),
                    'en': pair.get('en', ''),
                    'source_file': relative_path
                }
                df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
            
            # 一定間隔でCSVに保存
            processed_count += 1
            if processed_count % 5 == 0:
                df.to_csv(output_csv, index=False)
                print(f"{processed_count}件処理しました。中間保存を行いました。")
            
            # APIレート制限を考慮して少し待機
            time.sleep(2)
            
        except Exception as e:
            print(f"エラー: {json_file} の処理中にエラーが発生しました: {e}")
    
    # 最終的なCSVを保存
    df.to_csv(output_csv, index=False)
    print(f"処理完了。{len(df)}行のデータを {output_csv} に保存しました。")

if __name__ == "__main__":
    process_json_files()
