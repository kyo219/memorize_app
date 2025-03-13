import pandas as pd
import os
from datetime import datetime
import argparse

class StudyNotesGenerator:
    def __init__(self, table_path='data/eibunpo/dataframe/eibunpo_sentences.csv'):
        self.table_path = table_path
        self.table_df = self.load_table()
        
    def load_table(self):
        if not os.path.exists(self.table_path) or os.path.getsize(self.table_path) == 0:
            print(f"{self.table_path} が見つかりません、または空です。終了します。")
            exit()
        return pd.read_csv(self.table_path)
    
    def filter_data(self, filter_type):
        """
        データをフィルタリングする
        filter_type: 'all_incorrect' または 'today_incorrect'
        """
        if filter_type == 'all_incorrect':
            # 間違えたフラグが残っているもの
            return self.table_df[self.table_df['latest_label'] == 'Incorrect']
        elif filter_type == 'today_incorrect':
            # 今日間違えたもの
            today = datetime.now().strftime('%Y-%m-%d')
            return self.table_df[
                (self.table_df['latest_label'] == 'Incorrect') & 
                (self.table_df['last_answered'].str.startswith(today, na=False))
            ]
        else:
            print(f"不明なフィルタータイプ: {filter_type}")
            return pd.DataFrame()
    
    def generate_markdown(self, filter_type, output_path=None):
        """
        マークダウンファイルを生成する
        filter_type: 'all_incorrect' または 'today_incorrect'
        output_path: 出力ファイルパス（Noneの場合は自動生成）
        """
        filtered_df = self.filter_data(filter_type)
        
        if filtered_df.empty:
            print(f"フィルター条件 '{filter_type}' に一致するデータがありません。")
            return
        
        # 出力ファイル名を決定
        if output_path is None:
            today = datetime.now().strftime('%Y-%m-%d')
            filter_name = "all_incorrect" if filter_type == "all_incorrect" else "today_incorrect"
            output_path = f"study_notes_{filter_name}_{today}.md"
        
        # マークダウンコンテンツを作成
        md_content = self._create_markdown_content(filtered_df, filter_type)
        
        # ファイルに書き込み
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(md_content)
        
        print(f"学習ノートを {output_path} に生成しました。")
        
    def _create_markdown_content(self, df, filter_type):
        """マークダウンコンテンツを作成する"""
        today = datetime.now().strftime('%Y-%m-%d')
        title = "今日間違えた問題の学習ノート" if filter_type == "today_incorrect" else "間違えた問題の学習ノート"
        
        content = [
            f"# {title} ({today})",
            "",
            f"## 概要",
            f"- 対象問題数: {len(df)}問",
            "",
            "## 理解すべき文法ポイント",
            ""
        ]
        
        # 文法ポイントをまとめる
        grammar_points = {}
        for _, row in df.iterrows():
            grammar = row.get('note_grammar', '')
            if pd.notna(grammar) and grammar.strip():
                # 最初の一文を抽出してキーにする
                key = grammar.split('.')[0] if '.' in grammar else grammar
                key = key.strip()
                if key not in grammar_points:
                    grammar_points[key] = []
                grammar_points[key].append((row.get('jp', ''), row.get('en', ''), grammar))
        
        for point, examples in grammar_points.items():
            content.append(f"### {point}")
            content.append("")
            for jp, en, grammar in examples[:3]:  # 最大3つの例を表示
                content.append(f"- 例文: 「{jp}」")
                content.append(f"  - 英訳: {en}")
                content.append(f"  - 解説: {grammar}")
                content.append("")
            content.append("")
        
        # イディオムをまとめる
        content.append("## 覚えるべきイディオム・表現")
        content.append("")
        
        idioms = {}
        for _, row in df.iterrows():
            idiom = row.get('note_idiom', '')
            if pd.notna(idiom) and idiom.strip():
                # 最初の一文を抽出してキーにする
                key = idiom.split('.')[0] if '.' in idiom else idiom
                key = key.strip()
                if key not in idioms:
                    idioms[key] = []
                idioms[key].append((row.get('jp', ''), row.get('en', ''), idiom))
        
        for idiom, examples in idioms.items():
            content.append(f"### {idiom}")
            content.append("")
            for jp, en, idiom_note in examples[:3]:  # 最大3つの例を表示
                content.append(f"- 例文: 「{jp}」")
                content.append(f"  - 英訳: {en}")
                content.append(f"  - 解説: {idiom_note}")
                content.append("")
            content.append("")
        
        # 理解が必要な点をまとめる
        content.append("## 理解が必要な点")
        content.append("")
        
        understanding_gaps = {}
        for _, row in df.iterrows():
            gap = row.get('note', '')
            if pd.notna(gap) and gap.strip():
                # 最初の一文を抽出してキーにする
                key = gap.split('.')[0] if '.' in gap else gap
                key = key.strip()
                if key not in understanding_gaps:
                    understanding_gaps[key] = []
                understanding_gaps[key].append((row.get('jp', ''), row.get('en', ''), gap))
        
        for gap, examples in understanding_gaps.items():
            content.append(f"### {gap}")
            content.append("")
            for jp, en, gap_note in examples[:3]:  # 最大3つの例を表示
                content.append(f"- 例文: 「{jp}」")
                content.append(f"  - 英訳: {en}")
                content.append(f"  - 解説: {gap_note}")
                content.append("")
            content.append("")
        
        # 全ての例文リスト
        content.append("## 全ての例文リスト")
        content.append("")
        content.append("| 日本語 | 英語 | 最終回答日 |")
        content.append("|-------|------|------------|")
        
        for _, row in df.iterrows():
            jp = row.get('jp', '')
            en = row.get('en', '')
            last_answered = row.get('last_answered', '')
            content.append(f"| {jp} | {en} | {last_answered} |")
        
        return "\n".join(content)

def main():
    parser = argparse.ArgumentParser(description='学習ノートを生成するツール')
    parser.add_argument('--filter', choices=['all_incorrect', 'today_incorrect'], 
                        default='all_incorrect',
                        help='フィルタータイプ: all_incorrect (全ての間違い) または today_incorrect (今日の間違い)')
    parser.add_argument('--output', type=str, default=None,
                        help='出力ファイルパス (指定しない場合は自動生成)')
    parser.add_argument('--table', type=str, default='data/eibunpo/dataframe/eibunpo_sentences.csv',
                        help='入力テーブルのパス')
    
    args = parser.parse_args()
    
    generator = StudyNotesGenerator(table_path=args.table)
    generator.generate_markdown(args.filter, args.output)

if __name__ == "__main__":
    main() 