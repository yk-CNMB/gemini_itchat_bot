#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
import time
import logging
import itchat
from google import generativeai as genai

# ====================================================
# 配置区
CONFIG_FILE = "config.json"
LOG_FILE = "bot.log"
CACHE_FILE = os.path.expanduser("itchat.pkl")
# ====================================================

# 初始化日志
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

# ====================================================
# 读取配置
def load_config():
    default = {
        "gemini_api_key": "",
        "model": "model/gemini-2.5-pro",
        "prompt_prefix": "你是一个友好的助手",
        "max_tokens": 300,
        "temperature": 0.7
    }
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            cfg = json.load(f)
        default.update(cfg)
    return default


config = load_config()
if not config["gemini_api_key"]:
    print("⚠️ 请在 config.json 中填写 gemini_api_key！")
genai.configure(api_key=config["gemini_api_key"])

# ====================================================
# 注册消息处理函数
try:
    TEXT = itchat.content.TEXT
except AttributeError:
    TEXT = "Text"


@itchat.msg_register(TEXT)
def handle_msg(msg):
    user_text = msg.get('Text', '')
    user = msg.get('FromUserName', '未知用户')
    logging.info(f"收到消息: {user_text} 来自: {user}")

    prompt = f"{config['prompt_prefix']}\n用户: {user_text}\nAI:"
    try:
        response = genai.generate_text(
            model=config["model"],
            prompt=prompt,
            max_output_tokens=config["max_tokens"],
        )
        reply = response.text.strip()
    except Exception as e:
        reply = "抱歉，AI 服务暂时不可用。"
        logging.error(f"生成回复失败: {e}")

    logging.info(f"回复消息: {reply}")
    return reply


# ====================================================
# 智能登录逻辑
def login_and_run():
    while True:
        try:
            if os.path.exists(CACHE_FILE):
                print("检测到已有登录缓存，尝试使用 hotReload 登录……")
                itchat.auto_login(hotReload=True, enableCmdQR=2, statusStorageDir=CACHE_FILE)
            else:
                print("首次登录，生成二维码……")
                itchat.auto_login(hotReload=False, enableCmdQR=2, statusStorageDir=CACHE_FILE)

            print("✅ 登录成功，开始监听消息……")
            itchat.run(blockThread=True)

        except Exception as e:
            logging.error(f"运行出错: {e}")
            print(f"⚠️ 运行出错: {e}")

            # 如果登录文件损坏则删除
            if os.path.exists(CACHE_FILE):
                os.remove(CACHE_FILE)
                print("已删除旧的登录缓存，准备重新登录。")

            time.sleep(5)
            continue


# ====================================================
# 主入口
if __name__ == "__main__":
    print("💡 建议使用后台运行：nohup python3 bot.py &")
    login_and_run()
