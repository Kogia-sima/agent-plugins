# CLAUDE.md

## このリポジトリの目的

個人用の **Claude Code プラグインマーケットプレイス**。自作プラグインを `plugins/<plugin-name>/` に置き、`.claude-plugin/marketplace.json` で一覧管理する。`claude plugin marketplace add` でこのリポジトリを登録すると、各プラグインを `<plugin-name>@agent-plugins` としてインストールできる。

## ディレクトリ構成

```
<project root directory>/
├── .claude-plugin/
│   └── marketplace.json         # マーケットプレイス定義（プラグイン一覧）
├── plugins/                     # 公開するプラグイン本体
│   └── <plugin-name>/
│       ├── .claude-plugin/
│       │   └── plugin.json      # プラグインのマニフェスト（name は marketplace.json と一致させる）
│       └── skills/<skill-name>/SKILL.md
├── scripts/                     # 開発用スクリプト
├── .github/workflows/           # CI（pre-commit, GitHub Actions Lint）
├── .devcontainer/               # VSCode Dev Container の設定ファイル
├── .claude/                     # このリポジトリ用 Claude Code 設定・ローカル Skill
├── README.md                    # リポジトリ概要・導入手順・プラグインカタログ
└── CLAUDE.md
```

プラグインを追加・変更したら `claude plugin validate .` で検証すること。

## 技術スタック

* **エディタ**: Visual Studio Code（VSCode）, Dev Container, Claude Code
* **バージョン管理**: GitHub
* **CI/CD**: GitHub Actions, pre-commit
* **コード品質**: MarkdownLint, Ruff, pyright
* **セキュリティ**: Dependabot + gitleaks

## 開発ルール

* コミットメッセージには日本語で記述すること（例: "feat: 新しい Skill を追加"）。
* 各スクリプト・設定ファイルには日本語で詳細なコメントを記載すること。
* 一貫性を保つため、コードスタイルやドキュメントのフォーマットは既存のものに従うこと。
* `CLAUDE.md` のディレクトリ構成や技術スタックは常に最新の状態に保つこと。
