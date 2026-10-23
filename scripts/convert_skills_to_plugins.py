"""
`.skills/` 配下の Skill アーカイブ（*.skill）を、それぞれ独立したプラグインに変換するスクリプト。

1 つの Skill を 1 つのプラグインとして、次の構成で `plugins/` 配下に展開する。

    plugins/<skill-name>/
    ├── .claude-plugin/
    │   └── plugin.json          # プラグインのマニフェスト
    └── skills/<skill-name>/     # アーカイブの中身（SKILL.md や references/ など）

あわせて `.claude-plugin/marketplace.json` にプラグインのエントリを追加し、
`sync_codex_plugins.py` を呼び出して Codex CLI 用のマニフェスト
（`.codex-plugin/plugin.json` と `.agents/plugins/marketplace.json`）も生成する。
次のいずれかに当てはまる Skill は「プラグイン化済み」とみなしてスキップする。

* `plugins/<skill-name>/` ディレクトリが既に存在する
* 既存のいずれかのプラグインに `skills/<skill-name>/` が含まれている

使い方（リポジトリのルートで実行）:
    python scripts/convert_skills_to_plugins.py            # 変換を実行
    python scripts/convert_skills_to_plugins.py --dry-run  # 変換内容の確認のみ
"""

import argparse
import json
import re
import stat
import sys
import zipfile
from dataclasses import dataclass
from pathlib import Path, PurePosixPath

# Codex CLI 用マニフェストの生成処理（同じ scripts/ ディレクトリのスクリプト）
from sync_codex_plugins import sync as sync_codex_plugins

# リポジトリのルートディレクトリ（このスクリプトの 1 つ上の階層）
REPO_ROOT = Path(__file__).resolve().parent.parent

# 新規作成するプラグインに設定する初期バージョン
DEFAULT_VERSION = "0.1.0"

# SKILL.md 先頭の YAML フロントマター（--- で囲まれた部分）を抽出する正規表現
FRONTMATTER_PATTERN = re.compile(r"\A---\s*\n(.*?)\n---\s*(?:\n|\Z)", re.DOTALL)

# プラグイン名・Skill 名として許可する形式（小文字英数字とハイフンのみ）
NAME_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


@dataclass
class SkillArchive:
    """展開前の Skill アーカイブの情報。"""

    # アーカイブファイルのパス
    path: Path
    # Skill 名（SKILL.md の name。プラグイン名としても使う）
    name: str
    # SKILL.md の description
    description: str
    # アーカイブ内のトップレベルディレクトリ名（例: "adr-writer/"）
    root_prefix: str


def parse_frontmatter(text: str) -> dict[str, str]:
    """SKILL.md のフロントマターから `key: value` 形式の項目を辞書で返す。

    PyYAML に依存しないよう、1 行 1 項目の単純な形式のみ解釈する。
    値を囲む引用符（" または '）は取り除く。
    """
    match = FRONTMATTER_PATTERN.match(text)
    if match is None:
        return {}

    result: dict[str, str] = {}
    for line in match.group(1).splitlines():
        # インデントされた行（複数行の値の続きなど）は対象外
        if not line or line[0].isspace() or ":" not in line:
            continue
        key, value = line.split(":", 1)
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
            value = value[1:-1]
        result[key.strip()] = value
    return result


def summarize_description(description: str) -> str:
    """Skill の description から、プラグイン説明用に最初の 1 文を取り出す。

    Skill の description は発動条件まで含む長文になりがちなため、
    マーケットプレイスの一覧で読みやすいよう先頭の文だけを使う。
    """
    first_sentence = description.split("。", 1)[0].strip()
    return first_sentence or description.strip()


def load_skill_archive(path: Path) -> SkillArchive:
    """Skill アーカイブを検査し、Skill 名などの情報を読み取る。

    アーカイブは `<skill-name>/SKILL.md` を含む単一ディレクトリ構成であることを前提とする。
    想定外の構成や危険なパスを含む場合は ValueError を送出する。
    """
    with zipfile.ZipFile(path) as zf:
        names = zf.namelist()

        # パストラバーサル（絶対パスや ".." を含むエントリ）を拒否する
        for entry in names:
            entry_path = PurePosixPath(entry)
            if entry_path.is_absolute() or ".." in entry_path.parts:
                raise ValueError(f"不正なパスを含んでいます: {entry}")

        # トップレベルのディレクトリがちょうど 1 つであることを確認する
        roots = {PurePosixPath(entry).parts[0] for entry in names}
        if len(roots) != 1:
            raise ValueError(
                f"トップレベルのディレクトリが 1 つではありません: {sorted(roots)}"
            )
        root = roots.pop()

        skill_md = f"{root}/SKILL.md"
        if skill_md not in names:
            raise ValueError(f"{skill_md} が見つかりません")
        frontmatter = parse_frontmatter(zf.read(skill_md).decode("utf-8"))

    # Skill 名は SKILL.md の name を優先し、無ければディレクトリ名を使う
    name = frontmatter.get("name") or root
    if not NAME_PATTERN.match(name):
        raise ValueError(f"Skill 名が kebab-case ではありません: {name}")

    return SkillArchive(
        path=path,
        name=name,
        description=frontmatter.get("description", ""),
        root_prefix=f"{root}/",
    )


