from flask import Flask, request, jsonify
import logging
from dotenv import load_dotenv
from scripts.generate_video import generate_video
from flask_cors import CORS 
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
app = Flask(__name__)
CORS(app) 

@app.route('/generate_video', methods=['POST'])
def generate_video_endpoint():
    try:
        request_data = request.json
        data = request_data.get('data', {})
        video_size = [1920, 1080] if data.get('video_size') == "9:16" else [1080, 1920]
        topic = data.get('topic', "")
        system_prompt = data.get("system_prompt") 
        voice = data.get('voice', '1')
        subtitle_style = data.get('subtitle_style', "FontSize=15,PrimaryColour=&HFFFFFF&,Alignment=10")
        music_path = data.get('music', "./assets/music/1.wav")
        model = 'llama2:13b'
        generate_video(topic, system_prompt, model,music_path,subtitle_style, voice, video_size)
        return jsonify({'status': 'success'}), 200
    except Exception as e:
        logging.error(f"Error during video generation process: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')
