# 專案摘要

## 專案概述

這是一個基於 AI 的歌詞轉換與旋律對齊系統，能夠將新歌詞按照原始歌曲的旋律和節奏進行合成。

## 核心技術棧

### 後端技術
- **Flask**: Web 框架，提供 API 和頁面路由
- **OpenAI API**:
  - Whisper: 語音轉文字，轉錄原始歌詞
  - GPT-4o-mini: 分析歌詞結構和節奏
  - TTS-1-HD: 文字轉語音，生成演唱

### 音頻處理
- **Librosa**: 核心音頻分析庫
  - 音高檢測 (pitch tracking)
  - 節奏檢測 (beat tracking)
  - MFCC 特徵提取
  - 時間拉伸 (time stretch)
  - 音高轉換 (pitch shift)
- **SoundFile**: 音頻文件 I/O
- **Pydub**: 音頻格式轉換
- **SciPy**: 信號處理

### 前端技術
- **HTML5**: 結構和音頻播放
- **CSS3**: 漸層樣式、動畫效果
- **Vanilla JavaScript**: 文件上傳、AJAX 請求

## 檔案說明

### 核心模組

#### `audio_processor.py`
音頻處理核心類，提供以下功能：
- 載入和保存音頻文件
- 提取旋律特徵（音高、節奏、MFCC）
- 分析人聲時間軸
- 歌詞對齊算法
- 時間拉伸和音高轉換
- 音頻混合

主要類：
- `AudioProcessor`: 音頻處理類

主要方法：
- `extract_melody_features()`: 提取旋律特徵
- `analyze_vocal_timing()`: 分析時間軸
- `align_lyrics_to_melody()`: 歌詞對齊
- `mix_audio()`: 混合音頻

#### `ai_service.py`
OpenAI API 整合服務，提供：
- 歌詞結構分析
- 發音指南生成
- 語音合成
- 音頻轉錄

主要類：
- `AIService`: AI 服務類

主要方法：
- `analyze_lyrics_structure()`: 使用 GPT 分析歌詞
- `generate_speech_with_timing()`: TTS 語音合成
- `transcribe_audio()`: Whisper 轉錄
- `optimize_lyrics_timing()`: 優化時間軸

#### `vocal_synthesizer.py`
歌聲合成器，整合所有模組，提供：
- 完整的合成流程
- 逐步處理和進度追蹤
- 錯誤處理

主要類：
- `VocalSynthesizer`: 合成器類

主要方法：
- `synthesize_vocal()`: 主合成流程
- `adjust_pitch_to_melody()`: 音高調整
- `create_word_by_word_synthesis()`: 逐字合成

#### `app.py`
Flask Web 應用，提供：
- Web 界面路由
- RESTful API 端點
- 文件上傳處理
- 結果下載服務

主要路由：
- `GET /`: 主頁面
- `POST /api/synthesize`: 合成 API
- `GET /api/download/<task_id>/<filename>`: 文件下載
- `GET /api/health`: 健康檢查
- `GET /api/test-openai`: API 測試

### 輔助文件

#### `test_setup.py`
環境測試腳本，檢查：
- Python 版本
- 依賴包安裝狀態
- 環境變數配置
- OpenAI API 連接

#### `install.sh`
自動安裝腳本，執行：
- 虛擬環境創建
- 依賴安裝
- 環境配置
- 測試運行

#### `templates/index.html`
前端界面，功能：
- 文件上傳（支持拖放）
- 表單提交
- 進度顯示
- 音頻播放
- 結果下載

## 工作流程

```
用戶上傳文件和歌詞
        ↓
Flask 接收請求 (app.py)
        ↓
VocalSynthesizer 開始處理
        ↓
1. Whisper 轉錄原始歌詞 (ai_service.py)
        ↓
2. 分析音頻特徵 (audio_processor.py)
   - 提取音高、節奏、節拍
   - 檢測歌唱段落
   - 找出音節變化點
        ↓
3. GPT 分析歌詞結構 (ai_service.py)
   - 比較原歌詞和新歌詞
   - 提供節奏調整建議
   - 生成分段方案
        ↓
4. 對齊新歌詞 (audio_processor.py)
   - 按時間點分配歌詞
   - 根據 AI 建議優化
        ↓
5. TTS 生成語音 (ai_service.py)
   - 計算語速
   - 生成完整語音
        ↓
6. 時間拉伸 (audio_processor.py)
   - 調整語音長度匹配旋律
        ↓
7. 混合音頻 (audio_processor.py)
   - 合併人聲和旋律
   - 調整音量
   - 輸出最終文件
        ↓
返回結果給用戶
```

## 數據流

### 輸入
1. **原始歌曲**: WAV/MP3 文件（歌詞+旋律）
2. **純旋律**: WAV/MP3 文件（僅伴奏）
3. **新歌詞**: 文本字符串

