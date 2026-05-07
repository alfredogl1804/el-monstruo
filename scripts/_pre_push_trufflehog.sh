#!/usr/bin/env bash
# Pre-push hook (Sprint S-001 task S-1.1)
set -e
if ! command -v trufflehog >/dev/null 2>&1; then
    echo "[skip] trufflehog not installed - install: brew install trufflesecurity/trufflehog/trufflehog"
    exit 0
fi
echo "[trufflehog] scanning last 5 commits..."
trufflehog git file://. --since-commit HEAD~5 --no-update --fail
