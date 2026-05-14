#!/bin/bash
set -e
cd "$(dirname "$0")"

if [ ! -d ".venv" ]; then
  echo "The environment is not installed yet. Run install.command first."
  exit 1
fi
if [ ! -f ".env" ]; then
  echo "Missing .env file. Run install.command first."
  exit 1
fi
source .venv/bin/activate
PORT=${PORT:-8765}
python3 - <<'PY'
from dotenv import dotenv_values
cfg = dotenv_values('.env')
provider = (cfg.get('LLM_PROVIDER') or 'openai').strip().lower()
if provider == 'lmstudio':
    print('LM Studio mode. Make sure the server is running at: ' + (cfg.get('LMSTUDIO_BASE_URL') or 'http://localhost:1234/v1'))
elif provider == 'xai':
    key = (cfg.get('XAI_API_KEY') or cfg.get('LLM_API_KEY') or '').strip()
    if not key:
        raise SystemExit('Missing XAI_API_KEY in the .env file.')
else:
    key = (cfg.get('OPENAI_API_KEY') or cfg.get('LLM_API_KEY') or '').strip()
    if not key:
        raise SystemExit('Missing OPENAI_API_KEY in the .env file.')
PY
python3 run.py &
SERVER_PID=$!
cleanup(){ kill $SERVER_PID >/dev/null 2>&1 || true; }
trap cleanup EXIT INT TERM
for i in {1..60}; do
  if curl -s http://127.0.0.1:${PORT}/health >/dev/null 2>&1; then
    open "http://127.0.0.1:${PORT}" || true
    wait $SERVER_PID
    exit $?
  fi
  sleep 0.5
done
echo "The server did not start in time."
exit 1
