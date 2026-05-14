#!/bin/bash
set -e
cd "$(dirname "$0")"

echo "Ez eltávolítja a helyi virtuális környezetet és a cache-eket."
printf "Folytatod? [y/N]: "
IFS= read -r ANSWER
ANSWER=$(printf "%s" "$ANSWER" | tr '[:upper:]' '[:lower:]')
if [ "$ANSWER" != "y" ]; then
  echo "Megszakítva."
  exit 0
fi

rm -rf .venv
find . -type d -name "__pycache__" -prune -exec rm -rf {} +
find . -type f -name "*.pyc" -delete

echo
printf "Töröljem a helyi memóriát is (DATA/sqlite/evm.sqlite3, WAL/SHM és a DATA/logs tükrözött logjai)? [y/N]: "
IFS= read -r WIPE
WIPE=$(printf "%s" "$WIPE" | tr '[:upper:]' '[:lower:]')
if [ "$WIPE" = "y" ]; then
  rm -f DATA/sqlite/evm.sqlite3 DATA/sqlite/evm.sqlite3-shm DATA/sqlite/evm.sqlite3-wal
  rm -f DATA/logs/*.ndjson 2>/dev/null || true
  echo "A helyi memória is törölve lett."
else
  echo "A helyi memória megmaradt."
fi

echo "Uninstall kész."
