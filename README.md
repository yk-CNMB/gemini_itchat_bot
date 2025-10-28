# Gemini Itchat Bot (Raspberry Pi)

This project integrates **itchat** (personal WeChat) with **Google Gemini (gemini-1.5-pro)**.
**WARNING:** Using personal WeChat protocols (itchat) may lead to account restriction or ban on your main WeChat account. Use a secondary/test account.

## Features
- Private chat replies (automatic)
- Group replies when @mentioned or when message starts with configured prefix (default `!ai`)
- Editable prompt template in `settings.json`
- Admin commands: in private chat, an admin may send `/admin setprompt <new prompt>` to update the prompt
- Hot reload login (hotReload=True), keeps session between restarts

## Quick start (on Raspberry Pi)
```bash
unzip gemini_itchat_bot_full.zip
cd gemini_itchat_bot
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
# set your Gemini API key in environment or edit start.sh
export GEMINI_API_KEY="your_gemini_api_key_here"
bash start.sh
```

## Config
Edit `settings.json` to change prompt template, reply prefix, admin users, model, and token limits.

## Admin commands (private chat)

- `/admin setprompt <new prompt>` : replace prompt template

- `/admin showsettings` : show current settings

