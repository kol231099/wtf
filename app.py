from flask import Flask, render_template, request, jsonify, send_file
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
import uuid
from dotenv import load_dotenv

# 應用 scipy 兼容性補丁（必須在導入 librosa 之前）
import scipy_compat

from vocal_synthesizer import VocalSynthesizer

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['OUTPUT_FOLDER'] = 'outputs'
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB 上傳限制

CORS(app)

# 確保目錄存在
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)

# 允許的文件格式
ALLOWED_EXTENSIONS = {'wav', 'mp3', 'flac', 'm4a'}


def allowed_file(filename):
    """檢查文件格式是否允許"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def index():
    """主頁面"""
    return render_template('index.html')


@app.route('/api/synthesize', methods=['POST'])
def synthesize():
    """
    處理歌聲合成請求

    期望的表單數據：
    - original_audio: 原始歌曲文件（包含歌詞+旋律）
    - melody_audio: 純旋律文件
    - new_lyrics: 新歌詞文本
    """
    try:
        # 驗證文件是否上傳
        if 'original_audio' not in request.files:
            return jsonify({'error': '缺少原始歌曲文件'}), 400

        if 'melody_audio' not in request.files:
            return jsonify({'error': '缺少純旋律文件'}), 400

        original_file = request.files['original_audio']
        melody_file = request.files['melody_audio']
        new_lyrics = request.form.get('new_lyrics', '')

        if not new_lyrics:
            return jsonify({'error': '請輸入新歌詞'}), 400

        # 驗證文件格式
        if not allowed_file(original_file.filename):
            return jsonify({'error': '原始歌曲文件格式不支援'}), 400

        if not allowed_file(melody_file.filename):
            return jsonify({'error': '旋律文件格式不支援'}), 400

        # 生成唯一的任務 ID
        task_id = str(uuid.uuid4())
        task_dir = os.path.join(app.config['UPLOAD_FOLDER'], task_id)
        output_dir = os.path.join(app.config['OUTPUT_FOLDER'], task_id)
        os.makedirs(task_dir, exist_ok=True)
        os.makedirs(output_dir, exist_ok=True)

        # 保存上傳的文件
        original_filename = secure_filename(original_file.filename)
        melody_filename = secure_filename(melody_file.filename)

        original_path = os.path.join(task_dir, f'original_{original_filename}')
        melody_path = os.path.join(task_dir, f'melody_{melody_filename}')

        original_file.save(original_path)
        melody_file.save(melody_path)

        # 執行合成
        synthesizer = VocalSynthesizer()
        result = synthesizer.synthesize_vocal(
            original_audio_path=original_path,
            melody_path=melody_path,
            new_lyrics=new_lyrics,
            output_dir=output_dir
        )

        if result['success']:
            # 返回結果
            response_data = {
                'success': True,
                'task_id': task_id,
                'steps': result['steps'],
                'original_lyrics': result.get('original_lyrics', ''),
                'aligned_lyrics': result.get('aligned_lyrics', []),
                'lyrics_analysis': result.get('lyrics_analysis', {}),
                'melody_features': result.get('melody_features', {}),
                'files': {
                    'final_output': f'/api/download/{task_id}/final_output.wav',
                    'stretched_vocal': f'/api/download/{task_id}/stretched_vocal.wav',
                    'tts_vocal': f'/api/download/{task_id}/tts_vocal.wav'
                }
            }
            return jsonify(response_data), 200
        else:
            return jsonify({
                'success': False,
                'error': result.get('error', '未知錯誤'),
                'steps': result.get('steps', [])
            }), 500

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'伺服器錯誤: {str(e)}'}), 500


@app.route('/api/download/<task_id>/<filename>')
def download_file(task_id, filename):
    """下載生成的文件"""
    try:
        file_path = os.path.join(app.config['OUTPUT_FOLDER'], task_id, filename)

        if not os.path.exists(file_path):
            return jsonify({'error': '文件不存在'}), 404

        return send_file(file_path, as_attachment=True)

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/health')
def health_check():
    """健康檢查端點"""
    return jsonify({
        'status': 'healthy',
        'openai_api_configured': bool(os.getenv('OPENAI_API_KEY'))
    })


@app.route('/api/test-openai')
def test_openai():
    """測試 OpenAI API 連接"""
    try:
        from ai_service import AIService
        ai_service = AIService()

        # 簡單測試
        response = ai_service.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": "Say 'API working'"}],
            max_tokens=10
        )

        return jsonify({
            'success': True,
            'message': 'OpenAI API 連接正常',
            'response': response.choices[0].message.content
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


if __name__ == '__main__':
    print("正在啟動 AI 歌詞轉換系統...")
    print(f"上傳目錄: {app.config['UPLOAD_FOLDER']}")
    print(f"輸出目錄: {app.config['OUTPUT_FOLDER']}")
    print(f"OpenAI API 已配置: {bool(os.getenv('OPENAI_API_KEY'))}")
    print("\n請在瀏覽器中打開: http://localhost:5000\n")

    app.run(debug=True, host='0.0.0.0', port=5000)
