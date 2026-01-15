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
    TTS_VOICE = 'nova'  # 可選: alloy, echo, fable, onyx, nova, shimmer
    TTS_SPEED_MIN = 0.25
    TTS_SPEED_MAX = 4.0

    # GPT 配置
    GPT_MODEL = 'gpt-4o-mini'
    GPT_TEMPERATURE = 0.7
    GPT_MAX_TOKENS = 2000

    # Whisper 配置
    WHISPER_MODEL = 'whisper-1'

    # 音頻混合配置
    DEFAULT_MELODY_VOLUME = 0.5
    DEFAULT_VOCAL_VOLUME = 0.8

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
