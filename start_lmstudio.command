#!/bin/bash
set -e
cd "$(dirname "$0")"
[ -f .env ] || cp .env.example .env
python3 - <<'PY'
from pathlib import Path
p = Path('.env')
lines = []
seen = False
for raw in p.read_text(encoding='utf-8').splitlines():
    if raw.startswith('LLM_PROVIDER='):
        lines.append('LLM_PROVIDER=lmstudio')
        seen = True
    else:
        lines.append(raw)
if not seen:
    lines.append('LLM_PROVIDER=lmstudio')
p.write_text('\n'.join(lines) + '\n', encoding='utf-8')
PY
exec ./start.command
