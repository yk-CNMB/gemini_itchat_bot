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
SESSION_FILE = "itchat.pkl"
LOG_FILE = "bot.log"

# ------------------------------
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
        "model": "gemini-1.5-flash",
        "prompt_prefix": "你是一个友好的中文智能助手",
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
model = genai.GenerativeModel(config["model"])

# ------------------------------
# 处理文本消息
@itchat.msg_register(itchat.content.TEXT)
def handle_msg(msg):
    user_text = msg.get("Text", "").strip()
    if not user_text:
        return "请发送有效内容～"

    username = msg.get("FromUserName", "")
    logging.info(f"收到消息: {user_text} 来自: {username}")

    # 构建 prompt
    prompt = f"{config['prompt_prefix']}\n用户：{user_text}\nAI："

    try:
        response = model.generate_content(prompt)
        text = response.text.strip() if response and response.text else "（AI无回复）"
    except Exception as e:
        text = "抱歉，AI服务暂时不可用，请稍后再试。"
        logging.error(f"AI 回复失败: {e}")

    logging.info(f"回复消息: {text}")
    return text


# ------------------------------
# 登录与自动重连逻辑
def login_and_run():
    while True:
        try:
            if os.path.exists(SESSION_FILE):
                print("检测到登录缓存，尝试使用热重载登录...")
                itchat.auto_login(hotReload=True, enableCmdQR=2)
            else:
                print("首次登录，生成二维码登录...")
                itchat.auto_login(hotReload=False, enableCmdQR=2)

            print("登录成功！正在监听微信消息...")
            itchat.run(blockThread=True)

        except KeyboardInterrupt:
            print("已手动退出程序。")
            break
        except Exception as e:
            logging.error(f"运行出错：{e}，5秒后重试...")
            print(f"运行出错：{e}，5秒后重试...")
            time.sleep(5)
            continue


# ------------------------------
if __name__ == "__main__":
    print("建议使用后台运行：nohup python3 bot.py &")
    login_and_run()