def is_already_plugin(plugins_dir: Path, skill_name: str) -> bool:
    """指定した Skill が既にプラグイン化されているかを判定する。"""
    # 同名のプラグインディレクトリが存在する
    if (plugins_dir / skill_name).exists():
        return True
    # 既存プラグインのいずれかに同名の Skill が含まれている
    return any(plugins_dir.glob(f"*/skills/{skill_name}/SKILL.md"))


def extract_skill(archive: SkillArchive, dest_dir: Path) -> None:
    """アーカイブの中身を `dest_dir`（skills/<skill-name>/）へ展開する。

    トップレベルのディレクトリ名は取り除き、実行権限はアーカイブの設定を引き継ぐ。
    """
    with zipfile.ZipFile(archive.path) as zf:
        for info in zf.infolist():
            relative = info.filename.removeprefix(archive.root_prefix)
            if not relative or info.is_dir():
                continue

            target = dest_dir / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(zf.read(info))

            # zip の external_attr 上位 16 ビットに Unix のパーミッションが入っている
            mode = info.external_attr >> 16
            if mode & stat.S_IXUSR:
                target.chmod(
                    target.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH
                )


def write_json(path: Path, data: object) -> None:
    """JSON を 2 スペースインデント・日本語そのまま・末尾改行ありで書き出す。"""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def find_marketplace_entry(
    marketplace: dict[str, object], name: str
) -> dict[str, object] | None:
    """marketplace.json の plugins から、指定した名前のエントリを探す。"""
    plugins = marketplace.get("plugins", [])
    assert isinstance(plugins, list)
    for entry in plugins:
        if isinstance(entry, dict) and entry.get("name") == name:
            return entry  # type: ignore[return-value]
    return None


def main() -> int:
    parser = argparse.ArgumentParser(
        description="`.skills/` の Skill アーカイブをプラグインに変換する"
    )
    parser.add_argument(
        "--skills-dir",
        type=Path,
        default=REPO_ROOT / ".skills",
        help="Skill アーカイブ（*.skill）の格納ディレクトリ（既定: .skills）",
    )
    parser.add_argument(
        "--plugins-dir",
        type=Path,
        default=REPO_ROOT / "plugins",
        help="プラグインの出力先ディレクトリ（既定: plugins）",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="ファイルを書き込まず、実行内容の表示のみ行う",
    )
    args = parser.parse_args()

    skills_dir: Path = args.skills_dir
    plugins_dir: Path = args.plugins_dir
    dry_run: bool = args.dry_run
    marketplace_path = REPO_ROOT / ".claude-plugin" / "marketplace.json"

    archives = sorted(skills_dir.glob("*.skill"))
    if not archives:
        print(f"Skill アーカイブが見つかりません: {skills_dir}")
        return 0

    marketplace = json.loads(marketplace_path.read_text(encoding="utf-8"))
    marketplace_plugins = marketplace.setdefault("plugins", [])

    # プラグインの作者情報はマーケットプレイスの owner を流用する
    author = marketplace.get("owner")

    converted: list[str] = []
    skipped: list[str] = []
    failed: list[str] = []

    for archive_path in archives:
        try:
            archive = load_skill_archive(archive_path)
        except (ValueError, zipfile.BadZipFile, UnicodeDecodeError) as e:
            print(f"[ERROR] {archive_path.name}: {e}", file=sys.stderr)
            failed.append(archive_path.name)
            continue

        if is_already_plugin(plugins_dir, archive.name):
            print(f"[SKIP]  {archive.name}: プラグイン化済み")
            skipped.append(archive.name)
            continue

        # marketplace.json に手書きの説明が既にあればそれを優先し、
        # 無ければ SKILL.md の description の先頭 1 文を使う
        entry = find_marketplace_entry(marketplace, archive.name)
        if entry is not None and isinstance(entry.get("description"), str):
            description = str(entry["description"])
        else:
            description = summarize_description(archive.description)

        plugin_dir = plugins_dir / archive.name
        manifest: dict[str, object] = {
            "name": archive.name,
            "description": description,
            "version": DEFAULT_VERSION,
        }
        if author is not None:
            manifest["author"] = author

        print(f"[ADD]   {archive.name} -> {plugin_dir.relative_to(REPO_ROOT)}")
        if not dry_run:
            extract_skill(archive, plugin_dir / "skills" / archive.name)
            write_json(plugin_dir / ".claude-plugin" / "plugin.json", manifest)

        # marketplace.json に未登録の場合のみエントリを追加する
        if entry is None:
            marketplace_plugins.append(
                {
                    "name": archive.name,
                    "source": f"./{plugin_dir.relative_to(REPO_ROOT).as_posix()}",
                    "description": description,
                }
            )
        converted.append(archive.name)

    if converted and not dry_run:
        write_json(marketplace_path, marketplace)
        # Claude Code 側の変更を Codex CLI 用マニフェストにも反映する
        for path in sync_codex_plugins():
            print(f"[CODEX] {path.relative_to(REPO_ROOT)}")

    print(
        f"\n変換: {len(converted)} 件 / スキップ: {len(skipped)} 件 / 失敗: {len(failed)} 件"
    )
    if converted and not dry_run:
        print("`claude plugin validate .` で検証してください。")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
