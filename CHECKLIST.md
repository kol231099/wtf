# 部署與使用檢查列表

使用這個檢查列表確保系統正確設置和運行。

## 初次安裝檢查

### 1. 系統需求
- [ ] Python 3.8 或更高版本已安裝
- [ ] pip 已安裝且可用
- [ ] ffmpeg 已安裝（音頻處理需要）
- [ ] 至少 2GB 可用記憶體
- [ ] 至少 1GB 可用磁盤空間

### 2. 專案設置
- [ ] 已下載或克隆專案到本地
- [ ] 已進入專案目錄
- [ ] 目錄結構完整（包含所有 .py 文件）

### 3. 依賴安裝
- [ ] 已創建虛擬環境（可選但推薦）
- [ ] 運行 `pip install -r requirements.txt` 成功
- [ ] 所有依賴包安裝無錯誤

### 4. 環境配置
- [ ] 已複製 `.env.example` 為 `.env`
- [ ] 已在 `.env` 中填入 OpenAI API Key
- [ ] API Key 有效且有足夠額度
- [ ] 已設置 Flask Secret Key（可選）

### 5. 測試
- [ ] 運行 `python test_setup.py` 全部通過
- [ ] OpenAI API 連接測試成功
- [ ] 所有目錄正確創建

## 首次運行檢查

### 1. 啟動應用
- [ ] 運行 `python app.py` 無錯誤
- [ ] 看到啟動信息
- [ ] 顯示 "OpenAI API 已配置: True"
- [ ] 應用運行在 http://localhost:5000

### 2. 訪問界面
- [ ] 在瀏覽器打開 http://localhost:5000
- [ ] 頁面正常載入
- [ ] 界面顯示完整（無 404 錯誤）
- [ ] 可以看到上傳區域

### 3. 健康檢查
- [ ] 訪問 http://localhost:5000/api/health
- [ ] 返回 `{"status": "healthy", "openai_api_configured": true}`

## 首次使用檢查

### 1. 準備測試文件
- [ ] 準備一個原始歌曲文件（WAV 格式，約 1 分鐘）
- [ ] 準備一個純旋律文件（WAV 格式，同樣長度）
- [ ] 準備新歌詞文本

### 2. 上傳測試
- [ ] 可以成功選擇或拖放原始歌曲文件
- [ ] 文件名正確顯示
- [ ] 可以成功選擇或拖放旋律文件
- [ ] 可以在文本框輸入新歌詞

### 3. 處理測試
- [ ] 點擊「開始合成」按鈕
- [ ] 顯示處理進度
- [ ] 可以看到處理步驟
- [ ] 處理完成無錯誤

### 4. 結果驗證
- [ ] 顯示結果區域
- [ ] 可以播放最終混合音頻
- [ ] 可以播放純人聲音頻
- [ ] 可以下載生成的文件
- [ ] 顯示 AI 分析結果

## 常見問題排查

### Python 版本問題
```bash
# 檢查版本
python3 --version

# 如果版本太低，需要升級
# macOS: brew install python@3.10
# Ubuntu: sudo apt-get install python3.10
```

### 依賴安裝失敗
```bash
# 升級 pip
pip install --upgrade pip

# 單獨安裝可能有問題的包
pip install librosa
pip install soundfile
pip install openai
```

### ffmpeg 未安裝
```bash
# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt-get install ffmpeg libsndfile1

# Windows
# 從 https://ffmpeg.org/download.html 下載
```

### OpenAI API 錯誤
- [ ] 檢查 API Key 是否正確
- [ ] 檢查賬戶是否有額度
- [ ] 檢查網絡連接
- [ ] 運行 `curl https://api.openai.com/v1/models -H "Authorization: Bearer YOUR_API_KEY"`

### 文件上傳失敗
- [ ] 檢查文件大小是否超過 50MB
- [ ] 檢查文件格式是否支持
- [ ] 檢查 uploads 目錄是否有寫入權限

### 處理失敗
- [ ] 查看終端錯誤信息
- [ ] 檢查音頻文件是否損壞
- [ ] 嘗試使用較短的音頻（30 秒）
- [ ] 檢查歌詞是否太長或太短

## 性能優化檢查

### 生產環境部署
- [ ] 使用 gunicorn 而不是開發服務器
- [ ] 設置 Nginx 反向代理
- [ ] 啟用 HTTPS
- [ ] 配置日誌記錄
- [ ] 設置文件自動清理
- [ ] 配置監控和告警

### 成本優化
- [ ] 監控 API 使用量
- [ ] 設置 API 使用限制
- [ ] 考慮緩存常用結果
- [ ] 定期清理舊文件

## 維護檢查（定期）

### 每週
- [ ] 檢查磁盤空間
- [ ] 清理舊的上傳和輸出文件
- [ ] 檢查錯誤日誌

### 每月
- [ ] 更新 Python 依賴包
- [ ] 檢查 OpenAI API 費用
- [ ] 查看用戶反饋
- [ ] 測試系統功能

### 每季度
- [ ] 審查安全配置
- [ ] 更新文檔
- [ ] 評估新功能需求
- [ ] 性能測試和優化

## 安全檢查

- [ ] `.env` 文件未提交到版本控制
- [ ] API Key 未在代碼中硬編碼
- [ ] 文件上傳有大小限制
- [ ] 文件類型有白名單限制
- [ ] 臨時文件定期清理
- [ ] 生產環境使用強密鑰
- [ ] HTTPS 已啟用（生產環境）

## 文檔檢查

- [ ] README.md 內容完整
- [ ] QUICKSTART.md 步驟清晰
- [ ] API 文檔準確
- [ ] 代碼註釋充分
- [ ] 配置說明清楚

## 完成！

如果以上所有項目都已勾選，恭喜你！系統已經正確設置並可以使用了。

如果遇到任何問題：
1. 查看對應章節的排查步驟
2. 查閱 README.md 的常見問題部分
3. 運行 `python test_setup.py` 診斷問題
4. 檢查終端的詳細錯誤信息
