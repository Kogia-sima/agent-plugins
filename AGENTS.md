# AGENTS.md

## このリポジトリの目的

**Claude Code / Codex CLI** の両方で使える、個人用のプラグインマーケットプレイス。自作プラグインを `plugins/<plugin-name>/` に置き、各 CLI 向けのマーケットプレイス定義で一覧を管理する。

* Claude Code: `claude plugin marketplace add` でこのリポジトリを登録し、`<plugin-name>@agent-plugins` としてインストールする
* Codex CLI: `codex plugin marketplace add` でこのリポジトリを登録し、`<plugin-name>@agent-plugins` としてインストールする

Skill 本体（`skills/<skill-name>/SKILL.md`）は両 CLI で共通の形式なので、1 つのファイルを共有する。

## ディレクトリ構成

```
<project root directory>/
├── .claude-plugin/
│   └── marketplace.json         # Claude Code 用マーケットプレイス定義（正本）
├── .agents/
│   ├── plugins/
│   │   └── marketplace.json     # Codex CLI 用マーケットプレイス定義（スクリプトで生成）
│   └── skills/                  # Codex CLI 用ローカル Skill（.claude/skills/ へのシンボリックリンク）
├── plugins/                     # 公開するプラグイン本体
│   └── <plugin-name>/
│       ├── .claude-plugin/
│       │   └── plugin.json      # Claude Code 用マニフェスト（正本。name は marketplace.json と一致させる）
│       ├── .codex-plugin/
│       │   └── plugin.json      # Codex CLI 用マニフェスト（スクリプトで生成）
│       └── skills/<skill-name>/SKILL.md
├── scripts/                     # 開発用スクリプト
│   ├── convert_skills_to_plugins.py  # Skill アーカイブ（.skills/*.skill）をプラグインに変換
│   ├── sync_codex_plugins.py         # Claude Code 用マニフェストから Codex CLI 用マニフェストを生成
│   └── japanese_commit_message.py    # コミットメッセージの日本語チェック（pre-commit フック）
├── .github/workflows/           # CI（pre-commit, GitHub Actions Lint）
├── .devcontainer/               # VSCode Dev Container の設定ファイル
├── .claude/                     # このリポジトリ用 Claude Code 設定・ローカル Skill
├── README.md                    # リポジトリ概要・導入手順・プラグインカタログ
└── AGENTS.md                    # プロジェクト指示（Claude Code / Codex CLI 共通）
```

## プラグインの追加・変更手順

1. Claude Code 側のファイル（`.claude-plugin/marketplace.json` と `plugins/<plugin-name>/.claude-plugin/plugin.json`）を編集する
2. `python scripts/sync_codex_plugins.py` を実行し、Codex CLI 側のファイルを生成・更新する
3. `claude plugin validate .` で検証する

* Codex CLI 側の JSON（`.agents/plugins/marketplace.json`, `plugins/*/.codex-plugin/plugin.json`）は手で編集しないこと。同期が取れていないと pre-commit（`check-codex-plugins`）が失敗する。
* Codex 上のカテゴリを変えたい場合は、`scripts/sync_codex_plugins.py` の `CATEGORIES` を編集する。
* `scripts/convert_skills_to_plugins.py` でプラグインを追加した場合は、手順 2 が自動で実行される。

## 技術スタック

* **エディタ**: Visual Studio Code（VSCode）, Dev Container, Claude Code, Codex CLI
* **バージョン管理**: GitHub
* **CI/CD**: GitHub Actions, pre-commit
* **コード品質**: MarkdownLint, Ruff, pyright
* **セキュリティ**: Dependabot + gitleaks

## 開発ルール

* コミットメッセージには日本語で記述すること（例: "feat: 新しい Skill を追加"）。
* 各スクリプト・設定ファイルには日本語で詳細なコメントを記載すること。
* 一貫性を保つため、コードスタイルやドキュメントのフォーマットは既存のものに従うこと。
* `AGENTS.md` のディレクトリ構成や技術スタックは常に最新の状態に保つこと。
