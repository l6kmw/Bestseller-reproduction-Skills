#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

rm -rf _temp/example-smoke

python3 scripts/run_workflow.py \
  --texts examples/example-viral-reference-notes.md \
  --product templates/example-product-brief.yaml \
  --workdir _temp/example-smoke \
  --duration 30 \
  --platform "TikTok/Reels/Shorts/独立站" \
  --prompt-only

test -s _temp/example-smoke/final/ecommerce-viral-remix-package.md

python3 scripts/validate_package.py \
  examples/example-output-sample.md \
  --brand-terms \
  --require-safety

echo "PASS smoke test"
