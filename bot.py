#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
import time
import logging
import itchat
from google import generativeai as genai

# ------------------------------
# 配置文件路径
CONFIG_FILE = "config.json"
LOG_FILE = "chat.log"

# 初始化日志
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

# ------------------------------
# 读取配置
def load_config():
    default = {
        "gemini_api_key": "",
        "model": "gemini-pro",
        "prompt_prefix": "",
        "max_tokens": 300,
        "temperature": 0.7
    }
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            cfg = json.load(f)
        default.update(cfg)
    return default

config = load_config()
genai.configure(api_key=config["gemini_api_key"])

# ------------------------------
# 兼容 itchat TEXT
try:
    TEXT = itchat.content.TEXT
except AttributeError:
    TEXT = "Text"

# ------------------------------
# 消息处理函数
@itchat.msg_register(TEXT)
def handle_msg(msg):
    try:
        username = msg.get('FromUserName') or msg.get('User', '未知用户')
        user_text = msg.get('Text', '')
        logging.info(f"收到消息: {user_text} 来自: {username}")

        prompt = f"{config['prompt_prefix']}\n用户: {user_text}\nAI:"
        reply = genai.generate_text(
            model=config["model"],
            prompt=prompt,
            max_output_tokens=config["max_tokens"]
        )
        text = reply.text.strip()
        logging.info(f"回复消息: {text}")
        return text

    except Exception as e:
        logging.error(f"处理消息失败: {e}, msg={msg}")
        return "抱歉，消息处理失败"

# ------------------------------
# 登录与自动重连
def login_and_run():
    logged_in = False
    while True:
        try:
            if not logged_in:
                print("请扫码登录微信……")
                itchat.auto_login(hotReload=False, enableCmdQR=2)
                logged_in = True
                print("登录成功！正在监听消息……")
            itchat.run(blockThread=True)
        except Exception as e:
            logging.error(f"运行出错: {e}, 5秒后重连……")
            logged_in = False
            time.sleep(5)

# ------------------------------
# 启动入口
if __name__ == "__main__":
    print("建议使用后台运行: nohup python3 bot.py &")
    login_and_run()

