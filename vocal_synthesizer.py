import os
import librosa
import numpy as np
import soundfile as sf
from audio_processor import AudioProcessor
from ai_service import AIService
from config import Config


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

            # Step 7: 提取音符級別特徵
            result['steps'].append('正在分析原旋律的音符細節...')
            print("Step 7: 提取音符級別特徵")

            # 提取原旋律的每個音符信息
            notes = self.audio_processor.extract_note_level_features(melody_path)
            print(f"  檢測到 {len(notes)} 個音符")

            # Step 8: 歌詞與音符對齊
            result['steps'].append('正在將歌詞對齊到音符...')
            print("Step 8: 歌詞與音符對齊")

            aligned = self.audio_processor.align_lyrics_to_notes(new_lyrics, notes)
            print(f"  對齊了 {len(aligned)} 個字")

            # 打印對齊信息（用於調試）
            for i, item in enumerate(aligned[:5]):  # 只打印前5個
                print(f"  [{i}] '{item['char']}' -> {item['note']['pitch']:.1f}Hz, {item['note']['duration']:.2f}s")

            # Step 9: 逐字生成並調整 vocal
            result['steps'].append('正在逐字生成歌聲並匹配原唱法...')
            print("Step 9: 逐字生成歌聲")

            vocal_segments = []
            tts_sr = 22050

            for i, item in enumerate(aligned):
                char = item['char']
                note = item['note']

                print(f"  處理 [{i+1}/{len(aligned)}]: '{char}' (目標: {note['pitch']:.1f}Hz, {note['duration']:.2f}s)")

                # 9.1: 為單個字生成 TTS
                char_tts_path = os.path.join(output_dir, f'char_{i}_{char}.wav')

                # 使用正常速度生成（後續會拉伸）
                self.ai_service.generate_speech_with_timing(
                    char,
                    char_tts_path,
                    voice=Config.TTS_VOICE,  # 使用配置的聲音（shimmer=女聲柔和）
                    speed=1.0  # 正常速度
                )

                # 9.2: 加載生成的音頻
                char_audio, char_sr = self.audio_processor.load_audio(char_tts_path)

                # 9.3: 調整時長以匹配音符時長
                char_duration = librosa.get_duration(y=char_audio, sr=char_sr)
                target_duration = note['duration']

                if char_duration > 0:
                    stretch_factor = char_duration / target_duration
                    char_audio = self.audio_processor.time_stretch_audio(char_audio, stretch_factor)

                # 9.4: 調整音高以匹配音符音高
                # 提取原始TTS的音高
                char_f0 = librosa.yin(char_audio, fmin=80, fmax=400, sr=char_sr)
                char_f0_median = np.median(char_f0[~np.isnan(char_f0)]) if np.any(~np.isnan(char_f0)) else 200

                # 計算需要調整的半音數
                if char_f0_median > 0 and note['pitch'] > 0:
                    pitch_ratio = note['pitch'] / char_f0_median
                    n_steps = 12 * np.log2(pitch_ratio)
                    n_steps = np.clip(n_steps, -12, 12)  # 限制範圍

                    # 應用音高調整
                    char_audio = self.audio_processor.pitch_shift_audio(
                        char_audio, char_sr, n_steps
                    )

                # 9.5: 如果音符有音高變化（滑音），模擬它
                if note.get('pitch_variation', 0) > 2:  # 顯著的音高變化
                    # 添加適度顫音
                    try:
                        char_audio = self.audio_processor.apply_vibrato(
                            char_audio, char_sr,
                            rate=5.5,
                            depth=min(0.5, note['pitch_variation'] / 10)
                        )
                    except:
                        pass  # 如果失敗就跳過

                # 9.6: 調整音量以匹配音符強度
                target_rms = note['loudness']
                char_rms = np.sqrt(np.mean(char_audio**2))
                if char_rms > 0:
                    char_audio = char_audio * (target_rms / char_rms)

                # 9.7: 確保音頻長度正確
                target_samples = int(target_duration * char_sr)
                if len(char_audio) > target_samples:
                    char_audio = char_audio[:target_samples]
                elif len(char_audio) < target_samples:
                    char_audio = np.pad(char_audio, (0, target_samples - len(char_audio)))

                vocal_segments.append(char_audio)

                # 清理臨時文件
                if os.path.exists(char_tts_path):
                    os.remove(char_tts_path)

            # Step 10: 拼接所有字
            result['steps'].append('正在拼接所有字形成完整歌聲...')
            print("Step 10: 拼接vocal片段")

            # 創建完整的時間軸
            total_duration = melody_features['duration']
            total_samples = int(total_duration * tts_sr)
            final_vocal = np.zeros(total_samples)

            # 將每個字放到對應的時間位置
            for i, (item, segment) in enumerate(zip(aligned, vocal_segments)):
                note = item['note']
                start_sample = int(note['start'] * tts_sr)
                end_sample = start_sample + len(segment)

                # 確保不超出範圍
                if end_sample > total_samples:
                    segment = segment[:total_samples - start_sample]
                    end_sample = total_samples

                if start_sample < total_samples:
                    # 添加淡入淡出以避免咔噠聲
                    fade_len = min(100, len(segment) // 4)
                    if fade_len > 0:
                        fade_in = np.linspace(0, 1, fade_len)
                        fade_out = np.linspace(1, 0, fade_len)
                        segment[:fade_len] *= fade_in
                        segment[-fade_len:] *= fade_out

                    final_vocal[start_sample:end_sample] += segment

            # 歸一化
            max_val = np.max(np.abs(final_vocal))
            if max_val > 0:
                final_vocal = final_vocal / max_val * 0.9

            stretched_vocal = final_vocal

            # 保存逐字處理後的人聲
            stretched_vocal_path = os.path.join(output_dir, 'stretched_vocal.wav')
            self.audio_processor.save_audio(stretched_vocal, stretched_vocal_path, sr=tts_sr)
            result['files']['stretched_vocal'] = stretched_vocal_path

            # Step 11: 混合旋律和人聲
            result['steps'].append('正在混合旋律和人聲...')
            print("Step 11: 混合音頻")

            # 從 melody_features 中獲取旋律音頻
            melody_audio = melody_features['audio']

            final_output = os.path.join(output_dir, 'final_output.wav')
            self.audio_processor.mix_audio(
                melody_audio,
                stretched_vocal,
                final_output,
                melody_volume=Config.DEFAULT_MELODY_VOLUME,
                vocal_volume=Config.DEFAULT_VOCAL_VOLUME
            )

            result['files']['final_output'] = final_output
            # 逐字生成的方式不再有單一的 tts_vocal 文件
            # result['files']['tts_vocal'] = stretched_vocal_path
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
