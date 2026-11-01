#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"
echo "=== J.A.R.V.I.S. o'rnatilmoqda ==="
command -v python3 >/dev/null || { echo "Python 3.11+ o'rnating: https://www.python.org/downloads/"; exit 1; }
if [ "$(uname)" = "Linux" ]; then
  echo "Linux uchun kerak bo'lishi mumkin: sudo apt install python3-tk python3-venv libportaudio2"
fi
python3 -m venv .venv
. .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
[ -f .env ] || cp .env.example .env
echo
echo "Tayyor! .env faylini oching va API kalitingizni yozing, so'ng ./start.sh ni ishga tushiring."
