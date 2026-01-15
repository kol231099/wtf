import os
import librosa
import numpy as np
import soundfile as sf
from audio_processor import AudioProcessor
from ai_service import AIService


class VocalSynthesizer:
    """歌聲合成器，整合音頻處理和 AI 服務"""

    def __init__(self):
        self.audio_processor = AudioProcessor()
        self.ai_service = AIService()

    def synthesize_vocal(self, original_audio_path, melody_path, new_lyrics, output_dir='outputs'):
        """
        主要合成流程

        Args:
            original_audio_path: 原始歌曲路徑（包含歌詞+旋律）
            melody_path: 純旋律路徑
            new_lyrics: 新歌詞文本
            output_dir: 輸出目錄

        Returns:
            result: 包含結果信息的字典
        """
        os.makedirs(output_dir, exist_ok=True)

        result = {
            'success': False,
            'steps': [],
            'files': {}
        }

        try:
            # Step 1: 轉錄原始歌曲（可選，獲取原始歌詞）
            result['steps'].append('正在轉錄原始歌曲...')
            print("Step 1: 轉錄原始歌曲")
            transcription = self.ai_service.transcribe_audio(original_audio_path)
            original_lyrics = transcription.get('text', '')
            result['original_lyrics'] = original_lyrics

            # Step 2: 分析原始歌曲的時間軸
            result['steps'].append('正在分析原始歌曲的節奏和時間軸...')
            print("Step 2: 分析時間軸")
            timing_info = self.audio_processor.analyze_vocal_timing(original_audio_path)
            result['timing_info'] = timing_info

            # Step 3: 提取旋律特徵
            result['steps'].append('正在提取旋律特徵...')
            print("Step 3: 提取旋律特徵")
            melody_features = self.audio_processor.extract_melody_features(melody_path)
            result['melody_features'] = {
                'tempo': float(melody_features['tempo']),
                'duration': float(melody_features['duration']),
                'beat_count': len(melody_features['beats'])
            }

            # Step 4: 使用 AI 分析歌詞結構
            result['steps'].append('正在使用 AI 分析歌詞結構...')
            print("Step 4: AI 分析歌詞")
            lyrics_analysis = self.ai_service.analyze_lyrics_structure(
                original_lyrics, new_lyrics, timing_info
            )
            result['lyrics_analysis'] = lyrics_analysis

            # Step 5: 對齊新歌詞到旋律
            result['steps'].append('正在對齊新歌詞到旋律...')
            print("Step 5: 對齊歌詞")
            aligned_lyrics = self.audio_processor.align_lyrics_to_melody(
                new_lyrics, melody_features, timing_info
            )

            # Step 6: 根據 AI 建議優化對齊
            result['steps'].append('正在優化歌詞時間軸...')
            print("Step 6: 優化對齊")
            optimized_lyrics = self.ai_service.optimize_lyrics_timing(
                aligned_lyrics, lyrics_analysis
            )
            result['aligned_lyrics'] = optimized_lyrics

            # Step 7: 生成語音片段並合成
            result['steps'].append('正在生成歌聲...')
            print("Step 7: 生成歌聲")
            vocal_segments = []

            # 使用 OpenAI TTS 生成整段語音
            # 計算建議的語速
            original_duration = timing_info['total_duration']
            estimated_speaking_duration = len(new_lyrics) * 0.3  # 粗略估計
            speed = min(4.0, max(0.25, estimated_speaking_duration / original_duration))

            tts_output = os.path.join(output_dir, 'tts_vocal.wav')
            self.ai_service.generate_speech_with_timing(
                new_lyrics,
                tts_output,
                voice='nova',  # 可調整不同的聲音
                speed=speed
            )

            # Step 8: 時間拉伸以匹配旋律長度
            result['steps'].append('正在調整歌聲時長以匹配旋律...')
            print("Step 8: 時間拉伸")
            tts_audio, tts_sr = self.audio_processor.load_audio(tts_output)
            melody_audio = melody_features['audio']

            # 計算拉伸因子
            tts_duration = librosa.get_duration(y=tts_audio, sr=tts_sr)
            melody_duration = melody_features['duration']
            stretch_factor = tts_duration / melody_duration

            # 拉伸 TTS 音頻以匹配旋律長度
            stretched_vocal = self.audio_processor.time_stretch_audio(tts_audio, stretch_factor)

            # 保存拉伸後的人聲
            stretched_vocal_path = os.path.join(output_dir, 'stretched_vocal.wav')
            self.audio_processor.save_audio(stretched_vocal, stretched_vocal_path)
            result['files']['stretched_vocal'] = stretched_vocal_path

            # Step 9: 混合旋律和人聲
            result['steps'].append('正在混合旋律和人聲...')
            print("Step 9: 混合音頻")
            final_output = os.path.join(output_dir, 'final_output.wav')
            self.audio_processor.mix_audio(
                melody_audio,
                stretched_vocal,
                final_output,
                melody_volume=0.5,
                vocal_volume=0.8
            )

            result['files']['final_output'] = final_output
            result['files']['tts_vocal'] = tts_output
            result['success'] = True
            result['steps'].append('合成完成!')

            return result

        except Exception as e:
            result['error'] = str(e)
            result['steps'].append(f'錯誤: {str(e)}')
            print(f"合成錯誤: {str(e)}")
            import traceback
            traceback.print_exc()
            return result

    def adjust_pitch_to_melody(self, vocal_audio, melody_features):
        """
        調整人聲音高以匹配旋律（進階功能）

        Args:
            vocal_audio: 人聲音頻
            melody_features: 旋律特徵

        Returns:
            adjusted_vocal: 調整後的人聲
        """
        # 提取人聲和旋律的音高
        vocal_pitches, _ = librosa.piptrack(y=vocal_audio, sr=self.audio_processor.sample_rate)
        melody_pitches = melody_features['pitches']

        # 計算平均音高差異
        vocal_pitch_mean = np.mean(vocal_pitches[vocal_pitches > 0])
        melody_pitch_mean = np.mean(melody_pitches[melody_pitches > 0])

        # 計算需要調整的半音數
        if vocal_pitch_mean > 0 and melody_pitch_mean > 0:
            pitch_ratio = melody_pitch_mean / vocal_pitch_mean
            n_steps = 12 * np.log2(pitch_ratio)

            # 調整音高
            adjusted_vocal = self.audio_processor.pitch_shift_audio(
                vocal_audio,
                self.audio_processor.sample_rate,
                n_steps
            )

            return adjusted_vocal
        else:
            return vocal_audio

    def create_word_by_word_synthesis(self, aligned_lyrics, melody_path, output_dir='outputs'):
        """
        逐字生成並拼接（更精確但較慢）

        Args:
            aligned_lyrics: 對齊後的歌詞
            melody_path: 旋律路徑
            output_dir: 輸出目錄

        Returns:
            final_audio_path: 最終音頻路徑
        """
        segments = []

        for i, lyric_item in enumerate(aligned_lyrics):
            word = lyric_item['word']
            duration = lyric_item['duration']

            # 為每個詞生成 TTS
            temp_path = os.path.join(output_dir, f'temp_word_{i}.wav')

            # 根據持續時間調整語速
            speed = max(0.25, min(4.0, 1.0 / duration))

            self.ai_service.generate_speech_with_timing(
                word,
                temp_path,
                voice='nova',
                speed=speed
            )

            # 載入並調整時長
            word_audio, sr = self.audio_processor.load_audio(temp_path)
            word_duration = librosa.get_duration(y=word_audio, sr=sr)

            if word_duration > 0:
                stretch_factor = word_duration / duration
                stretched = self.audio_processor.time_stretch_audio(word_audio, stretch_factor)
                segments.append(stretched)

            # 清理臨時文件
            if os.path.exists(temp_path):
                os.remove(temp_path)

        # 拼接所有片段
        if segments:
            final_vocal = np.concatenate(segments)
            output_path = os.path.join(output_dir, 'word_by_word_vocal.wav')
            self.audio_processor.save_audio(final_vocal, output_path)
            return output_path
        else:
            return None
