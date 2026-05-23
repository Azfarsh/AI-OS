#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

python3 -m venv .venv
# shellcheck disable=SC1091
source .venv/bin/activate

pip install --upgrade pip
pip install -r requirements.txt
pip install -e .

if [[ ! -f .env ]]; then
  cp .env.example .env
  echo "Created .env — add OPENROUTER_API_KEY"
fi

mkdir -p memory/notes memory/chroma sessions logs context

echo "Done. Run: source .venv/bin/activate && ais"
