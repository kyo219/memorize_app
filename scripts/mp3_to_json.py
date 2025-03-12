import os
import glob
import json
import time
import openai
from pathlib import Path
from tqdm import tqdm
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import OPENAI_API_KEY

# OpenAI APIキーの設定
openai.api_key = OPENAI_API_KEY

# 入力ディレクトリと出力ディレクトリの設定
INPUT_DIRS = ["data/eibunpo/21177-1", "data/eibunpo/21177-2"]
OUTPUT_DIR = "data/eibunpo/text"

# 出力ディレクトリが存在しない場合は作成
os.makedirs(OUTPUT_DIR, exist_ok=True)

def transcribe_audio_with_whisper(audio_file_path, language):
    """
    GPT-4oを使用して音声ファイルを指定された言語で文字起こしする
    """
    try:
        # audio.transcriptions.createを使用して音声ファイルを文字起こし
        with open(audio_file_path, "rb") as audio_file:
            response = openai.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                response_format="text",
                language=language  # 言語を直接指定
            )

        transcription_text = response
        return transcription_text

    except Exception as e:
        print(f"Error transcribing {audio_file_path} in {language}: {e}")
        return None


def process_mp3_files():
    """
    指定されたディレクトリ内のすべてのMP3ファイルを処理する
    """
    all_mp3_files = []
    
    # 指定されたディレクトリからMP3ファイルを収集
    for input_dir in INPUT_DIRS:
        mp3_files = glob.glob(os.path.join(input_dir, "**", "*.mp3"), recursive=True)
        all_mp3_files.extend(mp3_files)
    
    print(f"Found {len(all_mp3_files)} MP3 files to process")
    
    # 各MP3ファイルを処理
    for mp3_file in tqdm(all_mp3_files):
        relative_path = os.path.relpath(mp3_file, "data/eibunpo")
        output_file = os.path.join(OUTPUT_DIR, os.path.splitext(relative_path)[0] + ".json")
        
        # 文字起こし結果を格納する辞書
        transcription_dict = {}
        
        # 日本語の文字起こし
        if "ja" not in transcription_dict:
            print(f"Processing {mp3_file} for Japanese transcription")
            transcription_text_ja = transcribe_audio_with_whisper(mp3_file, "ja")
            if transcription_text_ja:
                transcription_dict["ja"] = transcription_text_ja
                print(f"Added Japanese transcription for {mp3_file}")
            else:
                print(f"Failed to transcribe {mp3_file} in Japanese")
        
        # 英語の文字起こし
        if "en" not in transcription_dict:
            print(f"Processing {mp3_file} for English transcription")
            transcription_text_en = transcribe_audio_with_whisper(mp3_file, "en")
            if transcription_text_en:
                transcription_dict["en"] = transcription_text_en
                print(f"Added English transcription for {mp3_file}")
            else:
                print(f"Failed to transcribe {mp3_file} in English")
        
        # 文字起こし結果をファイルに保存
        if transcription_dict:
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(transcription_dict, f, ensure_ascii=False, indent=2)
            print(f"Saved transcriptions to {output_file}")
        
        # APIレート制限を考慮して少し待機
        time.sleep(1)

if __name__ == "__main__":
    process_mp3_files()
