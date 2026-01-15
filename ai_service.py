import os
from openai import OpenAI
from dotenv import load_dotenv
import json

load_dotenv()


class AIService:
    """AI 服務類，使用 OpenAI API 進行歌詞分析和語音合成"""

    def __init__(self):
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

    def analyze_lyrics_structure(self, original_lyrics, new_lyrics, timing_info):
        """
        使用 OpenAI API 分析歌詞結構並優化對齊

        Args:
            original_lyrics: 原始歌詞
            new_lyrics: 新歌詞
            timing_info: 時間軸信息

        Returns:
            analysis: 分析結果，包含優化建議
        """
        prompt = f"""
你是一位專業的音樂製作人和歌詞創作者。請分析以下歌詞的結構和節奏。

原始歌詞：
{original_lyrics}

新歌詞：
{new_lyrics}

原始歌曲的時間信息：
- 總時長：{timing_info.get('total_duration', 0):.2f} 秒
- 歌唱段落數量：{len(timing_info.get('vocal_segments', []))}
- 音節變化點數量：{len(timing_info.get('onset_times', []))}

請分析：
1. 新歌詞與原始歌詞的音節數量比較
2. 建議如何調整新歌詞的演唱節奏以匹配原旋律
3. 哪些地方可能需要拉長或加快演唱速度
4. 提供字數分割建議（將歌詞分成與原始歌曲節奏匹配的段落）

請以 JSON 格式回應，包含以下欄位：
{{
    "syllable_comparison": "比較說明",
    "rhythm_adjustments": ["調整建議1", "調整建議2"],
    "segments": [
        {{"text": "歌詞片段", "suggested_duration": 時長（秒）, "notes": "建議"}}
    ],
    "overall_recommendation": "整體建議"
}}
"""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "你是一位專業的音樂製作人，擅長歌詞節奏分析和編曲。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                response_format={"type": "json_object"}
            )

            analysis = json.loads(response.choices[0].message.content)
            return analysis

        except Exception as e:
            print(f"OpenAI API 錯誤: {str(e)}")
            return {
                "error": str(e),
                "syllable_comparison": "無法分析",
                "rhythm_adjustments": [],
                "segments": [],
                "overall_recommendation": "發生錯誤，請檢查 API 設定"
            }

    def generate_pronunciation_guide(self, lyrics, language='zh'):
        """
        生成歌詞的發音指南（用於 TTS）

        Args:
            lyrics: 歌詞文本
            language: 語言代碼

        Returns:
            pronunciation_guide: 發音指南
        """
        prompt = f"""
請為以下歌詞提供詳細的發音指南，包括：
1. 每個字的拼音（中文）或音標（英文）
2. 重音位置
3. 建議的演唱技巧（連音、斷音等）

歌詞：
{lyrics}

請以 JSON 格式回應：
{{
    "words": [
        {{"text": "字詞", "pronunciation": "發音", "stress": "重音位置", "technique": "演唱技巧"}}
    ]
}}
"""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "你是一位聲樂教練，擅長發音指導。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                response_format={"type": "json_object"}
            )

            guide = json.loads(response.choices[0].message.content)
            return guide

        except Exception as e:
            print(f"OpenAI API 錯誤: {str(e)}")
            return {"words": [], "error": str(e)}

    def generate_speech_with_timing(self, text, output_path, voice='alloy', speed=1.0):
        """
        使用 OpenAI TTS API 生成語音

        Args:
            text: 要合成的文本
            output_path: 輸出文件路徑
            voice: 聲音選項 (alloy, echo, fable, onyx, nova, shimmer)
            speed: 語速 (0.25 - 4.0)

        Returns:
            output_path: 生成的音頻文件路徑
        """
        try:
            response = self.client.audio.speech.create(
                model="tts-1-hd",
                voice=voice,
                input=text,
                speed=speed
            )

            response.stream_to_file(output_path)
            return output_path

        except Exception as e:
            print(f"TTS 生成錯誤: {str(e)}")
            raise e

    def optimize_lyrics_timing(self, aligned_lyrics, analysis):
        """
        根據 AI 分析結果優化歌詞時間軸

        Args:
            aligned_lyrics: 初步對齊的歌詞
            analysis: AI 分析結果

        Returns:
            optimized_lyrics: 優化後的歌詞時間軸
        """
        if 'segments' not in analysis or not analysis['segments']:
            return aligned_lyrics

        suggested_segments = analysis['segments']
        optimized_lyrics = []

        # 根據 AI 建議重新分配時間
        current_time = 0
        for segment in suggested_segments:
            text = segment.get('text', '')
            duration = segment.get('suggested_duration', 1.0)

            optimized_lyrics.append({
                'word': text,
                'start': current_time,
                'end': current_time + duration,
                'duration': duration,
                'notes': segment.get('notes', '')
            })

            current_time += duration

        return optimized_lyrics

    def transcribe_audio(self, audio_file_path):
        """
        使用 Whisper API 轉錄音頻中的歌詞

        Args:
            audio_file_path: 音頻文件路徑

        Returns:
            transcription: 轉錄結果，包含文本和時間戳
        """
        try:
            with open(audio_file_path, 'rb') as audio_file:
                response = self.client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    response_format="verbose_json",
                    timestamp_granularities=["word"]
                )

            return {
                'text': response.text,
                'words': response.words if hasattr(response, 'words') else [],
                'language': response.language if hasattr(response, 'language') else 'unknown'
            }

        except Exception as e:
            print(f"Whisper 轉錄錯誤: {str(e)}")
            return {
                'text': '',
                'words': [],
                'error': str(e)
            }
