#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
import time
import logging

try:
    import itchat_uos as itchat
except ImportError:
    import itchat

from google import generativeai as genai

# ------------------------------
# 配置路径与日志
CONFIG_FILE = "config.json"
LOG_FILE = "chat.log"
HOT_RELOAD_FILE = "itchat.pkl"

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
# 消息注册兼容
try:
    TEXT = itchat.content.TEXT
except AttributeError:
    TEXT = 'Text'

@itchat.msg_register(TEXT)
def handle_msg(msg):
    user_text = msg.text
    username = msg.fromUserName
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
# 登录函数（带防循环逻辑）
def safe_login():
    """确保不会无限循环登录"""
    for attempt in range(3):
        try:
            first_time = not os.path.exists(HOT_RELOAD_FILE)
            print("首次登录，生成二维码..." if first_time else "尝试使用缓存登录...")

            itchat.auto_login(
                hotReload=not first_time,
                enableCmdQR=2,
                loginCallback=lambda: print("✅ 微信登录成功！"),
                exitCallback=lambda: print("⚠️ 微信已退出。")
            )

            if itchat.originInstance.isLogging:
                print("登录状态异常，重新尝试...")
                time.sleep(3)
                continue

            print("登录成功，开始监听消息。")
            return True
        except Exception as e:
            logging.error(f"登录出错: {e}")
            time.sleep(5)
    print("登录失败，请检查网络或微信状态。")
    return False

# ------------------------------
def main_loop():
    """主循环"""
    while True:
        if safe_login():
            try:
                itchat.run(blockThread=True)
            except Exception as e:
                logging.error(f"运行出错: {e}")
                print("运行出错，5 秒后重启登录...")
                time.sleep(5)
        else:
            print("连续登录失败，等待 10 秒后重试。")
            time.sleep(10)

# ------------------------------
if __name__ == "__main__":
    print("建议后台运行: nohup python3 bot.py &")
    main_loop()
