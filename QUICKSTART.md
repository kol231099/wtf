# 快速開始指南

這份指南將幫助你在 5 分鐘內開始使用 AI 歌詞轉換系統。

## 第一步：安裝依賴

確保你的系統已安裝 Python 3.8 或更高版本：

```bash
python3 --version
```

安裝所需的 Python 包：

```bash
pip install -r requirements.txt
```

## 第二步：配置 OpenAI API

1. 訪問 [OpenAI Platform](https://platform.openai.com/) 並登入
2. 前往 API Keys 頁面創建新的 API Key
3. 複製 `.env.example` 為 `.env`：

```bash
cp .env.example .env
```

4. 編輯 `.env` 文件，填入你的 API Key：

```
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxxxxx
```

## 第三步：測試環境

運行測試腳本：

```bash
python test_setup.py
```

確保所有測試都通過（顯示綠色的 ✓）。

## 第四步：啟動應用

```bash
python app.py
```

你應該會看到類似以下的輸出：

```
正在啟動 AI 歌詞轉換系統...
上傳目錄: uploads
輸出目錄: outputs
OpenAI API 已配置: True

請在瀏覽器中打開: http://localhost:5000
```

## 第五步：使用系統

1. 在瀏覽器中打開 `http://localhost:5000`
2. 準備兩個音頻文件：
   - **原始歌曲**: 包含歌詞和旋律的 WAV 文件
   - **純旋律**: 僅包含伴奏的 WAV 文件

3. 按照網頁上的指示：
   - 上傳原始歌曲
   - 上傳純旋律
   - 輸入新歌詞
   - 點擊「開始合成」

4. 等待處理完成（約 30-60 秒）

5. 播放或下載生成的音頻

## 範例工作流程

假設你有一首歌，想把歌詞改成生日祝福：

### 原始歌詞
```
Happy birthday to you
Happy birthday to you
Happy birthday dear friend
Happy birthday to you
```

### 新歌詞
```
祝你生日快樂
祝你生日快樂
祝親愛的朋友生日快樂
祝你生日快樂
```

系統會：
1. 轉錄原始歌曲
2. 分析節奏和音調
3. 將中文歌詞對齊到原旋律
4. 生成中文演唱
5. 混合人聲和旋律

## 常見問題快速解答

**問：上傳失敗怎麼辦？**
- 確保文件格式是 WAV、MP3、FLAC 或 M4A
- 檢查文件大小是否超過 50MB

**問：處理時間很長？**
- 這是正常的，音頻處理和 AI 分析需要時間
- 1 分鐘的音頻通常需要 30-60 秒處理

**問：生成的聲音不自然？**
- 目前使用的是 TTS API，聲音會比較機械
- 可以嘗試調整歌詞的斷句和長度

**問：API 錯誤？**
- 檢查 OpenAI API Key 是否正確
- 確認賬戶有足夠的額度
- 運行 `python test_setup.py` 測試連接

## 下一步

- 閱讀完整的 [README.md](README.md) 了解更多功能
- 嘗試不同的歌詞和音頻
- 查看 AI 分析建議以優化效果

## 需要幫助？

如果遇到問題：
1. 檢查終端的錯誤信息
2. 運行 `python test_setup.py` 診斷問題
3. 查看 README.md 中的「常見問題」章節
4. 提交 GitHub Issue

祝你使用愉快！
