#!/bin/bash

cd "$(dirname "$0")"

LOGFILE="bot.log"
VENV="venv"

# -------------------------------
# 激活虚拟环境
if [ ! -d "$VENV" ]; then
    echo "创建虚拟环境..."
    python3 -m venv "$VENV"
fi
source "$VENV/bin/activate"

# -------------------------------
# 更新代码
echo "拉取最新代码..."
git pull origin main

# -------------------------------
# 安装依赖
echo "安装依赖..."
pip install -r requirements.txt

# -------------------------------
# 守护运行函数
run_bot() {
    while true; do
        echo "启动 bot..."
        python3 bot.py >> $LOGFILE 2>&1
        echo "bot 崩溃或退出，5秒后重启..."
        sleep 5
    done
}

# -------------------------------
# 判断登录状态
if [ ! -f ".itchat.pkl" ]; then
    echo "首次运行，前台扫码登录..."
    python3 bot.py
else
    echo "已有登录状态，后台守护运行 bot..."
    nohup bash -c run_bot &  # 后台守护
    echo "机器人已启动，日志输出到 $LOGFILE"
fi
