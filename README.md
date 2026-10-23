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

| プラグイン | バージョン | 内容 | 主なコマンド |
| --- | --- | --- | --- |

