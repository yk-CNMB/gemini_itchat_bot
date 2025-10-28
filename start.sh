#!/bin/bash
# Start script for Gemini-itchat bot
set -e
BASE_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$BASE_DIR"
if [ ! -d "venv" ]; then
  python3 -m venv venv
fi
source venv/bin/activate
pip install -r requirements.txt
# set environment variables here or use systemd with Environment= lines
export GEMINI_API_KEY="your_gemini_api_key_here"
# start bot (creates hot reload login file)
python3 bot.py
