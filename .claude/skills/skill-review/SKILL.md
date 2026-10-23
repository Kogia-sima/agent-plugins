---
name: skill-review
description: 任意のClaude SkillをAnthropic公式のベストプラクティスに照らしてレビューする。SKILL.mdの作成・改善後やレビュー依頼時に使用し、name/descriptionの良否・簡潔さ・構造・命名規約を点検して指摘とスコア、改善提案を出力する。
user-invocable: true
metadata:
  author: machida-analytics
---

# Skill Review

任意の Claude Skill（`SKILL.md` とその付随ファイル群）を、Anthropic 公式の
「Skill authoring best practices」に照らしてレビューし、指摘・スコア・改善提案を
レポートとして出力する。ユーザー承認のうえで修正提案を適用するところまで行う。

## 使う場面

- 新しい Skill を作成した直後、公開前の品質チェック。
- 既存 Skill の改善・リファクタリング前の現状診断。
- 「この Skill をレビューして」と依頼されたとき。

## レビュー手順（ワークフロー）

次のチェックリストをコピーして進捗を管理する。

```
Skill Review Progress:
- [ ] Step 1: レビュー対象を特定し、全ファイルを読み込む
- [ ] Step 2: チェックリストで各観点を評価する
- [ ] Step 3: レポートを出力する
- [ ] Step 4: 修正提案の適用可否を確認し、反映する
- [ ] Step 5: 再チェックで検証する
```

### Step 1: 対象を特定し読み込む

レビュー対象の Skill ディレクトリ（または `SKILL.md`）を特定する。対象が曖昧な
場合はユーザーに確認する。`reference/` などの付随ファイルもすべて読み込み、内容を把握する。

### Step 2: チェックリストで評価する

[reference/review-checklist.md](reference/review-checklist.md) を読み、各観点で
対象を評価する。観点の概要は下記「評価の主要観点」を参照。

### Step 3: レポートを出力する

[reference/report-template.md](reference/report-template.md) の様式でレビュー
レポートを出力する。指摘と改善提案はカテゴリ毎にセクション分けし、表形式で示す。
レポートの末尾には**最優先のネクストアクションを1つだけ**提示する（総評は不要）。

### Step 4: 修正提案を適用する

レポートを提示したうえで、ユーザーに修正適用の可否を確認する。**承認された指摘
のみ** `SKILL.md`（および付随ファイル）へ反映する。ユーザーが適用を望まない場合は
レポート出力までで完了とする。

### Step 5: 再チェックで検証する（feedback loop）

修正を適用した場合は、変更したファイルを再度チェックリストで自己検証し、指摘した
問題が解消され、新たな問題（行数超過・リンク切れ等）が生じていないことを確認する。
問題が残っていれば Step 4 に戻る。

## 評価の主要観点（要約）

詳細と合格基準は [reference/review-checklist.md](reference/review-checklist.md)
を参照。

- **Frontmatter 検証**: `name` / `description` の規約、`metadata.author` の必須。
- **簡潔さ**: Claude が既知の内容を冗長に説明していないか。
- **指示の具体度**: タスクの脆弱性に応じた指示の具体度。
- **スキルの構造**: SKILL.md 500行以内、参照は1階層のみ。
- **命名規約**: 曖昧な名前の回避。
- **一貫性・時限情報**: 用語の統一、時限情報の排除。
- **ワークフロー**: 複雑タスクの手順化と検証ループ。
- **スクリプト品質**（該当時）: エラー処理、定数の根拠、forward slash パス等。

## 出力フォーマット（要約）

[reference/report-template.md](reference/report-template.md) の統一様式に従う。
重大度は Critical / Warning / Suggestion の3段階。指摘＆改善提案はカテゴリ毎の
表形式で出力し、最後に推奨ネクストアクションを1つ示す。

## 誤検知の防止・適用範囲

- ベストプラクティスは**文脈に応じて適用**する。SKILL.md 単体で完結する小規模な
  Skill に対し、過剰なファイル分割や参照構造を強制しない。
- 行数制限などの定量基準は明確に判定するが、簡潔さ・指示の具体度（Degrees of freedom）などの
  定性観点は「改善余地（Suggestion）」として提示し、断定を避ける。
- 既存の意図的な設計判断を尊重し、確証のない推測は指摘に含めない。
