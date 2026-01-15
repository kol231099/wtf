#!/usr/bin/env python3
"""
測試腳本 - 檢查系統環境和依賴
"""

import sys
import os


def check_python_version():
    """檢查 Python 版本"""
    print("檢查 Python 版本...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print(f"✓ Python 版本: {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"✗ Python 版本過低: {version.major}.{version.minor}.{version.micro}")
        print("  需要 Python 3.8 或更高版本")
        return False


def check_dependencies():
    """檢查必要的依賴包"""
    print("\n檢查依賴包...")
    dependencies = [
        ('flask', 'Flask'),
        ('flask_cors', 'Flask-CORS'),
        ('openai', 'OpenAI'),
        ('librosa', 'Librosa'),
        ('soundfile', 'SoundFile'),
        ('numpy', 'NumPy'),
        ('scipy', 'SciPy'),
        ('pydub', 'Pydub'),
        ('dotenv', 'python-dotenv')
    ]

    all_installed = True
    for module_name, display_name in dependencies:
        try:
            __import__(module_name)
            print(f"✓ {display_name}")
        except ImportError:
            print(f"✗ {display_name} - 未安裝")
            all_installed = False

    return all_installed


def check_env_file():
    """檢查環境變數文件"""
    print("\n檢查環境配置...")
    if os.path.exists('.env'):
        print("✓ .env 文件存在")

        from dotenv import load_dotenv
        load_dotenv()

        api_key = os.getenv('OPENAI_API_KEY')
        if api_key and api_key != 'your_openai_api_key_here':
            print("✓ OpenAI API Key 已配置")
            return True
        else:
            print("✗ OpenAI API Key 未配置或使用默認值")
            print("  請在 .env 文件中設置您的 OpenAI API Key")
            return False
    else:
        print("✗ .env 文件不存在")
        print("  請複製 .env.example 為 .env 並填入您的 API Key")
        return False


def check_directories():
    """檢查必要的目錄"""
    print("\n檢查目錄結構...")
    directories = ['uploads', 'outputs', 'templates', 'static']
    all_exist = True

    for directory in directories:
        if os.path.exists(directory):
            print(f"✓ {directory}/")
        else:
            print(f"✗ {directory}/ - 不存在，正在創建...")
            os.makedirs(directory, exist_ok=True)
            print(f"  已創建 {directory}/")

    return True


def test_openai_connection():
    """測試 OpenAI API 連接"""
    print("\n測試 OpenAI API 連接...")

    try:
        from dotenv import load_dotenv
        load_dotenv()

        from openai import OpenAI

        client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": "Say 'Connection successful'"}],
            max_tokens=10
        )

        print("✓ OpenAI API 連接成功")
        print(f"  回應: {response.choices[0].message.content}")
        return True

    except Exception as e:
        print(f"✗ OpenAI API 連接失敗: {str(e)}")
        return False


def main():
    """主測試函數"""
    print("=" * 60)
    print("AI 歌詞轉換系統 - 環境測試")
    print("=" * 60)

    results = []

    results.append(("Python 版本", check_python_version()))
    results.append(("依賴包", check_dependencies()))
    results.append(("目錄結構", check_directories()))
    results.append(("環境配置", check_env_file()))

    # 只有在前面都通過的情況下才測試 API 連接
    if all(result[1] for result in results):
        results.append(("OpenAI API", test_openai_connection()))

    print("\n" + "=" * 60)
    print("測試結果摘要")
    print("=" * 60)

    for name, passed in results:
        status = "✓ 通過" if passed else "✗ 失敗"
        print(f"{name}: {status}")

    if all(result[1] for result in results):
        print("\n所有測試通過！系統已準備就緒。")
        print("運行 'python app.py' 來啟動應用。")
        return 0
    else:
        print("\n部分測試失敗，請修復上述問題後再試。")
        return 1


if __name__ == '__main__':
    exit(main())