### 中間處理
- **音頻特徵**: NumPy 數組（音高、節奏、MFCC）
- **時間軸信息**: JSON 對象（段落、onset 時間）
- **對齊歌詞**: 列表（每個詞的時間戳）
- **TTS 音頻**: WAV 文件
- **拉伸音頻**: NumPy 數組

### 輸出
1. **最終混合**: WAV 文件（旋律+新歌詞）
2. **純人聲**: WAV 文件（調整後的人聲）
3. **原始 TTS**: WAV 文件（未調整的 TTS）
4. **分析結果**: JSON 對象（AI 建議）

## API 設計

### 請求格式
```http
POST /api/synthesize
Content-Type: multipart/form-data

original_audio: File
melody_audio: File
new_lyrics: String
```

### 回應格式
```json
{
  "success": true,
  "task_id": "uuid-string",
  "steps": ["步驟1", "步驟2", ...],
  "original_lyrics": "轉錄的原始歌詞",
  "aligned_lyrics": [
    {
      "word": "字詞",
      "start": 0.0,
      "end": 0.5,
      "duration": 0.5
    }
  ],
  "lyrics_analysis": {
    "syllable_comparison": "分析說明",
    "rhythm_adjustments": ["建議1", "建議2"],
    "overall_recommendation": "整體建議"
  },
  "melody_features": {
    "tempo": 120.0,
    "duration": 60.0,
    "beat_count": 240
  },
  "files": {
    "final_output": "/api/download/uuid/final_output.wav",
    "stretched_vocal": "/api/download/uuid/stretched_vocal.wav",
    "tts_vocal": "/api/download/uuid/tts_vocal.wav"
  }
}
```

## 配置說明

### 環境變數 (.env)
```env
OPENAI_API_KEY=sk-...           # OpenAI API 金鑰（必須）
FLASK_SECRET_KEY=random-string  # Flask 密鑰（可選）
FLASK_ENV=development           # 環境模式（可選）
```

### 應用配置 (app.py)
```python
UPLOAD_FOLDER = 'uploads'           # 上傳目錄
OUTPUT_FOLDER = 'outputs'           # 輸出目錄
MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50MB 限制
ALLOWED_EXTENSIONS = {'wav', 'mp3', 'flac', 'm4a'}
```

### 音頻配置 (audio_processor.py)
```python
sample_rate = 22050  # 採樣率
```

## 效能考量

### 處理時間
- 1 分鐘音頻：約 30-60 秒
- 主要耗時：Whisper 轉錄、特徵提取、TTS 生成

### 記憶體使用
- 基本需求：約 500MB
- 處理時峰值：約 1-2GB

### API 成本（估算）
- Whisper 轉錄：$0.006/分鐘
- GPT-4o-mini：$0.00015/1K tokens（約 500-1000 tokens）
- TTS-1-HD：$0.03/1K 字符
- 總計：約 $0.05-0.15/次處理

## 限制與已知問題

1. **TTS 品質**: OpenAI TTS 雖然品質不錯，但仍不如真人演唱
2. **節奏複雜度**: 對於變速或複雜節奏的歌曲，對齊效果可能不理想
3. **語言支持**: 主要針對中文和英文優化
4. **處理時間**: 較長的音頻需要更多處理時間
5. **音高匹配**: 目前僅做基本的時長拉伸，未做精確的音高匹配

## 擴展建議

### 短期改進
1. 添加進度條百分比顯示
2. 支持取消正在處理的任務
3. 添加音頻預處理（降噪、正規化）
4. 優化時間對齊算法

### 長期改進
1. 整合專業歌聲合成模型（So-VITS-SVC、RVC）
2. 實現音高自動匹配
3. 支持和聲生成
4. 添加實時預覽功能
5. 批量處理支持
6. 用戶賬號系統
7. 歷史記錄管理

## 測試建議

### 單元測試
- 測試音頻特徵提取正確性
- 測試歌詞對齊算法
- 測試 API 端點

### 整合測試
- 完整流程測試
- 不同格式音頻測試
- 錯誤處理測試

### 用戶測試
- 不同長度的歌曲
- 不同語言的歌詞
- 不同風格的音樂

## 部署建議

### 開發環境
```bash
python app.py
```

### 生產環境
```bash
gunicorn -w 4 -b 0.0.0.0:8000 app:app
```

使用 Nginx 作為反向代理，處理靜態文件和 SSL。

## 維護清單

- [ ] 定期更新依賴包
- [ ] 監控 API 使用和成本
- [ ] 清理舊的上傳和輸出文件
- [ ] 檢查 OpenAI API 更新
- [ ] 收集用戶反饋優化算法

## 貢獻指南

1. Fork 專案
2. 創建功能分支
3. 提交變更
4. 推送到分支
5. 創建 Pull Request

## 授權

本專案僅供學習和研究使用。
