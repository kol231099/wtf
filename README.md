# AI 歌詞轉換與旋律對齊系統

這個系統可以將新歌詞按照原始歌曲的旋律和節奏進行合成，使用 AI 技術自動對齊歌詞時間軸並生成演唱版本。

## 功能特點

- **智能歌詞分析**: 使用 OpenAI GPT 分析原始歌詞和新歌詞的結構差異
- **自動時間對齊**: 基於音頻分析自動將新歌詞對齊到原旋律
- **語音合成**: 使用 OpenAI TTS API 生成自然的演唱聲音
- **音頻處理**: 自動調整時長、音高以匹配原旋律
- **Web 界面**: 簡潔美觀的網頁界面，支持拖放上傳
- **實時進度**: 顯示處理進度和 AI 分析結果

## 系統需求

- Python 3.8 或更高版本
- OpenAI API Key（需要訪問 GPT-4o-mini 和 Whisper、TTS API）
- 至少 2GB 可用記憶體
- 支持的音頻格式：WAV, MP3, FLAC, M4A

## 安裝步驟

### 1. 克隆或下載專案

```bash
cd /path/to/wtf
```

### 2. 創建虛擬環境（推薦）

```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows
```

### 3. 安裝依賴

```bash
pip install -r requirements.txt
```

**注意**: 某些系統可能需要額外安裝音頻處理庫：

