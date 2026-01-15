import librosa
import numpy as np
import soundfile as sf
from scipy import signal
from pydub import AudioSegment
import os
from config import Config


class AudioProcessor:
    """音頻處理類，負責分析和處理音頻文件"""

    def __init__(self):
        self.sample_rate = 22050

    def load_audio(self, file_path):
        """
        載入音頻文件

        Args:
            file_path: 音頻文件路徑

        Returns:
            y: 音頻時間序列
            sr: 採樣率
        """
        y, sr = librosa.load(file_path, sr=self.sample_rate)
        return y, sr

    def extract_melody_features(self, audio_path):
        """
        從音頻中提取旋律特徵

        Args:
            audio_path: 音頻文件路徑

        Returns:
            features: 包含音高、節奏等特徵的字典
        """
        y, sr = self.load_audio(audio_path)

        # 提取音高 (pitch)
        pitches, magnitudes = librosa.piptrack(y=y, sr=sr)

        # 提取節奏和節拍
        tempo, beats = librosa.beat.beat_track(y=y, sr=sr)

        # 提取 MFCC 特徵（音色特徵）
        mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)

        # 提取音量包絡
        rms = librosa.feature.rms(y=y)[0]

        # 提取過零率（聲音變化率）
        zcr = librosa.feature.zero_crossing_rate(y)[0]

        features = {
            'pitches': pitches,
            'magnitudes': magnitudes,
            'tempo': tempo,
            'beats': beats,
            'beat_times': librosa.frames_to_time(beats, sr=sr),
            'mfcc': mfcc,
            'rms': rms,
            'zcr': zcr,
            'duration': librosa.get_duration(y=y, sr=sr),
            'sr': sr,
            'audio': y
        }

        return features

    def analyze_vocal_timing(self, vocal_audio_path):
        """
        分析人聲的時間軸信息

        Args:
            vocal_audio_path: 包含人聲的音頻路徑

        Returns:
            timing_info: 時間軸信息字典
        """
        y, sr = self.load_audio(vocal_audio_path)

        # 使用音量檢測找出歌唱段落
        rms = librosa.feature.rms(y=y, frame_length=2048, hop_length=512)[0]

        # 找出有聲音的時間段（歌唱部分）
        threshold = np.mean(rms) * 0.3
        vocal_frames = rms > threshold

        # 將幀轉換為時間
        times = librosa.frames_to_time(np.arange(len(vocal_frames)), sr=sr, hop_length=512)

        # 找出歌唱段落的起始和結束點
        vocal_segments = []
        in_segment = False
        start_time = 0

        for i, is_vocal in enumerate(vocal_frames):
            if is_vocal and not in_segment:
                start_time = times[i]
                in_segment = True
            elif not is_vocal and in_segment:
                vocal_segments.append({
                    'start': start_time,
                    'end': times[i],
                    'duration': times[i] - start_time
                })
                in_segment = False

        # 提取音節信息（onset detection）
        onset_frames = librosa.onset.onset_detect(y=y, sr=sr, units='frames')
        onset_times = librosa.frames_to_time(onset_frames, sr=sr)

        timing_info = {
            'vocal_segments': vocal_segments,
            'onset_times': onset_times.tolist(),
            'total_duration': librosa.get_duration(y=y, sr=sr),
            'rms': rms.tolist(),
            'threshold': threshold
        }

        return timing_info

    def align_lyrics_to_melody(self, lyrics, melody_features, timing_info):
        """
        將歌詞對齊到旋律的時間點

        Args:
            lyrics: 新歌詞文本
            melody_features: 旋律特徵
            timing_info: 原始歌曲的時間軸信息

        Returns:
            aligned_lyrics: 對齊後的歌詞，包含時間戳
        """
        # 分割歌詞為字或詞
        lyrics_cleaned = lyrics.strip()
        # 處理中文和英文
        import re
        # 按標點符號和空格分割
        words = re.findall(r'[\u4e00-\u9fff]+|[a-zA-Z]+|[0-9]+', lyrics_cleaned)

        if not words:
            return []

        # 使用 onset times 作為對齊點
        onset_times = timing_info['onset_times']

        # 如果 onset 點比詞少，平均分配時間
        total_duration = timing_info['total_duration']

        aligned_lyrics = []

        if len(onset_times) >= len(words):
            # 有足夠的 onset 點，每個詞對應一個 onset
            for i, word in enumerate(words):
                start_time = onset_times[i] if i < len(onset_times) else onset_times[-1]
                end_time = onset_times[i + 1] if i + 1 < len(onset_times) else total_duration

                aligned_lyrics.append({
                    'word': word,
                    'start': start_time,
                    'end': end_time,
                    'duration': end_time - start_time
                })
        else:
            # onset 點較少，按時間平均分配
            time_per_word = total_duration / len(words)
            for i, word in enumerate(words):
                start_time = i * time_per_word
                end_time = (i + 1) * time_per_word

                aligned_lyrics.append({
                    'word': word,
                    'start': start_time,
                    'end': end_time,
                    'duration': end_time - start_time
                })

        return aligned_lyrics

    def time_stretch_audio(self, audio, stretch_factor):
        """
        時間拉伸音頻（不改變音高）

        Args:
            audio: 音頻數據
            stretch_factor: 拉伸因子（>1 變慢，<1 變快）

        Returns:
            stretched_audio: 拉伸後的音頻
        """
        return librosa.effects.time_stretch(audio, rate=stretch_factor)

    def pitch_shift_audio(self, audio, sr, n_steps):
        """
        改變音高（不改變速度）

        Args:
            audio: 音頻數據
            sr: 採樣率
            n_steps: 半音步數（正數升高，負數降低）

        Returns:
            shifted_audio: 改變音高後的音頻
        """
        return librosa.effects.pitch_shift(audio, sr=sr, n_steps=n_steps)

    def apply_vibrato(self, audio, sr, rate=5.5, depth=0.5):
        """
        為音頻添加顫音效果，讓聲音更像歌唱

        Args:
            audio: 音頻數據
            sr: 採樣率
            rate: 顫音頻率 (Hz)，通常在 4-7 Hz 之間
            depth: 顫音深度（半音），通常在 0.3-1.0 之間

        Returns:
            vibrato_audio: 添加顫音後的音頻
        """
        # 創建顫音調制信號（正弦波）
        t = np.arange(len(audio)) / sr
        vibrato_lfo = depth * np.sin(2 * np.pi * rate * t)

        # 使用相位累積實現音高調制
        # 將顫音轉換為瞬時頻率調制
        phase_acc = np.cumsum(2 ** (vibrato_lfo / 12))

        # 使用線性插值重新採樣音頻
        from scipy.interpolate import interp1d
        original_indices = np.arange(len(audio))
        new_indices = phase_acc * len(audio) / phase_acc[-1]

        # 確保索引在有效範圍內
        new_indices = np.clip(new_indices, 0, len(audio) - 1)

        # 插值生成顫音
        interp_func = interp1d(original_indices, audio, kind='linear',
                              bounds_error=False, fill_value=0)
        vibrato_audio = interp_func(new_indices)

        return vibrato_audio

    def apply_dynamic_pitch_contour(self, vocal_audio, sr, melody_pitches, hop_length=512):
        """
        根據旋律的音高輪廓動態調整人聲音高

        Args:
            vocal_audio: 人聲音頻
            sr: 採樣率
            melody_pitches: 旋律音高序列（Hz）
            hop_length: 幀跳躍長度

        Returns:
            adjusted_audio: 調整後的音頻
        """
        # 使用短時傅里葉變換 (STFT) 進行音高調制
        D = librosa.stft(vocal_audio, hop_length=hop_length)
        magnitude = np.abs(D)
        phase = np.angle(D)

        # 提取人聲的音高軌跡
        vocal_f0 = librosa.yin(vocal_audio, fmin=80, fmax=400, sr=sr, hop_length=hop_length)

        # 確保旋律音高和人聲幀數匹配
        if len(melody_pitches) != len(vocal_f0):
            # 重新採樣旋律音高以匹配人聲幀數
            from scipy.interpolate import interp1d
            original_indices = np.linspace(0, 1, len(melody_pitches))
            new_indices = np.linspace(0, 1, len(vocal_f0))
            interp_func = interp1d(original_indices, melody_pitches,
                                  kind='linear', fill_value='extrapolate')
            melody_pitches_resampled = interp_func(new_indices)
        else:
            melody_pitches_resampled = melody_pitches

        # 計算每幀的音高調整比例
        pitch_shifts = []
        for i in range(len(vocal_f0)):
            if vocal_f0[i] > 0 and melody_pitches_resampled[i] > 0:
                # 計算需要調整的半音數
                ratio = melody_pitches_resampled[i] / vocal_f0[i]
                n_steps = 12 * np.log2(ratio)
                # 限制調整範圍，避免過度調整
                n_steps = np.clip(n_steps, -12, 12)
                pitch_shifts.append(n_steps)
            else:
                pitch_shifts.append(0)

        pitch_shifts = np.array(pitch_shifts)

        # 平滑音高軌跡，避免突兀的跳躍
        from scipy.ndimage import gaussian_filter1d
        pitch_shifts_smooth = gaussian_filter1d(pitch_shifts, sigma=2)

        # 應用分段音高調整
        # 由於librosa不支持時變音高調整，我們使用pyrubberband或分段處理
        # 這裡使用簡化方法：分成多個片段，每個片段單獨調整
        n_segments = min(Config.PITCH_CONTOUR_SEGMENTS, len(pitch_shifts_smooth))
        segment_length = len(vocal_audio) // n_segments
        adjusted_segments = []

        for i in range(n_segments):
            start_sample = i * segment_length
            end_sample = (i + 1) * segment_length if i < n_segments - 1 else len(vocal_audio)
            segment = vocal_audio[start_sample:end_sample]

            # 計算該片段的平均音高調整
            start_frame = i * len(pitch_shifts_smooth) // n_segments
            end_frame = (i + 1) * len(pitch_shifts_smooth) // n_segments
            avg_shift = np.mean(pitch_shifts_smooth[start_frame:end_frame])

            # 調整該片段的音高
            if abs(avg_shift) > 0.1:  # 只有顯著變化才調整
                adjusted_segment = librosa.effects.pitch_shift(segment, sr=sr, n_steps=avg_shift)
            else:
                adjusted_segment = segment

            adjusted_segments.append(adjusted_segment)

        # 組合所有片段
        adjusted_audio = np.concatenate(adjusted_segments)

        # 確保長度一致
        if len(adjusted_audio) > len(vocal_audio):
            adjusted_audio = adjusted_audio[:len(vocal_audio)]
        elif len(adjusted_audio) < len(vocal_audio):
            adjusted_audio = np.pad(adjusted_audio, (0, len(vocal_audio) - len(adjusted_audio)))

        return adjusted_audio

    def apply_dynamic_envelope(self, vocal_audio, melody_rms, smoothing=5):
        """
        根據旋律的音量變化調整人聲的動態包絡

        Args:
            vocal_audio: 人聲音頻
            melody_rms: 旋律的 RMS 能量
            smoothing: 平滑窗口大小

        Returns:
            shaped_audio: 應用動態包絡後的音頻
        """
        # 計算人聲的 RMS
        vocal_rms = librosa.feature.rms(y=vocal_audio, frame_length=2048, hop_length=512)[0]

        # 將旋律 RMS 重採樣以匹配人聲 RMS 的長度
        if len(melody_rms) != len(vocal_rms):
            from scipy.interpolate import interp1d
            original_indices = np.linspace(0, 1, len(melody_rms))
            new_indices = np.linspace(0, 1, len(vocal_rms))
            interp_func = interp1d(original_indices, melody_rms,
                                  kind='cubic', fill_value='extrapolate')
            melody_rms_resampled = interp_func(new_indices)
        else:
            melody_rms_resampled = melody_rms

        # 歸一化
        melody_rms_norm = melody_rms_resampled / (np.max(melody_rms_resampled) + 1e-8)
        vocal_rms_norm = vocal_rms / (np.max(vocal_rms) + 1e-8)

        # 計算增益調整
        # 使用旋律的動態作為目標，但保留一些人聲的自然動態
        target_rms = (Config.ENVELOPE_MELODY_WEIGHT * melody_rms_norm +
                     Config.ENVELOPE_VOCAL_WEIGHT * vocal_rms_norm)
        gain_envelope = target_rms / (vocal_rms_norm + 1e-8)

        # 限制增益範圍，避免過度放大或縮小
        gain_envelope = np.clip(gain_envelope, 0.3, 3.0)

        # 平滑增益曲線
        from scipy.ndimage import uniform_filter1d
        gain_envelope_smooth = uniform_filter1d(gain_envelope, size=smoothing)

        # 將幀級增益擴展到樣本級
        hop_length = 512
        gain_per_sample = np.repeat(gain_envelope_smooth, hop_length)

        # 調整長度以匹配音頻
        if len(gain_per_sample) > len(vocal_audio):
            gain_per_sample = gain_per_sample[:len(vocal_audio)]
        elif len(gain_per_sample) < len(vocal_audio):
            gain_per_sample = np.pad(gain_per_sample,
                                    (0, len(vocal_audio) - len(gain_per_sample)),
                                    mode='edge')

        # 應用增益包絡
        shaped_audio = vocal_audio * gain_per_sample

        return shaped_audio

    def extract_note_level_features(self, audio_path):
        """
        提取音符級別的詳細特徵（用於逐字匹配）

        Args:
            audio_path: 音頻文件路徑

        Returns:
            notes: 音符列表，每個包含 {start, end, pitch, loudness}
        """
        y, sr = self.load_audio(audio_path)

        # 使用更精確的音高檢測
        f0, voiced_flag, voiced_probs = librosa.pyin(
            y,
            fmin=librosa.note_to_hz('C2'),
            fmax=librosa.note_to_hz('C7'),
            sr=sr,
            frame_length=2048,
            hop_length=256  # 更小的hop_length以獲得更高時間解析度
        )

        # 提取音量
        rms = librosa.feature.rms(y=y, frame_length=2048, hop_length=256)[0]

        # 將幀轉換為時間
        times = librosa.frames_to_time(np.arange(len(f0)), sr=sr, hop_length=256)

        # 檢測音符邊界（音高或音量變化顯著的地方）
        notes = []
        current_note = None

        for i in range(len(f0)):
            # 跳過無音高的幀
            if not voiced_flag[i] or np.isnan(f0[i]) or rms[i] < np.mean(rms) * 0.2:
                # 如果之前有音符在進行中，結束它
                if current_note is not None:
                    current_note['end'] = times[i]
                    current_note['duration'] = current_note['end'] - current_note['start']
                    if current_note['duration'] > 0.05:  # 過濾掉太短的音符
                        notes.append(current_note)
                    current_note = None
                continue

            # 檢查是否需要開始新音符
            should_start_new = False
            if current_note is None:
                should_start_new = True
            else:
                # 音高變化超過0.5個半音，視為新音符
                pitch_diff = abs(12 * np.log2(f0[i] / current_note['pitch']))
                if pitch_diff > 0.5:
                    should_start_new = True

            if should_start_new:
                # 結束舊音符
                if current_note is not None:
                    current_note['end'] = times[i]
                    current_note['duration'] = current_note['end'] - current_note['start']
                    if current_note['duration'] > 0.05:
                        notes.append(current_note)

                # 開始新音符
                current_note = {
                    'start': times[i],
                    'pitch': f0[i],
                    'loudness': rms[i],
                    'pitch_values': [f0[i]],
                    'loudness_values': [rms[i]]
                }
            else:
                # 累積當前音符的數據
                current_note['pitch_values'].append(f0[i])
                current_note['loudness_values'].append(rms[i])
                # 更新平均值
                current_note['pitch'] = np.median(current_note['pitch_values'])
                current_note['loudness'] = np.mean(current_note['loudness_values'])

        # 結束最後一個音符
        if current_note is not None:
            current_note['end'] = times[-1]
            current_note['duration'] = current_note['end'] - current_note['start']
            if current_note['duration'] > 0.05:
                notes.append(current_note)

        # 為每個音符計算額外特徵
        for note in notes:
            # 計算音高變化（滑音、顫音等）
            if len(note['pitch_values']) > 1:
                pitch_var = np.std(note['pitch_values'])
                note['pitch_variation'] = pitch_var
                # 檢測音高趨勢（上升/下降）
                note['pitch_trend'] = np.polyfit(
                    np.arange(len(note['pitch_values'])),
                    note['pitch_values'],
                    1
                )[0]
            else:
                note['pitch_variation'] = 0
                note['pitch_trend'] = 0

            # 清理臨時數據
            del note['pitch_values']
            del note['loudness_values']

        return notes

    def align_lyrics_to_notes(self, lyrics, notes):
        """
        將歌詞對齊到音符

        Args:
            lyrics: 歌詞字符串
            notes: 音符列表

        Returns:
            aligned: 對齊後的列表，每個元素包含 {char, note}
        """
        # 移除空白字符，保留所有可見字符
        chars = [c for c in lyrics if not c.isspace()]

        if len(chars) == 0 or len(notes) == 0:
            return []

        # 簡單策略：均勻分配字符到音符
        # 更複雜的策略可以使用時長信息
        aligned = []

        if len(chars) <= len(notes):
            # 字少音符多：每個字對應一個或多個音符
            chars_per_note = len(notes) / len(chars)
            for i, char in enumerate(chars):
                # 為這個字分配音符
                start_note_idx = int(i * chars_per_note)
                end_note_idx = int((i + 1) * chars_per_note)
                note_group = notes[start_note_idx:end_note_idx]

                if note_group:
                    # 合併這組音符的特徵
                    merged_note = {
                        'start': note_group[0]['start'],
                        'end': note_group[-1]['end'],
                        'duration': note_group[-1]['end'] - note_group[0]['start'],
                        'pitch': np.mean([n['pitch'] for n in note_group]),
                        'loudness': np.mean([n['loudness'] for n in note_group]),
                        'pitch_variation': np.mean([n.get('pitch_variation', 0) for n in note_group]),
                        'pitch_trend': np.mean([n.get('pitch_trend', 0) for n in note_group])
                    }
                    aligned.append({'char': char, 'note': merged_note})
        else:
            # 字多音符少：多個字共享一個音符
            notes_per_char = len(chars) / len(notes)
            for i, note in enumerate(notes):
                # 為這個音符分配字符
                start_char_idx = int(i * notes_per_char)
                end_char_idx = int((i + 1) * notes_per_char)
                char_group = chars[start_char_idx:end_char_idx]

                # 將音符時長均分給這些字
                if char_group:
                    duration_per_char = note['duration'] / len(char_group)
                    for j, char in enumerate(char_group):
                        char_note = note.copy()
                        char_note['start'] = note['start'] + j * duration_per_char
                        char_note['end'] = note['start'] + (j + 1) * duration_per_char
                        char_note['duration'] = duration_per_char
                        aligned.append({'char': char, 'note': char_note})

        return aligned

    def save_audio(self, audio, output_path, sr=None):
        """
        保存音頻文件

        Args:
            audio: 音頻數據
            output_path: 輸出路徑
            sr: 採樣率
        """
        if sr is None:
            sr = self.sample_rate

        sf.write(output_path, audio, sr)
        return output_path

    def mix_audio(self, melody_audio, vocal_audio, output_path, melody_volume=0.6, vocal_volume=1.0):
        """
        混合旋律和人聲音頻

        Args:
            melody_audio: 旋律音頻數據或路徑
            vocal_audio: 人聲音頻數據或路徑
            output_path: 輸出路徑
            melody_volume: 旋律音量
            vocal_volume: 人聲音量

        Returns:
            output_path: 輸出文件路徑
        """
        # 如果是路徑，載入音頻
        if isinstance(melody_audio, str):
            melody, sr1 = self.load_audio(melody_audio)
        else:
            melody = melody_audio
            sr1 = self.sample_rate

        if isinstance(vocal_audio, str):
            vocal, sr2 = self.load_audio(vocal_audio)
        else:
            vocal = vocal_audio
            sr2 = self.sample_rate

        # 確保長度一致
        min_len = min(len(melody), len(vocal))
        melody = melody[:min_len]
        vocal = vocal[:min_len]

        # 混合
        mixed = melody * melody_volume + vocal * vocal_volume

        # 歸一化避免削波
        mixed = mixed / np.max(np.abs(mixed)) * 0.9

        # 保存
        self.save_audio(mixed, output_path, sr1)
        return output_path
