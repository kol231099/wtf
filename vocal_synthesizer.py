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

            # Step 8: 嚴謹分割句子
            result['steps'].append('正在嚴謹分析句子邊界...')
            print("Step 8: 檢測句子邊界")

            # 使用多重判斷檢測句子邊界
            phrase_boundaries = self.audio_processor.detect_phrase_boundaries(notes, new_lyrics)
            print(f"  檢測到 {len(phrase_boundaries) - 1} 個句子")

            # Step 9: 將歌詞按句子分組
            result['steps'].append('正在將歌詞分組為句子...')
            print("Step 9: 歌詞分句")

            phrases = self.audio_processor.group_lyrics_by_phrases(new_lyrics, phrase_boundaries, notes)
            print(f"  分割為 {len(phrases)} 個句子")

            # 打印句子信息
            for i, phrase in enumerate(phrases):
                print(f"  句子 {i+1}: '{phrase['lyrics']}' ({phrase['char_count']}字, {phrase['note_count']}音符, {phrase['duration']:.2f}s)")

            # Step 10: 逐句生成並精確匹配
            result['steps'].append('正在逐句生成歌聲並匹配原唱法...')
            print("Step 10: 逐句生成歌聲")

            phrase_audios = []
            tts_sr = 22050

            for phrase_idx, phrase in enumerate(phrases):
                phrase_lyrics = phrase['lyrics']
                phrase_notes = phrase['notes']

                print(f"\n  ===== 處理句子 {phrase_idx + 1}/{len(phrases)}: '{phrase_lyrics}' =====")

                # 10.1: 為整個句子生成 TTS（保持連貫性）
                phrase_tts_path = os.path.join(output_dir, f'phrase_{phrase_idx}.wav')

                self.ai_service.generate_speech_with_timing(
                    phrase_lyrics,
                    phrase_tts_path,
                    voice=Config.TTS_VOICE,  # 女聲 shimmer
                    speed=1.0  # 正常速度
                )

                # 10.2: 加載句子音頻
                phrase_audio, phrase_sr = self.audio_processor.load_audio(phrase_tts_path)

                # 10.3: 調整時長以匹配句子的總時長
                phrase_duration = librosa.get_duration(y=phrase_audio, sr=phrase_sr)
                target_duration = phrase['duration']

                if phrase_duration > 0:
                    stretch_factor = phrase_duration / target_duration
                    phrase_audio = self.audio_processor.time_stretch_audio(phrase_audio, stretch_factor)
                    print(f"    時長調整: {phrase_duration:.2f}s → {target_duration:.2f}s (拉伸係數: {stretch_factor:.2f})")

                # 10.4: 提取句子TTS的音高軌跡
                phrase_f0, voiced_flag, voiced_probs = librosa.pyin(
                    phrase_audio,
                    fmin=librosa.note_to_hz('C2'),
                    fmax=librosa.note_to_hz('C7'),
                    sr=phrase_sr
                )

                # 10.5: 提取目標音高軌跡（從音符列表）
                target_f0 = []
                for note in phrase_notes:
                    note_frames = int(note['duration'] * phrase_sr / 512)  # hop_length=512
                    target_f0.extend([note['pitch']] * note_frames)

                target_f0 = np.array(target_f0)

                # 確保長度匹配
                if len(target_f0) > len(phrase_f0):
                    target_f0 = target_f0[:len(phrase_f0)]
                elif len(target_f0) < len(phrase_f0):
                    # 擴展
                    from scipy.interpolate import interp1d
                    old_x = np.linspace(0, 1, len(target_f0))
                    new_x = np.linspace(0, 1, len(phrase_f0))
                    f = interp1d(old_x, target_f0, kind='linear', fill_value='extrapolate')
                    target_f0 = f(new_x)

                # 10.6: 精確調整音高以匹配原唱
                try:
                    phrase_audio = self.audio_processor.apply_dynamic_pitch_contour(
                        phrase_audio,
                        phrase_sr,
                        target_f0
                    )
                    print(f"    ✓ 音高調整完成")
                except Exception as e:
                    print(f"    ⚠ 音高調整失敗: {e}")

                # 10.7: 調整音量包絡以匹配原唱的強度變化
                try:
                    # 構建目標RMS
                    target_rms = []
                    for note in phrase_notes:
                        note_frames = int(note['duration'] * phrase_sr / 512)
                        target_rms.extend([note['loudness']] * note_frames)
                    target_rms = np.array(target_rms)

                    phrase_audio = self.audio_processor.apply_dynamic_envelope(
                        phrase_audio,
                        target_rms
                    )
                    print(f"    ✓ 音量調整完成")
                except Exception as e:
                    print(f"    ⚠ 音量調整失敗: {e}")

                # 10.8: 確保音頻長度精確
                target_samples = int(target_duration * phrase_sr)
                if len(phrase_audio) > target_samples:
                    phrase_audio = phrase_audio[:target_samples]
                elif len(phrase_audio) < target_samples:
                    phrase_audio = np.pad(phrase_audio, (0, target_samples - len(phrase_audio)))

                phrase_audios.append({
                    'audio': phrase_audio,
                    'start_time': phrase['start_time'],
                    'duration': phrase['duration']
                })

                # 清理臨時文件
                if os.path.exists(phrase_tts_path):
                    os.remove(phrase_tts_path)

            # Step 11: 拼接所有句子
            result['steps'].append('正在拼接所有句子形成完整歌聲...')
            print("\nStep 11: 拼接句子")

            # 創建完整的時間軸
            total_duration = melody_features['duration']
            total_samples = int(total_duration * tts_sr)
            final_vocal = np.zeros(total_samples)

            # 將每個句子放到對應的時間位置
            for i, phrase_data in enumerate(phrase_audios):
                start_sample = int(phrase_data['start_time'] * tts_sr)
                phrase_audio = phrase_data['audio']
                end_sample = start_sample + len(phrase_audio)

                # 確保不超出範圍
                if end_sample > total_samples:
                    phrase_audio = phrase_audio[:total_samples - start_sample]
                    end_sample = total_samples

                if start_sample < total_samples and len(phrase_audio) > 0:
                    # 添加淡入淡出（僅在句子邊界）
                    fade_len = min(500, len(phrase_audio) // 10)  # 更長的淡入淡出
                    if fade_len > 0 and i > 0:  # 不淡入第一個句子
                        fade_in = np.linspace(0, 1, fade_len)
                        phrase_audio[:fade_len] *= fade_in

                    if fade_len > 0 and i < len(phrase_audios) - 1:  # 不淡出最後一個句子
                        fade_out = np.linspace(1, 0, fade_len)
                        phrase_audio[-fade_len:] *= fade_out

                    final_vocal[start_sample:end_sample] = phrase_audio

                print(f"  句子 {i+1} 放置在 {phrase_data['start_time']:.2f}s")

            # 歸一化
            max_val = np.max(np.abs(final_vocal))
            if max_val > 0:
                final_vocal = final_vocal / max_val * 0.9

            stretched_vocal = final_vocal

            # 保存逐句處理後的人聲
            stretched_vocal_path = os.path.join(output_dir, 'stretched_vocal.wav')
            self.audio_processor.save_audio(stretched_vocal, stretched_vocal_path, sr=tts_sr)
            result['files']['stretched_vocal'] = stretched_vocal_path

            # Step 12: 混合旋律和人聲
            result['steps'].append('正在混合旋律和人聲...')
            print("\nStep 12: 混合音頻")

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
