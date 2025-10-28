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
SESSION_FILE = "itchat.pkl"

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
        "model": "gemini-2.5-flash",
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
# 消息处理函数
@itchat.msg_register('Text')
def handle_msg(msg):
    user_text = msg.get('Text', '')
    username = msg.get('FromUserName', '')
    logging.info(f"收到消息: {user_text} 来自: {username}")

    # 构建 prompt
    prompt = f"{config['prompt_prefix']}\n用户: {user_text}\nAI:"
    try:
        reply = genai.generate_text(
            model=config["model"],
            prompt=prompt,
            max_output_tokens=config["max_tokens"],
            temperature=config["temperature"]
        )
        text = reply.text.strip()
    except Exception as e:
        text = "抱歉，AI 服务暂时不可用"
        logging.error(f"AI 回复失败: {e}")

    logging.info(f"回复消息: {text}")
    return text

# ------------------------------
# 登录与自动重连
def login_with_retry():
    while True:
        try:
            # 尝试加载 session，如果失败删除
            first_login = not os.path.exists(SESSION_FILE)
            if not first_login:
                try:
                    itchat.load_login_status(statusStorageDir=SESSION_FILE)
                except Exception:
                    logging.warning("Session 文件损坏，删除重试...")
                    os.remove(SESSION_FILE)
                    first_login = True

            if first_login:
                logging.info("首次登录，请扫码...")
                itchat.auto_login(
                    hotReload=False,
                    enableCmdQR=2,
                    statusStorageDir=SESSION_FILE,
                    loginCallback=lambda: logging.info("首次登录成功！")
                )
            else:
                logging.info("使用 session 自动登录...")
                itchat.auto_login(
                    hotReload=True,
                    enableCmdQR=2,
                    statusStorageDir=SESSION_FILE,
                    loginCallback=lambda: logging.info("自动登录成功！")
                )

            logging.info("Start auto replying.")
            itchat.run(blockThread=True)

        except Exception as e:
            logging.error(f"运行出错: {e}, 删除 session 并重试...")
            if os.path.exists(SESSION_FILE):
                os.remove(SESSION_FILE)
            time.sleep(5)
            continue

# ------------------------------
# 启动
if __name__ == "__main__":
    print("建议使用后台运行: nohup python3 bot.py &")
    login_with_retry()

