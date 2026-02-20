#!/usr/bin/env python3
"""
アフィリエイト記事 AI自動生成スクリプト
使用方法: python3 generate_article.py
"""

import os
import json
import datetime
from pathlib import Path
from openai import OpenAI

# ============================================================
# 設定エリア（ユーザーがカスタマイズする部分）
# ============================================================

# OpenAI APIキー（環境変数から取得）
# 環境変数 OPENAI_API_KEY を設定してください
client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
    base_url="https://api.openai.com/v1"  # 本番OpenAI APIを使用
)

# アフィリエイトリンク設定（A8.netで取得したリンクに差し替えてください）
AFFILIATE_LINKS = {
    "三井住友カード": "https://ck.jp.ap.valuecommerce.com/servlet/referral?sid=YOUR_SID&pid=YOUR_PID",
    "楽天カード": "https://ck.jp.ap.valuecommerce.com/servlet/referral?sid=YOUR_SID&pid=YOUR_PID2",
    "JCBカード": "https://px.a8.net/svt/ejp?a8mat=YOUR_A8_CODE",
    "エポスカード": "https://px.a8.net/svt/ejp?a8mat=YOUR_A8_CODE2",
}

# サイト情報
SITE_NAME = "クレジットカード比較ナビ"
SITE_URL = "https://YOUR_USERNAME.github.io"  # GitHubユーザー名に変更

# 記事出力先（Jekyllの_postsフォルダ）
OUTPUT_DIR = Path("../_posts")

# ============================================================
# SEOキーワードリスト（自動生成する記事のテーマ）
# ============================================================

KEYWORDS = [
    "クレジットカード 初めて おすすめ",
    "クレジットカード 学生 おすすめ 2024",
    "クレジットカード ポイント 還元率 高い",
    "クレジットカード 年会費無料 おすすめ",
    "楽天カード メリット デメリット",
    "三井住友カード 審査 通りやすい",
    "クレジットカード 海外旅行 おすすめ",
    "クレジットカード 主婦 審査 通りやすい",
    "クレジットカード 2枚持ち おすすめ 組み合わせ",
    "クレジットカード ゴールド おすすめ コスパ",
    "クレジットカード キャッシュバック おすすめ",
    "クレジットカード 電子マネー チャージ おすすめ",
    "クレジットカード 即日発行 おすすめ",
    "クレジットカード 審査なし 作れる",
    "クレジットカード 比較 2024 最新",
]


def generate_article(keyword: str) -> dict:
    """
    キーワードに基づいてSEO最適化されたアフィリエイト記事を生成する
    """
    
    # アフィリエイトリンクをプロンプトに含める
    affiliate_info = "\n".join([
        f"- {name}: {url}" for name, url in AFFILIATE_LINKS.items()
    ])
    
    prompt = f"""
あなたはSEOに強いクレジットカード比較サイトのライターです。
以下のキーワードで検索上位を狙える、読者に役立つ記事を書いてください。

【ターゲットキーワード】
{keyword}

【記事の要件】
1. タイトルはキーワードを含む魅力的なものにする（30〜40文字）
2. 文字数は2000〜3000文字
3. H2・H3見出しを使って読みやすく構成する
4. 具体的な数字・データを含める
5. 読者の悩みを解決する実用的な内容にする
6. 以下のアフィリエイトリンクを自然な形で2〜3箇所に挿入する：
{affiliate_info}
7. 記事の最後に「まとめ」セクションを入れる
8. Markdown形式で出力する

【出力形式】
以下のJSON形式で出力してください：
{{
  "title": "記事タイトル",
  "description": "SEO用メタディスクリプション（120文字以内）",
  "tags": ["タグ1", "タグ2", "タグ3"],
  "content": "Markdown形式の記事本文"
}}
"""
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "あなたはSEOとアフィリエイトマーケティングの専門家です。"},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        max_tokens=4000,
        response_format={"type": "json_object"}
    )
    
    result = json.loads(response.choices[0].message.content)
    return result


def save_article(article: dict, keyword: str) -> str:
    """
    記事をJekyll形式のMarkdownファイルとして保存する
    """
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    today = datetime.date.today().strftime("%Y-%m-%d")
    
    # ファイル名用にキーワードをスラッグ化
    slug = keyword.replace(" ", "-").replace("　", "-")
    slug = "".join(c for c in slug if c.isalnum() or c in "-_")[:50]
    filename = f"{today}-{slug}.md"
    
    # Jekyll Front Matter（ヘッダー情報）
    tags_str = "\n".join([f"  - {tag}" for tag in article.get("tags", [])])
    
    front_matter = f"""---
layout: post
title: "{article['title']}"
date: {today}
description: "{article.get('description', '')}"
tags:
{tags_str}
---

"""
    
    filepath = OUTPUT_DIR / filename
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(front_matter)
        f.write(article["content"])
    
    print(f"✅ 記事を保存しました: {filepath}")
    return str(filepath)


def main():
    """
    メイン処理：キーワードリストから記事を自動生成する
    """
    print(f"🚀 アフィリエイト記事自動生成を開始します")
    print(f"📝 生成予定記事数: {len(KEYWORDS)}件\n")
    
    generated = []
    errors = []
    
    for i, keyword in enumerate(KEYWORDS, 1):
        print(f"[{i}/{len(KEYWORDS)}] キーワード: {keyword}")
        
        try:
            # 記事生成
            article = generate_article(keyword)
            
            # ファイル保存
            filepath = save_article(article, keyword)
            generated.append({"keyword": keyword, "file": filepath, "title": article["title"]})
            
            print(f"   タイトル: {article['title']}\n")
            
        except Exception as e:
            print(f"   ❌ エラー: {e}\n")
            errors.append({"keyword": keyword, "error": str(e)})
    
    # 結果サマリー
    print("\n" + "="*50)
    print(f"✅ 生成完了: {len(generated)}件")
    if errors:
        print(f"❌ エラー: {len(errors)}件")
    print("="*50)
    
    return generated


if __name__ == "__main__":
    main()
