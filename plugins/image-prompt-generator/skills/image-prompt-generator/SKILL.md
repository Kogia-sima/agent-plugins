---
name: image-prompt-generator
description: ビジネス向けの図・イラスト（概念図、フロー図、アイソメトリック図、アイキャッチ、資料用ビジュアルなど）を画像生成AIで作成するための英語プロンプトを生成するスキル。「画像生成用のプロンプトを作って」「Midjourney/DALL-E/Stable Diffusion用のプロンプトがほしい」「この図を画像AIで作りたい」「資料に載せるイラストのプロンプトを書いて」などの依頼で必ず発動すること。明示的に「プロンプト」と言われなくても、ユーザーが画像生成AIに入力するテキストを求めている文脈であれば積極的に使用する。
---

# Image Prompt Generator (Business Diagrams)

ユーザーの要望をもとに、画像生成AI用の詳細な英語プロンプトを生成し、必ずその日本語訳とセットで提示する。

## 手順

1. 要望から次の要素を把握する。不足があれば1〜2問だけ簡潔に確認し、それ以外は妥当なデフォルトで補う（補った内容は出力後に一言添える）。
   - 主題・伝えたい内容
   - 図の種類（概念図 / フロー図 / アイソメトリックイラスト / アイキャッチ 等）
   - 用途（プレゼン資料 / 顧客提案 / Web記事 等）
   - スタイル・配色・アスペクト比
   - 図中に入れるテキスト（ラベル・見出し等）の有無と内容
2. 下記ガイドラインに沿って英語プロンプトを組み立てる。
3. 下記の出力形式で提示する。

## プロンプト作成ガイドライン

- 構成順: 主題 → 図の種類/構図 → 図中テキスト指定 → スタイル → 配色 → 背景 → 品質・用途指定。
- ビジネス向けデフォルトスタイル（ユーザー指定がない場合）:
  - Style: `flat design, minimalist, clean corporate illustration, vector style`
  - Colors: `professional color palette, navy blue and light gray, subtle accent color`
  - Composition: `balanced layout, generous white space`
  - Background: `plain white background`
  - Quality: `high resolution, sharp lines, presentation-ready`
- 具体的な数値・固有名詞は再現されないため、構造や関係性の表現に落とし込む。
- アスペクト比や用途（例: `16:9 aspect ratio, suitable for a business presentation slide`）を明記する。
- 生成先モデルが判明している場合はその記法に合わせる（例: Midjourneyなら `--ar 16:9`）。不明ならツール非依存の自然文で書く。

## 図中テキストのルール（重要）

- 画像内に含まれるテキストは、すべて日本語に統一する。
- プロンプトに `all text and labels in Japanese, no English text` を必ず含める。
- 表示したい日本語テキストは、プロンプト内に具体的な文字列として引用符付きで明記する（例: `labeled "現状分析", "施策立案", "実行" in Japanese`）。曖昧に "with labels" とだけ書かない。
- テキストは短い単語・フレーズに限定する（1ラベルあたり2〜6文字程度が目安）。長文は崩れやすい。
- モデルによっては日本語の描画精度が低い旨を、出力後に一言注意として添える（生成結果の文字が崩れた場合はラベル数を減らす・後から手動で文字入れする等の代替案を示す）。
- ユーザーが「文字なし」を明示した場合のみ `no text, no labels` に切り替える。

## 出力形式

ALWAYS この構成で出力する:

1. **英語プロンプト** — コードブロックでそのままコピーできる形にする。
2. **日本語訳** — 英語プロンプトの内容を忠実に訳す。ユーザーが内容を検証・修正指示できることが目的。
3. （対応モデルの場合）**ネガティブプロンプト** — 同様に英語＋日本語訳のセットで提示する。ネガティブプロンプトには `English text, garbled characters, misspelled text` を含めることを推奨。

## 例

Input: 「クラウド移行のメリットを説明するスライド用の画像がほしい」

Output:

英語プロンプト:
```
A clean flat design business illustration showing the concept of cloud migration, servers and data flowing upward into a stylized cloud, three benefit icons below labeled "コスト削減", "拡張性", "安定運用" in Japanese, all text and labels in Japanese, no English text, isometric perspective, navy blue and light gray professional color palette with a subtle accent color, balanced layout with generous white space, plain white background, high resolution, sharp lines, 16:9 aspect ratio, suitable for a business presentation slide
```

日本語訳:
「クラウド移行の概念を示す、クリーンなフラットデザインのビジネスイラスト。サーバーとデータが様式化された雲に向かって上昇していく様子。下部に『コスト削減』『拡張性』『安定運用』と日本語でラベル付けされた3つのメリットアイコン。画像内のテキストはすべて日本語、英語表記なし。アイソメトリック視点。ネイビーブルーとライトグレーのプロフェッショナルな配色に控えめなアクセントカラー。余白を活かしたバランスの良いレイアウト。無地の白背景。高解像度、シャープな線。アスペクト比16:9、ビジネスプレゼン用スライドに適した仕上がり。」
