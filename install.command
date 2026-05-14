#!/bin/bash
set -e
cd "$(dirname "$0")"
echo "Starting EVM Experimental Test Environment setup..."
/usr/bin/python3 --version >/dev/null 2>&1 || { echo "Python 3 was not found on this system."; exit 1; }
[ -d .venv ] || /usr/bin/python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt
[ -f .env ] || cp .env.example .env
printf "Provider [openai/lmstudio/xai] (Enter=openai): "
IFS= read -r PROVIDER
[ -n "$PROVIDER" ] || PROVIDER="openai"
PROVIDER=$(printf "%s" "$PROVIDER" | tr '[:upper:]' '[:lower:]')
APIKEY=""
if [ "$PROVIDER" = "openai" ]; then
  printf "OpenAI API key: "
  IFS= read -r APIKEY
elif [ "$PROVIDER" = "xai" ]; then
  printf "xAI API key: "
  IFS= read -r APIKEY
fi
PROVIDER_FOR_WRITE="$PROVIDER" APIKEY_FOR_WRITE="$APIKEY" python3 - <<'PY'
from pathlib import Path
import os
provider = os.environ.get('PROVIDER_FOR_WRITE', 'openai').strip().lower() or 'openai'
key = os.environ.get('APIKEY_FOR_WRITE', '').strip()
p = Path('.env')
config = {}
for raw in p.read_text(encoding='utf-8').splitlines():
    if '=' in raw and not raw.strip().startswith('#'):
        k,v = raw.split('=',1)
        config[k]=v
config['LLM_PROVIDER'] = provider
config.setdefault('PORT','8765')
config.setdefault('ACTIVE_TURN_WINDOW','4')
config.setdefault('SHOW_DEBUG_PANEL','1')
config.setdefault('SHOW_EV','1')
config.setdefault('SHOW_DIA','1')
config.setdefault('SHOW_SNAPSHOT','1')
config.setdefault('OPENAI_BASE_URL','https://api.openai.com/v1')
config.setdefault('XAI_BASE_URL','https://api.x.ai/v1')
config.setdefault('LMSTUDIO_BASE_URL','http://localhost:1234/v1')
config.setdefault('LMSTUDIO_API_KEY','lm-studio')
config.setdefault('LMSTUDIO_RESPONSE_MODEL','local-model')
config.setdefault('LMSTUDIO_EXTRACTOR_MODEL','local-model')
if provider == 'openai':
    config['OPENAI_API_KEY'] = key
elif provider == 'xai':
    config['XAI_API_KEY'] = key
lines = [f'{k}={v}' for k,v in config.items()]
p.write_text('\n'.join(lines)+'\n', encoding='utf-8')
PY
mkdir -p data app/static
echo "Setup complete. Start with start.command or start_lmstudio.command"
