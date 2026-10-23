"""
コミットメッセージに日本語が含まれているかをチェックするスクリプト。
"""

import re
import sys


# ひらがな・カタカナ・漢字のいずれかにマッチする正規表現パターン
JAPANESE_PATTERN = re.compile(r"[\u3040-\u9FFF\uF900-\uFAFF]")

# 除外対象のプレフィックスパターン
SKIP_PATTERNS = re.compile(
    r"^("
    r"Merge\s"  # Merge commit（例: "Merge branch 'main'"）
    r"|Revert\s"  # Revert commit（例: "Revert "feat: ..."）
    r"|(amend|fixup|squash)!\s"  # autosquash commit（例: "fixup! feat: ..."）
    r")"
)


def main():
    # commit-msgフックの第1引数にはコミットメッセージが記載されたファイルのパスが渡される
    commit_msg_file = sys.argv[1]

    with open(commit_msg_file, encoding="utf-8") as f:
        commit_msg = f.read().strip()

    # 除外対象のコミットはチェックをスキップ
    if SKIP_PATTERNS.match(commit_msg):
        sys.exit(0)

    # コミットメッセージに日本語が1文字以上含まれていれば正常終了
    if JAPANESE_PATTERN.search(commit_msg):
        sys.exit(0)

    # エラーメッセージ (文字化けを防ぐために英語で表示)
    print("error: Commit message must contain Japanese characters.", file=sys.stderr)
    sys.exit(1)


if __name__ == "__main__":
    main()