- **Mac**: `brew install ffmpeg`
- **Ubuntu/Debian**: `sudo apt-get install ffmpeg libsndfile1`
- **Windows**: 下載 [ffmpeg](https://ffmpeg.org/download.html) 並添加到 PATH

### 4. 配置環境變數

```bash
cp .env.example .env
```

編輯 `.env` 文件，填入你的 OpenAI API Key：

```
OPENAI_API_KEY=sk-your-actual-api-key-here
FLASK_SECRET_KEY=your-random-secret-key
FLASK_ENV=development
```

### 5. 測試環境

運行測試腳本確保一切就緒：

```bash
python test_setup.py
```

如果所有測試通過，你可以開始使用系統了！

### 6. 啟動應用

```bash
python app.py
```

應用會在 `http://localhost:5000` 啟動。

## 使用方法

### 基本流程

1. **準備音頻文件**:
   - 原始歌曲（包含歌詞和旋律）- 建議使用 WAV 格式
   - 純旋律檔案（僅伴奏，無人聲）- 建議使用 WAV 格式

2. **打開 Web 界面**: 在瀏覽器中訪問 `http://localhost:5000`

3. **上傳文件**:
   - 點擊或拖放上傳原始歌曲
   - 點擊或拖放上傳純旋律檔案

4. **輸入新歌詞**: 在文本框中輸入你想替換的新歌詞

5. **開始合成**: 點擊「開始合成」按鈕

6. **等待處理**: 系統會顯示處理進度，包括：
   - 轉錄原始歌曲
   - 分析節奏和時間軸
   - 提取旋律特徵
   - AI 分析歌詞結構
   - 對齊新歌詞
   - 生成歌聲
   - 混合音頻

7. **下載結果**: 處理完成後可以：
   - 在線播放生成的音頻
   - 下載最終混合版本
   - 下載純人聲版本
   - 查看 AI 分析建議

### 提示與技巧

- **歌詞長度**: 新歌詞長度應該與原歌詞相近，否則可能需要調整演唱速度
- **音頻質量**: 使用高質量的 WAV 格式可以獲得更好的效果
- **純旋律**: 確保旋律檔案盡可能不包含人聲，這樣混合效果會更好
- **處理時間**: 約 1 分鐘的音頻可能需要 30-60 秒處理時間

## API 端點

如果你想通過 API 調用系統，可以使用以下端點：

### POST `/api/synthesize`

合成新歌曲

**請求參數**（multipart/form-data）:
- `original_audio`: 原始歌曲文件
- `melody_audio`: 純旋律文件
- `new_lyrics`: 新歌詞文本

**回應**:
```json
{
  "success": true,
  "task_id": "uuid",
  "steps": ["步驟1", "步驟2", ...],
  "original_lyrics": "轉錄的原始歌詞",
  "aligned_lyrics": [...],
  "lyrics_analysis": {...},
  "files": {
    "final_output": "/api/download/uuid/final_output.wav",
    "stretched_vocal": "/api/download/uuid/stretched_vocal.wav",
    "tts_vocal": "/api/download/uuid/tts_vocal.wav"
  }
}
```

### GET `/api/download/<task_id>/<filename>`

下載生成的文件

### GET `/api/health`

檢查系統健康狀態

### GET `/api/test-openai`

測試 OpenAI API 連接

## 技術架構

### 後端
- **Flask**: Web 框架
- **OpenAI API**:
  - GPT-4o-mini: 歌詞結構分析
  - Whisper: 語音轉文字
  - TTS-1-HD: 文字轉語音

### 音頻處理
- **Librosa**: 音頻特徵提取、節奏分析
- **SoundFile**: 音頻文件讀寫
- **Pydub**: 音頻格式轉換
- **SciPy**: 信號處理

### 前端
- **HTML5**: 結構
- **CSS3**: 樣式（漸層、動畫）
- **JavaScript**: 互動邏輯、文件上傳

## 目錄結構

```
wtf/
├── app.py                  # Flask 主應用
├── audio_processor.py      # 音頻處理模組
├── ai_service.py          # OpenAI API 服務
├── vocal_synthesizer.py   # 歌聲合成器
├── test_setup.py          # 環境測試腳本
├── requirements.txt       # Python 依賴
├── .env.example          # 環境變數範例
├── .env                  # 環境變數（不提交到 Git）
├── README.md             # 說明文件
├── templates/
│   └── index.html        # Web 界面
├── uploads/              # 上傳文件目錄
└── outputs/              # 輸出文件目錄
```

## 工作原理

1. **音頻分析階段**:
   - 使用 Whisper API 轉錄原始歌曲獲取原歌詞
   - 提取音頻的節奏、音高、節拍等特徵
   - 檢測歌唱段落和音節變化點

2. **AI 分析階段**:
   - GPT 比較原歌詞和新歌詞的音節數量
   - 提供節奏調整建議
   - 生成歌詞分段方案

3. **時間對齊階段**:
   - 將新歌詞按照原歌曲的時間點對齊
   - 根據 AI 建議優化時間分配

4. **語音合成階段**:
   - 使用 TTS API 生成新歌詞的語音
   - 自動調整語速以匹配原時長
   - 時間拉伸以精確匹配旋律長度

5. **混音階段**:
   - 將生成的人聲與純旋律混合
   - 調整音量平衡
   - 輸出最終音頻文件

## 已知限制

- TTS 生成的聲音較為機械，不如真人演唱自然
- 對於節奏複雜或速度變化大的歌曲，對齊效果可能不理想
- 新歌詞與原歌詞長度差異過大時，可能需要手動調整
- 處理時間較長（約 1 分鐘音頻需要 30-60 秒）

## 未來改進方向

- [ ] 整合更專業的 AI 歌聲合成模型（如 So-VITS-SVC、RVC）
- [ ] 支持更精細的音高調整和音色匹配
- [ ] 添加批量處理功能
- [ ] 支持更多音頻格式
- [ ] 優化處理速度
- [ ] 添加預覽功能（處理前試聽）
- [ ] 支持自定義 TTS 聲音訓練

## 常見問題

**Q: 為什麼生成的聲音聽起來很機械？**
A: 目前使用的是 OpenAI TTS API，雖然品質不錯但仍然是合成聲音。如果需要更自然的效果，可以考慮整合專業的歌聲合成模型。

**Q: 可以處理多長的音頻？**
A: 建議處理 1-3 分鐘的音頻片段。更長的音頻會增加處理時間和 API 成本。

**Q: OpenAI API 費用如何計算？**
A: 主要費用來自 Whisper 轉錄、GPT 分析和 TTS 合成。約 1 分鐘音頻的處理成本大約 $0.05-0.15 USD。

**Q: 支持中文歌詞嗎？**
A: 是的，系統同時支持中文和英文歌詞。

## 授權

本專案僅供學習和研究使用。

## 貢獻

歡迎提交 Issue 和 Pull Request！

## 聯繫方式

如有問題或建議，請創建 GitHub Issue。
