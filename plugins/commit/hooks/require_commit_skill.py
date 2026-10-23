"""
`commit` スキルを読み込まずに `git commit` を実行しようとした場合にブロックする
PreToolUse フック（Claude Code / Codex CLI 共通）。

Bash ツールの実行直前に呼ばれ、標準入力からフック入力（JSON）を受け取る。
コマンドに `git commit` が含まれている場合のみ、セッションの transcript（JSONL）を
走査して `commit` スキルが読み込み済みかを判定し、未読み込みなら実行を拒否する。
フックの入出力形式は両 CLI で共通だが、transcript の形式は CLI ごとに異なるため、
以下のいずれかが記録されていれば「読み込み済み」とみなす。

Claude Code（エントリの type が "user" / "assistant"）:
    * Skill ツールの呼び出し（input.skill が "commit" または "<plugin>:commit"）
    * スキル本文の注入メッセージ（"Base directory for this skill: .../skills/commit"）
      ※ ユーザが `/commit` コマンドで起動した場合はこちらのみが記録される

Codex CLI（エントリの type が "response_item"）:
    * スキル本文の注入メッセージ（"<skill>" で始まり、<name> が commit のもの）
      ※ ユーザが `$commit` でスキルを明示的に指定した場合に記録される
    * `.../skills/commit/SKILL.md` を絶対パスで読むツール呼び出し
      ※ モデルが自らスキルを使うと判断した場合は、シェルで SKILL.md を読む

判定できない場合（入力が壊れている、transcript が読めない等）は、
作業を妨げないよう何もせずに終了する（＝実行を許可する）。
"""

import json
import re
import sys
from pathlib import Path

# 対象のスキル名
SKILL_NAME = "commit"

# `git commit` を検出する正規表現。
# * コマンドの先頭、または区切り文字（; & | ( 空白 など）の直後にある `git` を対象とする
# * `git -C <path> commit` や `git -c key=value commit` のように、
#   サブコマンドの前に置かれたグローバルオプションも許容する
# * `git log --grep commit` のように、別サブコマンドの引数としての "commit" には一致しない
GIT_COMMIT_PATTERN = re.compile(
    r"(?:^|[;&|(`\s])git"
    r"(?:\s+(?:-[Cc]\s+\S+|--?[\w-]+(?:=\S+)?))*"
    r"\s+commit(?:\s|$|[;&|)`])"
)

# スキル本文が注入されたメッセージの先頭行。
# パスの末尾が `skills/commit` であるものを `commit` スキルの読み込みとみなす
# （re.match で使うため、テキストの先頭行にのみ一致する）
SKILL_BASE_DIR_PATTERN = re.compile(
    r"Base directory for this skill: \S*[/\\]skills[/\\]"
    + re.escape(SKILL_NAME)
    + r"\s*$",
    re.MULTILINE,
)

# Codex CLI でスキル本文が注入されたメッセージの <name> 要素。
# プラグイン経由の場合は "<plugin>:commit" の形式になるため、名前空間も許容する
CODEX_SKILL_NAME_PATTERN = re.compile(
    r"<name>(?:[^<:]+:)?" + re.escape(SKILL_NAME) + r"</name>"
)

# Codex CLI のツール呼び出しで、`commit` スキルの SKILL.md を読んだことを表すパス。
# `git add plugins/commit/skills/commit/SKILL.md` のような相対パスでの言及で
# 誤検知しないよう、絶対パス（/ または ~ 始まり）のみを対象とする
CODEX_SKILL_FILE_PATTERN = re.compile(
    r"(?:^|[\s'\"=])[/~]\S*/skills/" + re.escape(SKILL_NAME) + r"/SKILL\.md"
)

# Codex CLI の transcript で、ツール呼び出しを表す payload.type の一覧
CODEX_TOOL_CALL_TYPES = ("function_call", "custom_tool_call", "local_shell_call")

# 拒否時にエージェントへ伝えるメッセージ
DENY_REASON = (
    f"`git commit` を実行する前に `{SKILL_NAME}` スキルを読み込んでください。"
    f"`{SKILL_NAME}` スキル（SKILL.md）を読み込み、その手順とコミットメッセージの"
    "ルールに従ってからコミットし直してください。"
)


def is_git_commit(command: str) -> bool:
    """Bash コマンド文字列に `git commit` が含まれているかを判定する。"""
    return GIT_COMMIT_PATTERN.search(command) is not None


def is_commit_skill_name(name: object) -> bool:
    """Skill ツールに渡されたスキル名が `commit` スキルを指しているかを判定する。

    プラグイン経由の場合は "<plugin>:commit" の形式になるため、名前空間を除いて比較する。
    """
    return isinstance(name, str) and name.split(":")[-1] == SKILL_NAME


