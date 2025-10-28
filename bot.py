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
HOT_RELOAD_FILE = "itchat.pkl"

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
        user_text = msg.get('Text', '')
        username = msg.get('FromUserName', '')
        logging.info(f"收到消息: {user_text} 来自: {username}")

        prompt = f"{config['prompt_prefix']}\n用户: {user_text}\nAI:"
        reply = genai.generate_text(
            model=config["model"],
            prompt=prompt,
            max_output_tokens=config["max_tokens"]
        )
        text = reply.text.strip() if reply else "抱歉，AI 服务暂时不可用"
        logging.info(f"回复消息: {text}")
        return text
    except Exception as e:
        logging.error(f"handle_msg 异常: {e}")
        return "抱歉，AI 服务暂时不可用"

# ------------------------------
# 登录与运行
def login_and_run():
    first_login = not os.path.exists(HOT_RELOAD_FILE)
    while True:
        try:
            print(f"{'首次登录' if first_login else '使用热登录'}，请扫码（首次）或自动登录……")
            itchat.auto_login(
                hotReload=not first_login,
                enableCmdQR=2,
                loginCallback=lambda: print("登录成功回调")
            )
            print("登录成功！正在监听消息……")
            itchat.run(blockThread=True)
            break  # 登录成功后退出循环
        except Exception as e:
            logging.error(f"运行出错: {e}")
            print(f"运行出错: {e}, 删除无效 session 并重试……")
            if os.path.exists(HOT_RELOAD_FILE):
                os.remove(HOT_RELOAD_FILE)
            first_login = True
            time.sleep(5)

# ------------------------------
# 主入口
if __name__ == "__main__":
    print("建议使用后台运行: nohup python3 bot.py &")
    login_and_run()
