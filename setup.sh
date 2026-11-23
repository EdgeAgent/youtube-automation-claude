#!/usr/bin/env bash
# One-command bootstrap: check the environment, print honest next steps.
# It installs nothing and changes nothing — it just tells you where you stand.
set -u
cd "$(dirname "$0")"

echo "YouTube Automation for Muse — environment check"
echo "=================================================="

fail=0

if command -v python3 >/dev/null 2>&1; then
  echo "✓ Python: $(python3 --version 2>&1)"
else
  echo "✗ Python 3 not found — install Python 3.10+ first."
  fail=1
fi

if python3 -c "import PIL" >/dev/null 2>&1; then
  echo "✓ Pillow is installed"
else
  echo "✗ Pillow missing — install it with:  pip install Pillow"
  fail=1
fi

if command -v ffmpeg >/dev/null 2>&1; then
  echo "✓ ffmpeg: $(ffmpeg -version 2>/dev/null | head -1)"
else
  echo "✗ ffmpeg not found — install it (needed to pull real frames from your videos)."
  echo "    Debian/Ubuntu: sudo apt install ffmpeg   macOS: brew install ffmpeg"
  fail=1
fi

if python3 -m pytest --version >/dev/null 2>&1; then
  echo "✓ pytest available (optional, for the test suite)"
else
  echo "· pytest not installed (optional) — run tests later with:  pip install pytest"
fi

echo
if [ "$fail" -eq 0 ]; then
  echo "You're ready. Next steps:"
else
  echo "Fix the ✗ items above, then run ./setup.sh again. Once clean:"
fi
echo "  1. Pick a niche — copy config/niche.example.yaml to config/<your-niche>.yaml"
echo "     (worked examples live in config/examples/)"
echo "  2. Using Muse? Just tell your agent your niche and point it at SKILL.md."
echo "  3. Read docs/packaging-playbook.md — it's the strategy the code enforces."
echo "  4. Run the tests any time with:  python3 -m pytest"
