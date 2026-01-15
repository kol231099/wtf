import librosa
import numpy as np
import soundfile as sf
from scipy import signal
from pydub import AudioSegment
import os


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
