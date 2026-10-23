"""
Claude Code 用のマニフェストから、Codex CLI 用のマニフェストを生成するスクリプト。

このリポジトリでは Claude Code 側のマニフェストを正本とし、Codex 側のファイルは
本スクリプトで生成する（Codex 側の JSON は手で編集しない）。

    .claude-plugin/marketplace.json            -> .agents/plugins/marketplace.json
    plugins/<name>/.claude-plugin/plugin.json  -> plugins/<name>/.codex-plugin/plugin.json

Skill 本体（skills/<skill-name>/SKILL.md）は両 CLI で共通の形式のため、そのまま共有する。

使い方（リポジトリのルートで実行）:
    python scripts/sync_codex_plugins.py          # Codex 用のマニフェストを生成・更新
    python scripts/sync_codex_plugins.py --check  # 生成結果と既存ファイルの差分を検査のみ
"""

import argparse
import json
import sys
from pathlib import Path

# リポジトリのルートディレクトリ（このスクリプトの 1 つ上の階層）
REPO_ROOT = Path(__file__).resolve().parent.parent

# Claude Code 用マーケットプレイス定義（正本）
CLAUDE_MARKETPLACE_PATH = REPO_ROOT / ".claude-plugin" / "marketplace.json"

# Codex 用マーケットプレイス定義（生成物）
CODEX_MARKETPLACE_PATH = REPO_ROOT / ".agents" / "plugins" / "marketplace.json"

# Codex のマーケットプレイス一覧に表示する名前
MARKETPLACE_DISPLAY_NAME = "Agent Plugins"

# プラグインごとの Codex 上のカテゴリ。ここに無いプラグインは DEFAULT_CATEGORY を使う
CATEGORIES: dict[str, str] = {
    "commit": "Coding",
    "python-testing": "Coding",
}
DEFAULT_CATEGORY = "Productivity"

# Codex マーケットプレイスの各エントリに必須のインストールポリシー
# * installation: AVAILABLE（ユーザが選んだときだけインストールする）
# * authentication: ON_INSTALL（認証が必要な場合はインストール時に行う）
DEFAULT_POLICY = {"installation": "AVAILABLE", "authentication": "ON_INSTALL"}


def load_json(path: Path) -> dict[str, object]:
    """JSON ファイルを読み込み、辞書として返す。"""
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise TypeError(f"JSON のトップレベルがオブジェクトではありません: {path}")
    return data


def dump_json(data: object) -> str:
    """JSON を 2 スペースインデント・日本語そのまま・末尾改行ありの文字列にする。

    `convert_skills_to_plugins.py` の出力形式と揃えている。
    """
    return json.dumps(data, ensure_ascii=False, indent=2) + "\n"


def category_of(name: str) -> str:
    """プラグイン名から Codex 上のカテゴリを決める。"""
    return CATEGORIES.get(name, DEFAULT_CATEGORY)


def build_codex_plugin(claude_manifest: dict[str, object]) -> dict[str, object]:
    """Claude Code 用 plugin.json から Codex 用 plugin.json の内容を組み立てる。"""
    name = str(claude_manifest["name"])
    description = str(claude_manifest.get("description", ""))

    manifest: dict[str, object] = {"name": name}
    # 識別情報（バージョン・説明・作者）は Claude Code 側の値をそのまま引き継ぐ
    for key in ("version", "description", "author"):
        if key in claude_manifest:
            manifest[key] = claude_manifest[key]

    # Codex は skills の場所を明示する必要がある（プラグインルートからの相対パス）
    manifest["skills"] = "./skills/"

    # Codex のプラグインブラウザに表示する情報
    interface: dict[str, object] = {
        "displayName": name,
        "shortDescription": description,
        "category": category_of(name),
    }
    author = claude_manifest.get("author")
    if isinstance(author, dict) and "name" in author:
        interface["developerName"] = author["name"]
    manifest["interface"] = interface
    return manifest


def build_codex_marketplace(claude_marketplace: dict[str, object]) -> dict[str, object]:
    """Claude Code 用 marketplace.json から Codex 用 marketplace.json の内容を組み立てる。"""
    plugins = claude_marketplace.get("plugins", [])
    assert isinstance(plugins, list)

    entries: list[dict[str, object]] = []
    for plugin in plugins:
        assert isinstance(plugin, dict)
        name = str(plugin["name"])
        entries.append(
            {
                "name": name,
                # Codex の source.path もマーケットプレイスのルート（リポジトリルート）からの相対パス
                "source": {"source": "local", "path": plugin["source"]},
                "policy": DEFAULT_POLICY,
                "category": category_of(name),
            }
        )

    return {
        # `<plugin-name>@agent-plugins` の形で参照できるよう Claude Code 側と名前を揃える
        "name": claude_marketplace["name"],
        "interface": {"displayName": MARKETPLACE_DISPLAY_NAME},
        "plugins": entries,
    }


def generate() -> dict[Path, str]:
    """生成すべき Codex 用ファイルの「パス -> 内容」を返す。"""
    claude_marketplace = load_json(CLAUDE_MARKETPLACE_PATH)
    outputs: dict[Path, str] = {
        CODEX_MARKETPLACE_PATH: dump_json(build_codex_marketplace(claude_marketplace))
    }

    for claude_path in sorted(REPO_ROOT.glob("plugins/*/.claude-plugin/plugin.json")):
        plugin_dir = claude_path.parent.parent
        codex_path = plugin_dir / ".codex-plugin" / "plugin.json"
        outputs[codex_path] = dump_json(build_codex_plugin(load_json(claude_path)))
    return outputs


def sync() -> list[Path]:
    """Codex 用ファイルを生成・更新し、書き換えたファイルの一覧を返す。

    `convert_skills_to_plugins.py` からも呼び出される。
    """
    updated: list[Path] = []
    for path, content in generate().items():
        if path.exists() and path.read_text(encoding="utf-8") == content:
            continue
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        updated.append(path)
    return updated


def check() -> list[Path]:
    """生成結果と既存ファイルを比較し、差分のあるファイルの一覧を返す（書き込みはしない）。"""
    return [
        path
        for path, content in generate().items()
        if not path.exists() or path.read_text(encoding="utf-8") != content
    ]


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Claude Code 用マニフェストから Codex CLI 用マニフェストを生成する"
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="ファイルを書き込まず、Codex 用マニフェストが最新かどうかの検査のみ行う",
    )
    args = parser.parse_args()

    if args.check:
        outdated = check()
        for path in outdated:
            print(f"[OUTDATED] {path.relative_to(REPO_ROOT)}", file=sys.stderr)
        if outdated:
            print(
                "\nCodex 用マニフェストが Claude Code 用マニフェストと一致しません。"
                "`python scripts/sync_codex_plugins.py` を実行してください。",
                file=sys.stderr,
            )
            return 1
        return 0

    updated = sync()
    for path in updated:
        print(f"[UPDATE] {path.relative_to(REPO_ROOT)}")
    print(f"\n更新: {len(updated)} 件")
    return 0


if __name__ == "__main__":
    sys.exit(main())
