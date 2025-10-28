#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Gemini + itchat chatbot
Features:
- Text replies in private chat and group chat. In groups, replies only when @mentioned or when command prefix used.
- Hot-reload login (hotReload=True) to keep session between restarts.
- Uses a configurable prompt template stored in `settings.json` (can be edited easily).
- Logs messages and replies to `bot.log`.
- Supports admin commands via private chat to change prompt at runtime (requires admin list in settings).
- Safe defaults; does not store API keys in repo. Use environment variables or .env.
"""
import os
import itchat
import json
import logging
import threading
import time
from google import generativeai as genai
from datetime import datetime

# --------- Configuration ---------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SETTINGS_PATH = os.path.join(BASE_DIR, 'settings.json')
LOG_PATH = os.path.join(BASE_DIR, 'bot.log')

# Load settings (editable)
default_settings = {
    "admin_users": [],               # list of WeChat Nicknames allowed to use admin commands
    "reply_prefix": "!ai",           # prefix to trigger bot in group when not @mentioned
    "model_name": "gemini-1.5-pro",  # default model
    "max_output_tokens": 512,
    "prompt_template": "You are a helpful assistant. {history}\nUser: {message}\nAssistant:"
}

if not os.path.exists(SETTINGS_PATH):
    with open(SETTINGS_PATH, 'w', encoding='utf-8') as f:
        json.dump(default_settings, f, ensure_ascii=False, indent=2)

def load_settings():
    with open(SETTINGS_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_settings(settings):
    with open(SETTINGS_PATH, 'w', encoding='utf-8') as f:
        json.dump(settings, f, ensure_ascii=False, indent=2)

settings = load_settings()

# --------- Logging ---------
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s',
    handlers=[logging.FileHandler(LOG_PATH, encoding='utf-8'), logging.StreamHandler()]
)

# --------- Gemini setup ---------
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')
if GEMINI_API_KEY:
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        logging.info('Gemini configured.')
    except Exception as e:
        logging.exception('Failed to configure Gemini: %s', e)
else:
    logging.warning('GEMINI_API_KEY not set. Set it in environment or start.sh before running.')

MODEL = settings.get('model_name', 'gemini-1.5-pro')
MAX_OUTPUT_TOKENS = settings.get('max_output_tokens', 512)

# --------- Simple in-memory conversation history (per user) ---------
# For privacy, history is kept only in memory and limited size.
user_history = {}  # { user_id: [ (role, text), ... ] }
HISTORY_MAX = 6  # keep last N exchanges

def append_history(user_id, role, text):
    hist = user_history.get(user_id, [])
    hist.append((role, text))
    if len(hist) > HISTORY_MAX * 2:
        hist = hist[-HISTORY_MAX*2:]
    user_history[user_id] = hist

def build_history_text(user_id):
    hist = user_history.get(user_id, [])
    parts = []
    for role, t in hist:
        parts.append(f"{role}: {t}")
    return "\n".join(parts)

# --------- Gemini call (synchronous) ---------
def generate_reply(prompt, model=MODEL, max_tokens=MAX_OUTPUT_TOKENS):
    try:
        logging.info('Sending prompt to Gemini (len=%d)', len(prompt))
        response = genai.generate_text(model=model, prompt=prompt, max_output_tokens=max_tokens)
        if hasattr(response, 'text'):
            text = response.text
        elif isinstance(response, dict) and 'candidates' in response and len(response['candidates'])>0:
            text = response['candidates'][0].get('content','')
        else:
            text = str(response)
        text = text.strip()
        logging.info('Gemini replied (len=%d)', len(text))
        return text
    except Exception as e:
        logging.exception('Gemini call failed: %s', e)
        return '抱歉，AI 服务当前不可用，请稍后再试。'

# --------- itchat handlers ---------
@itchat.msg_register(itchat.content.TEXT)
def text_reply(msg):
    """Handle private messages."""
    try:
        from_user = msg['FromUserName']
        nick = msg['User'].get('NickName') or msg['User'].get('RemarkName') or msg['User'].get('UserName')
        text = msg['Text'].strip()
        logging.info('Private message from %s: %s', nick, text)

        # Admin command: setprompt <JSON key> or show settings
        if nick in settings.get('admin_users', []) and text.startswith('/admin '):
            cmd = text[len('/admin '):].strip()
            if cmd.startswith('setprompt '):
                new_prompt = cmd[len('setprompt '):].strip()
                settings['prompt_template'] = new_prompt
                save_settings(settings)
                return '提示词已更新。'
            if cmd == 'showsettings':
                return json.dumps(settings, ensure_ascii=False, indent=2)
            return '未知 admin 命令。'

        # Normal private chat: build prompt and call Gemini
        user_id = from_user
        append_history(user_id, 'User', text)
        history_text = build_history_text(user_id)
        prompt = settings.get('prompt_template', '')\
                 .replace('{history}', history_text)\
                 .replace('{message}', text)

        reply = generate_reply(prompt)
        append_history(user_id, 'Assistant', reply)
        return reply
    except Exception as e:
        logging.exception('Error in private message handler: %s', e)
        return '内部错误。'

@itchat.msg_register(itchat.content.TEXT, isGroupChat=True)
def group_text_reply(msg):
    """Handle group messages. Reply when bot is @mentioned or when message starts with reply_prefix."""
    try:
        text = msg['Text'].strip()
        actual_text = text
        my_nick = itchat.search_friends()['NickName'] if itchat.search_friends() else ''
        mentioned = False
        if my_nick and ('@' + my_nick) in text:
            mentioned = True
            actual_text = text.replace('@' + my_nick, '').strip()

        reply_prefix = settings.get('reply_prefix', '!ai')
        if text.startswith(reply_prefix):
            mentioned = True
            actual_text = text[len(reply_prefix):].strip()

        if not mentioned:
            logging.info('Group message ignored (no mention/prefix).')
            return None

        room_id = msg['FromUserName']
        user_id = msg['ActualNickName'] if 'ActualNickName' in msg else msg['User'].get('NickName', 'group_user')
        append_history(user_id, 'User', actual_text)
        history_text = build_history_text(user_id)
        prompt = settings.get('prompt_template', '')\
                 .replace('{history}', history_text)\
                 .replace('{message}', actual_text)

        reply = generate_reply(prompt)
        append_history(user_id, 'Assistant', reply)

        try:
            return f"@{msg['ActualNickName'] if 'ActualNickName' in msg else ''} {reply}"
        except Exception:
            return reply
    except Exception as e:
        logging.exception('Error in group message handler: %s', e)
        return None

def main():
    logging.info('Starting itchat Gemini bot...')
    itchat.auto_login(hotReload=True)
    itchat.run()

if __name__ == '__main__':
    main()
