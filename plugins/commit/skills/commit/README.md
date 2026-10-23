# commit

## 概要

Conventional Commits 形式に沿ったコミットを作成する Skill です。

コミット時に必ず本 Skill を経由することで、コミットメッセージのフォーマットとコミット手順をチーム内で統一します。
実行時は以下の手順で動作します。

1. **変更内容の確認**: `git status` と `git diff --staged` で変更内容を確認する
2. **ステージング**: 変更がステージされていない場合、`git add` でステージする
3. **コミット**: 変更内容を分析し、規約に沿ったメッセージでコミットする
4. **エラー対応**: hook 関連のエラーが出た場合は、コードを修正して再コミットする

## 活用例

* **日々のコミット作業**: 変更内容の分析からメッセージ作成・コミットまでを一貫して任せる
* **コミットメッセージの品質統一**: type の選択や日本語での記述ルールをメンバー間で揃える

例: 「この変更をコミットして」「変更を保存して」といった依頼で起動します。

## 使い方

AIエージェント（Claude Code など）で、自然言語でコミットを依頼するか、 `/commit` コマンドを使用して起動します。
変更内容の分析からコミットまでを自動で行います。

## 注意点

* **Skill の経由必須**: コミット時は必ず本 Skill を経由してください。Skill を通さない直接のコミットは、メッセージ規約から外れる可能性があります。
* **スキル未読み込み時のブロック**: 本プラグインには PreToolUse フック（[`hooks/hooks.json`](../../hooks/hooks.json)）が同梱されています。セッション内で本 Skill を読み込まないまま AIエージェントが `git commit` を実行しようとすると、実行が拒否され、先に Skill を読み込むよう促されます。Claude Code と Codex CLI の両方で動作します。
* **Codex CLI でのフックの承認**: Codex CLI では、プラグインに同梱されたフックはレビュー（承認）するまで実行されません。インストール後に `/hooks` を開き、本プラグインのフックを承認してください。
* **ステージ内容の確認**: 意図しない変更が `git add` でステージされないよう、コミット前に変更内容を確認してください。
* **pre-commit との併用**: AIエージェントは完璧ではありません。[conventional-pre-commit](https://github.com/compilerla/conventional-pre-commit) などの commit フックと併用することを推奨します。

## 参考資料

* [Conventional Commits](https://www.conventionalcommits.org/ja/) — コミットメッセージ規約
* [Sentry Commit Message Guidelines](https://develop.sentry.dev/engineering-practices/commit-messages/) — 本 Skill が参考にしている Sentry の規約
* [SKILL.md](./SKILL.md) — 本 Skill の定義ファイル
