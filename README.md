# agent-plugins

個人用のプラグインマーケットプレイスです。**Claude Code** と **Codex CLI** のどちらからでもインストールできます。

## 導入方法

どちらの CLI でも、マーケットプレイスを登録してからプラグインを `<プラグイン名>@agent-plugins` の形で指定してインストールします。

### Claude Code

```bash
# ローカルのクローンを登録する場合
claude plugin marketplace add ./agent-plugins

# GitHub リポジトリから登録する場合
claude plugin marketplace add Kogia-sima/agent-plugins

# プラグインをインストール
claude plugin install <プラグイン名>@agent-plugins
```

セッション内では `/plugin marketplace add` と `/plugin install` でも同じ操作ができます。

### Codex CLI

```bash
# ローカルのクローンを登録する場合
codex plugin marketplace add ./agent-plugins

# GitHub リポジトリから登録する場合
codex plugin marketplace add Kogia-sima/agent-plugins

# 登録済みのプラグインを確認
codex plugin list --marketplace agent-plugins

# プラグインをインストール
codex plugin add <プラグイン名>@agent-plugins

# マーケットプレイスを最新の状態に更新
codex plugin marketplace upgrade agent-plugins
```

`codex` を起動してから `/plugins` を入力すると、プラグインブラウザからもインストールや有効・無効の切り替えができます。インストールしたプラグインの Skill は、新しく開始したセッションで使えるようになります。

特定のプロジェクトだけで有効・無効を切り替えたい場合は、そのプロジェクトの `.codex/config.toml` に設定します。

```toml
[plugins."<プラグイン名>@agent-plugins"]
enabled = true
```

## プラグイン一覧

| プラグイン | 内容 |
| --- | --- |
| [`adr-writer`](./plugins/adr-writer/) | ユーザのメモ書きや箇条書きから、ADR（Architectural Decision Records）の新規レコードをMarkdownファイルとして作成するスキル |
| [`document-review`](./plugins/document-review/) | Word・PDF・PowerPoint・Excel・Markdown など任意形式のドキュメントを、誤字脱字から目的適合性・全体構成まで多層的にレビューし、優先度順の推奨事項をまとめた Markdown レポートを作成するスキル |
| [`idea-sparring`](./plugins/idea-sparring/) | ユーザの背景情報とやりたいことのざっくりとした概要を入力として受け取り、ヒアリングを通じて本当の課題を特定したうえで、効果的な解決策を提案する壁打ちスキル |
| [`image-prompt-generator`](./plugins/image-prompt-generator/) | ビジネス向けの図・イラスト（概念図、フロー図、アイソメトリック図、アイキャッチ、資料用ビジュアルなど）を画像生成AIで作成するための英語プロンプトを生成するスキル |
| [`requirements-definition`](./plugins/requirements-definition/) | ユーザの要望をヒアリングしながら要件定義を行い、システム要件定義書を作成するスキル |
| [`task-designer`](./plugins/task-designer/) | ユーザの実現したいこと(ゴール)を、実行可能なレベルのタスク一覧(チェックリスト形式)に分解するスキル |
| [`tech-article-review`](./plugins/tech-article-review/) | ユーザーが書いた技術記事をレビューするスキル |
| [`wbs-creator`](./plugins/wbs-creator/) | プロジェクトのゴールを入力すると、WBS（作業分解構造）を表形式で生成するスキル |
| [`commit`](./plugins/commit/) | Conventional Commits 形式に沿ったコミットを作成するスキル |
