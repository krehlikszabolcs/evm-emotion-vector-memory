#!/bin/bash
set -e
cd "$(dirname "$0")"
echo "Choose backend:"
echo "1) LM Studio"
echo "2) OpenAI"
read -r -p "> " choice
case "$choice" in
  1) exec ./start_lmstudio.command ;;
  2) exec ./start_openai.command ;;
  *) echo "Ismeretlen választás"; exit 1 ;;
esac