def iter_content_blocks(entry: dict[str, object]) -> list[dict[str, object]]:
    """transcript の 1 エントリから、message.content のブロック一覧を取り出す。

    content が文字列の場合は text ブロック 1 つとして扱う。
    """
    message = entry.get("message")
    if not isinstance(message, dict):
        return []
    content = message.get("content")
    if isinstance(content, str):
        return [{"type": "text", "text": content}]
    if isinstance(content, list):
        return [block for block in content if isinstance(block, dict)]
    return []


def claude_entry_loads_skill(entry: dict[str, object]) -> bool:
    """Claude Code の transcript の 1 エントリが `commit` スキルの読み込みを表しているかを判定する。"""
    entry_type = entry.get("type")
    for block in iter_content_blocks(entry):
        # アシスタントによる Skill ツールの呼び出し
        if (
            entry_type == "assistant"
            and block.get("type") == "tool_use"
            and block.get("name") == "Skill"
        ):
            tool_input = block.get("input")
            if isinstance(tool_input, dict) and is_commit_skill_name(
                tool_input.get("skill")
            ):
                return True
        # スキル本文の注入メッセージ（Skill ツール・スラッシュコマンドの両方で記録される）。
        # ツール結果（tool_result）に同じ文字列が含まれていても誤検知しないよう、
        # ユーザ側の text ブロックの先頭行のみを対象とする
        if entry_type == "user" and block.get("type") == "text":
            text = block.get("text")
            if isinstance(text, str) and SKILL_BASE_DIR_PATTERN.match(text):
                return True
    return False


def codex_entry_loads_skill(entry: dict[str, object]) -> bool:
    """Codex CLI の transcript の 1 エントリが `commit` スキルの読み込みを表しているかを判定する。

    Codex CLI の transcript は、各行が {"type": "response_item", "payload": {...}} の形式で、
    payload にモデルとの間でやり取りされたメッセージやツール呼び出しが入る。
    """
    payload = entry.get("payload")
    if not isinstance(payload, dict):
        return False
    payload_type = payload.get("type")

    # `$commit` で明示的に指定されたときに注入される、スキル本文入りのユーザメッセージ
    if payload_type == "message" and payload.get("role") == "user":
        content = payload.get("content")
        blocks = content if isinstance(content, list) else []
        for block in blocks:
            text = block.get("text") if isinstance(block, dict) else None
            if (
                isinstance(text, str)
                and text.startswith("<skill>")
                and CODEX_SKILL_NAME_PATTERN.search(text)
            ):
                return True

    # モデルがシェル等で SKILL.md を読んだツール呼び出し。
    # 引数の形式はツールごとに異なるため、payload 全体を文字列化して検索する
    if payload_type in CODEX_TOOL_CALL_TYPES:
        serialized = json.dumps(payload, ensure_ascii=False)
        if CODEX_SKILL_FILE_PATTERN.search(serialized):
            return True
    return False


def entry_loads_skill(entry: dict[str, object]) -> bool:
    """transcript の 1 エントリが `commit` スキルの読み込みを表しているかを判定する。"""
    if entry.get("type") == "response_item":
        return codex_entry_loads_skill(entry)
    return claude_entry_loads_skill(entry)


def skill_loaded(transcript_path: Path) -> bool:
    """セッションの transcript（JSONL）を走査し、`commit` スキルが読み込み済みかを返す。"""
    with transcript_path.open(encoding="utf-8") as f:
        for line in f:
            try:
                entry = json.loads(line)
            except json.JSONDecodeError:
                # 書き込み途中の行などは読み飛ばす
                continue
            if isinstance(entry, dict) and entry_loads_skill(entry):
                return True
    return False


def main() -> int:
    """フックのエントリポイント。拒否する場合のみ JSON を標準出力へ書き出す。"""
    try:
        hook_input = json.load(sys.stdin)
    except json.JSONDecodeError:
        return 0
    if not isinstance(hook_input, dict):
        return 0

    tool_input = hook_input.get("tool_input")
    command = tool_input.get("command") if isinstance(tool_input, dict) else None
    if not isinstance(command, str) or not is_git_commit(command):
        return 0

    transcript_path = hook_input.get("transcript_path")
    if not isinstance(transcript_path, str):
        return 0
    try:
        if skill_loaded(Path(transcript_path)):
            return 0
    except OSError:
        # transcript が読めない場合は判定できないため許可する
        return 0

    # PreToolUse の決定制御: permissionDecision を "deny" にすると実行が拒否され、
    # permissionDecisionReason がエージェントへ伝えられる（Claude Code / Codex CLI 共通）
    output = {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": DENY_REASON,
        }
    }
    json.dump(output, sys.stdout, ensure_ascii=False)
    return 0


if __name__ == "__main__":
    sys.exit(main())
