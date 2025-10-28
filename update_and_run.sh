#!/bin/bash
# -----------------------------
# update_and_run.sh
# -----------------------------
# 描述: 自动更新代码、安装依赖、运行微信机器人

# 设置项目路径
PROJECT_DIR="$HOME/gemini_itchat_bot"
VENV_DIR="$PROJECT_DIR/venv"
GITHUB_REPO="https://github.com/yk-CNMB/gemini_itchat_bot.git"

# -----------------------------
# 1. 如果项目目录不存在，克隆仓库
if [ ! -d "$PROJECT_DIR" ]; then
    echo "项目目录不存在，正在克隆仓库..."
    git clone "$GITHUB_REPO" "$PROJECT_DIR"
fi

cd "$PROJECT_DIR" || exit 1

# -----------------------------
# 2. 拉取最新代码
echo "正在拉取最新代码..."
git fetch origin
git reset --hard origin/main

# -----------------------------
# 3. 创建虚拟环境（如果不存在）
if [ ! -d "$VENV_DIR" ]; then
    echo "虚拟环境不存在，正在创建..."
    python3 -m venv "$VENV_DIR"
fi

# -----------------------------
# 4. 激活虚拟环境并安装依赖
echo "激活虚拟环境..."
source "$VENV_DIR/bin/activate"

echo "升级 pip..."
pip install --upgrade pip

echo "安装依赖..."
pip install -r requirements.txt

# -----------------------------
# 5. 运行 bot.py
echo "运行 bot.py..."
# 后台运行方式，日志写入 bot.log
nohup python3 bot.py > bot.log 2>&1 &
echo "bot.py 已启动，日志文件: $PROJECT_DIR/bot.log"

# -----------------------------
# 6. 完成
echo "更新并启动完成。"
