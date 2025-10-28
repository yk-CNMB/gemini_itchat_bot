#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
import time
import logging
import subprocess
import itchat
from itchat.content import TEXT
from google import generativeai as genai

# ------------------------------
CONFIG_FILE = "config.json"
LOG_FILE = "chat.log"
SCRIPT_FILE = "bot.py"

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

# ------------------------------
def load_config():
    default = {
        "gemini_api_key": "",
        "model": "gemini-pro",
        "prompt_prefix": "",
        "max_tokens": 300,
        "temperature": 0.7,
        "github_repo": ""  # 用于一键更新
    }
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            cfg = json.load(f)
        default.update(cfg)
    return default

config = load_config()
genai.configure(api_key=config["gemini_api_key"])

# ------------------------------
@itchat.msg_register(TEXT)
def handle_msg(msg):
    user_text = msg.get('Text', '')
    username = msg.get('FromUserName', '')
    logging.info(f"收到消息: {user_text} 来自: {username}")

    prompt = f"{config['prompt_prefix']}\n用户: {user_text}\nAI:"
    try:
        reply = genai.generate_text(
            model=config["model"],
            prompt=prompt,
            max_output_tokens=config["max_tokens"]
        )
        text = reply.text.strip()
    except Exception as e:
        text = "抱歉，AI 服务暂时不可用"
        logging.error(f"AI 回复失败: {e}")

    logging.info(f"回复消息: {text}")
    return text

# ------------------------------
def update_from_github():
    """从 GitHub 更新自身代码"""
    if not config.get("github_repo"):
        print("未配置 github_repo，跳过更新")
        return
    try:
        subprocess.run(["git", "pull", "origin", "main"], check=True)
        subprocess.run(["pip", "install", "-r", "requirements.txt"], check=True)
        print("更新完成！请重新启动 bot.py")
        exit(0)
    except Exception as e:
        logging.error(f"更新失败: {e}")

# ------------------------------
def login_and_run():
    while True:
        try:
            print("请扫码登录微信……")
            itchat.auto_login(hotReload=True)
            print("登录成功！正在监听消息……")
            itchat.run(blockThread=True)
        except Exception as e:
            logging.error(f"运行出错: {e}, 5秒后重连……")
            time.sleep(5)
            continue

# ------------------------------
if __name__ == "__main__":
    print("建议使用后台运行: nohup python3 bot.py &")
    update_from_github()
    login_and_run()
