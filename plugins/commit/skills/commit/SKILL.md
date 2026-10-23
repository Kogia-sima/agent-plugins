---
name: commit
description: ALWAYS use this skill when committing code changes — never commit directly without it. Creates commits following proper conventional commit format and issue references. Trigger on any commit, git commit, save changes, or commit message task.
metadata:
  author: "Ryohei Machida"
  email: "r-machida@analytics-jp.com"
  created: "2026-07-02"
---

# commit

## 実行手順

1. `git status` と `git diff --staged` で変更内容を確認する
2. 変更がステージされていない場合、 `git add` で変更をステージする
3. 変更内容を分析し、 `git commit` でコミットする
4. コミット時に `hook` 関連のエラーが出た場合は、コードを修正して再度コミットする

## コミットメッセージのフォーマット

```
<type>(<scope>): <subject>

<body>

<footer>
```

## コミットメッセージのルール

* type, subject, body は必須とする (scope, footer は任意)
* subject と body は日本語で記述する
* subject は 50 文字以内で記述する
* body は各行 60 文字以内で記述する
* body には、変更内容だけでなく、変更理由や意図も記述する
* 関連する issue がある場合は、footer に参照を記述する（例: `Fixes #11`, `Refs #12`）

## type の選択基準

| type | 使用場面 |
| --- | --- |
| feat | 新機能の追加 |
| fix | バグ修正 |
| build | ビルド関連の変更 |
| chore | ビルドプロセスや補助ツールの変更 |
| ci | CI関連の変更 |
| docs | ドキュメントのみの変更 |
| perf | パフォーマンス改善 |
| refactor | リファクタリング |
| style | コードの動作に影響しない変更（フォーマット修正など） |
| test | テストの追加・修正 |

## コミットメッセージの例

```
fix(ci): pre-commit が Python ファイルを検出できない問題を修正

ci.yml で checkout の fetch-depth が 1 になっており、差分検出が
正しく動作していなかった。全履歴を取得するよう fetch-depth: 0 に
変更し、変更ファイルのみを対象とする lint が機能するようにした。

Fixes #23
Co-Authored-By: Claude <noreply@anthropic.com>
```
