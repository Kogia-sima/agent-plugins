#!/usr/bin/env bash

# 本スクリプトでエラーが発生した場合は即座に終了する
set -euo pipefail

# pipを最新版に更新
pip install --user --upgrade pip

# Ruff (Pythonの静的解析ツール) をインストール
pip install --user ruff

if [ -f ".pre-commit-config.yaml" ]; then
    # 既存のフックスクリプトが残っていると権限エラーになるため、事前に削除しておく
    rm -f .git/hooks/*
    # フックスクリプトを `.git/hooks/` にインストール
    pre-commit install
    # フック実行に必要な依存関係をインストール
    pre-commit install --install-hooks
fi
