# agent-plugins

個人用の Claude Code プラグインマーケットプレイスです。

## 導入方法

マーケットプレイスを登録してから、プラグインを名前で指定してインストールします。

```bash
# ローカルのクローンを登録する場合
claude plugin marketplace add ./agent-plugins

# GitHub リポジトリから登録する場合
claude plugin marketplace add Kogia-sima/agent-plugins

# プラグインをインストール
claude plugin install <プラグイン名>@agent-plugins
```

セッション内では `/plugin marketplace add` と `/plugin install` でも同じ操作ができます。

## プラグイン一覧

| プラグイン | 内容 |
| --- | --- |
| [`adr-writer`](./plugins/adr-writer/) | ユーザのメモ書きや箇条書きから、ADR（Architectural Decision Records）の新規レコードをMarkdownファイルとして作成するスキル |
| [`document-review`](./plugins/document-review/) | Word・PDF・PowerPoint・Excel・Markdown など任意形式のドキュメントを、誤字脱字から目的適合性・全体構成まで多層的にレビューし、優先度順の推奨事項をまとめた Markdown レポートを作成するスキル |
| [`idea-sparring`](./plugins/idea-sparring/) | ユーザの背景情報とやりたいことのざっくりとした概要を入力として受け取り、ヒアリングを通じて本当の課題を特定したうえで、効果的な解決策を提案する壁打ちスキル |
| [`image-prompt-generator`](./plugins/image-prompt-generator/) | ビジネス向けの図・イラスト（概念図、フロー図、アイソメトリック図、アイキャッチ、資料用ビジュアルなど）を画像生成AIで作成するための英語プロンプトを生成するスキル |
| [`note-article-writer`](./plugins/note-article-writer/) | 株式会社分析屋のブログ記事（note）の原稿を執筆するスキル |
| [`requirements-definition`](./plugins/requirements-definition/) | ユーザの要望をヒアリングしながら要件定義を行い、システム要件定義書を作成するスキル |
| [`task-designer`](./plugins/task-designer/) | ユーザの実現したいこと(ゴール)を、実行可能なレベルのタスク一覧(チェックリスト形式)に分解するスキル |
| [`tech-article-review`](./plugins/tech-article-review/) | ユーザーが書いた技術記事をレビューするスキル |
| [`wbs-creator`](./plugins/wbs-creator/) | プロジェクトのゴールを入力すると、WBS（作業分解構造）を表形式で生成するスキル |
| [`commit`](./plugins/commit/) | Conventional Commits 形式に沿ったコミットを作成するスキル |
