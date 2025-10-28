#!/bin/bash
# ------------------------------
# 功能: 一键更新 GitHub 仓库并重启 bot
# 使用方法: bash update_and_run.sh
# ------------------------------

# 项目路径
PROJECT_DIR=~/gemini_itchat_bot
VENV_DIR=$PROJECT_DIR/venv
BOT_LOG=$PROJECT_DIR/bot.log

# 进入项目目录
cd $PROJECT_DIR || { echo "目录不存在: $PROJECT_DIR"; exit 1; }

# 拉取最新代码
echo "拉取最新代码..."
git reset --hard
git pull origin main

# 激活虚拟环境
echo "激活虚拟环境..."
source $VENV_DIR/bin/activate

# 安装依赖
echo "安装依赖..."
pip install -r requirements.txt
pip install --upgrade itchat-uos google-generativeai

# 停止旧的后台进程
echo "停止旧进程..."
pkill -f "python3 bot.py"

# 启动 bot
echo "启动机器人..."
nohup python3 bot.py > $BOT_LOG 2>&1 &

echo "更新完成，机器人已在后台运行，日志: $BOT_LOG"
