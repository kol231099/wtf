"""
配置文件 - 集中管理應用配置
"""

import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """基礎配置類"""

    # Flask 配置
    SECRET_KEY = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = os.getenv('FLASK_ENV', 'development') == 'development'

    # 文件上傳配置
    UPLOAD_FOLDER = 'uploads'
    OUTPUT_FOLDER = 'outputs'
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50MB
    ALLOWED_EXTENSIONS = {'wav', 'mp3', 'flac', 'm4a'}

    # OpenAI 配置
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

    # 音頻處理配置
    AUDIO_SAMPLE_RATE = 22050
    AUDIO_CHANNELS = 1  # 單聲道

    # TTS 配置
    TTS_MODEL = 'tts-1-hd'
    TTS_VOICE = 'shimmer'  # 可選: alloy, echo, fable, onyx, nova, shimmer
                           # shimmer: 較柔和，適合歌唱
                           # nova: 較有活力
    TTS_SPEED_MIN = 0.25
    TTS_SPEED_MAX = 4.0
    TTS_SPEED_FACTOR = 0.8  # 速度調整係數（0.7-0.9，越小越慢）

    # GPT 配置
    GPT_MODEL = 'gpt-4o-mini'
    GPT_TEMPERATURE = 0.7
    GPT_MAX_TOKENS = 2000

    # Whisper 配置
    WHISPER_MODEL = 'whisper-1'

    # 音頻混合配置
    DEFAULT_MELODY_VOLUME = 0.5
    DEFAULT_VOCAL_VOLUME = 0.8

    # 音樂表現力配置
    # 顫音參數
    VIBRATO_RATE = 5.5      # 顫音頻率 (Hz)，通常 4-7 Hz
    VIBRATO_DEPTH = 0.4     # 顫音深度（半音），通常 0.3-1.0
                            # 較小的值 (0.3-0.5) 更自然
                            # 較大的值 (0.7-1.0) 更有戲劇性

    # 音高調整參數
    PITCH_CONTOUR_ENABLED = True    # 是否啟用動態音高跟隨
    PITCH_CONTOUR_SEGMENTS = 20     # 音高調整的分段數（越多越精細但越慢）

    # 動態包絡參數
    DYNAMIC_ENVELOPE_ENABLED = True  # 是否啟用動態音量調整
    ENVELOPE_MELODY_WEIGHT = 0.7    # 旋律動態的權重（0-1）
    ENVELOPE_VOCAL_WEIGHT = 0.3     # 原始人聲動態的權重（0-1）

    # 處理配置
    CLEANUP_OLD_FILES = True  # 是否自動清理舊文件
    FILE_RETENTION_HOURS = 24  # 文件保留時間（小時）


class DevelopmentConfig(Config):
    """開發環境配置"""
    DEBUG = True
    TESTING = False


class ProductionConfig(Config):
    """生產環境配置"""
    DEBUG = False
    TESTING = False

    # 生產環境應該使用更強的密鑰
    SECRET_KEY = os.getenv('FLASK_SECRET_KEY')

    # 可以添加其他生產環境專用配置
    # 例如：數據庫連接、Redis、日誌等


class TestingConfig(Config):
    """測試環境配置"""
    DEBUG = True
    TESTING = True

    # 測試環境使用臨時目錄
    UPLOAD_FOLDER = 'test_uploads'
    OUTPUT_FOLDER = 'test_outputs'


# 配置字典
config_by_name = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}


def get_config(config_name='default'):
    """
    獲取配置對象

    Args:
        config_name: 配置名稱 (development, production, testing)

    Returns:
        Config: 配置類實例
    """
    return config_by_name.get(config_name, DevelopmentConfig)
