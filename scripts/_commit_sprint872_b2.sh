#!/usr/bin/env bash
set -euo pipefail
cd ~/el-monstruo
git stash push -u -m "sprint872_b2_pre" || true
git pull --rebase origin main
git stash pop || echo "no stash"
git add kernel/e2e/screenshot/ tests/test_sprint87_2_screenshot.py scripts/_commit_sprint872_b2.sh
git status --short
git commit -m "feat(sprint872-b2): Screenshot capture con Playwright headless

Componentes:
- kernel/e2e/screenshot/capture.py (~190 LOC): Playwright async, full-page PNG.
- Storage default /tmp/monstruo_screenshots, configurable via env.
- Timeout duro 30s por screenshot, cap maximo 5 MB.
- Fallback: si Playwright no instalado, URL es preview, o tira excepcion ->
  ScreenshotResult con playwright_available=False y fallback_reason explicito.
- Privacy-first: cero servicios externos.

Capa Memento: validacion post-captura limita tamano (anti-DoS).
Brand DNA: e2e_screenshot_capture_failed, e2e_screenshot_timeout, etc.

Tests: 6/6 PASS

Co-authored-by: Manus Memento <ejecutor@elmonstruo.local>"
git push origin main
git log --oneline -4
