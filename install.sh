#!/bin/bash

# AI 歌詞轉換系統 - 安裝腳本
# 此腳本將幫助你快速設置開發環境

set -e  # 遇到錯誤時退出

echo "=================================="
echo "AI 歌詞轉換系統 - 自動安裝"
echo "=================================="
echo ""

# 檢查 Python 版本
echo "檢查 Python 版本..."
if ! command -v python3 &> /dev/null; then
    echo "錯誤: 未找到 Python 3"
    echo "請先安裝 Python 3.8 或更高版本"
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo "找到 Python $PYTHON_VERSION"

# 檢查是否需要安裝 ffmpeg
echo ""
echo "檢查音頻處理依賴..."
if ! command -v ffmpeg &> /dev/null; then
    echo "警告: 未找到 ffmpeg"
    echo ""
    echo "ffmpeg 是音頻處理所需的工具，請根據你的作業系統安裝："
    echo "  - macOS:   brew install ffmpeg"
    echo "  - Ubuntu:  sudo apt-get install ffmpeg libsndfile1"
    echo "  - Windows: 從 https://ffmpeg.org/download.html 下載"
    echo ""
    read -p "是否繼續安裝 Python 依賴？(y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
else
    echo "✓ ffmpeg 已安裝"
fi

# 創建虛擬環境
echo ""
echo "創建 Python 虛擬環境..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✓ 虛擬環境已創建"
else
    echo "✓ 虛擬環境已存在"
fi

# 激活虛擬環境
echo ""
echo "激活虛擬環境..."
source venv/bin/activate

# 升級 pip
echo ""
echo "升級 pip..."
pip install --upgrade pip

# 安裝依賴
echo ""
echo "安裝 Python 依賴包..."
pip install -r requirements.txt

echo ""
echo "✓ 依賴安裝完成"

# 設置環境變數
echo ""
if [ ! -f ".env" ]; then
    echo "創建環境配置文件..."
    cp .env.example .env
    echo "✓ 已創建 .env 文件"
    echo ""
    echo "重要: 請編輯 .env 文件並填入你的 OpenAI API Key"
    echo ""
    read -p "是否現在輸入 OpenAI API Key？(y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        read -p "請輸入你的 OpenAI API Key: " api_key
        if [ ! -z "$api_key" ]; then
            sed -i.bak "s/your_openai_api_key_here/$api_key/" .env
            rm .env.bak 2>/dev/null || true
            echo "✓ API Key 已設置"
        fi
    fi
else
    echo "✓ .env 文件已存在"
fi

# 運行測試
echo ""
echo "運行環境測試..."
python test_setup.py

echo ""
echo "=================================="
echo "安裝完成！"
echo "=================================="
echo ""
echo "接下來的步驟："
echo "1. 確保 .env 文件中已填入 OpenAI API Key"
echo "2. 運行 'python app.py' 啟動應用"
echo "3. 在瀏覽器中打開 http://localhost:5000"
echo ""
echo "如需幫助，請查看 README.md 或 QUICKSTART.md"
echo ""
