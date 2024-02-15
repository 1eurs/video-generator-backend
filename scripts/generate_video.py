import os
import time
import logging
from dotenv import load_dotenv
from ml_models.llm import generate_script
from ml_models.rvc.rvc import change_voice_characteristics
from .align_music_with_speech import merge_audio_with_music
from .text_to_images import create_video_with_subtitles
from ml_models.StyleTTS2 import synthesize_speech
import datetime


load_dotenv()
audio_dir = "./audio"
video_dir = "./video"
sub_dir = "./sub"

def create_directories():
    for directory in [audio_dir, video_dir, sub_dir]:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"Created directory: {directory}")

create_directories()

def generate_unique_filename(prefix='', extension=''):
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"{prefix}_{timestamp}.{extension}" if prefix else f"{timestamp}.{extension}"
    return filename

styletts_audio = f"./audio/{generate_unique_filename(prefix='tts', extension='wav')}"
changed_voice_audio = f"./audio/{generate_unique_filename(prefix='rvc', extension='wav')}"
final_audio = f"./audio/{generate_unique_filename(prefix='final', extension='wav')}"
final_video = f"./video/{generate_unique_filename(prefix='final', extension='mp4')}"
pre_subtitle_video = f"./video/{generate_unique_filename(prefix='presub', extension='mp4')}"
subtitle = f"./sub/{generate_unique_filename(prefix='sub', extension='ass')}"


def generate_video(topic, system_prompt, model, music_path , subtitle_style ,voice ,video_size):
    music_path="./assets/music/1.wav"
    rvc_model = f'./ml_models/rvc/models/1.pth'
    try:
        script = generate_script(topic, system_prompt, model)
        synthesize_speech(script, styletts_audio)
        change_voice_characteristics(output_audio_before_vc_path= styletts_audio, output_audio_after_vc_path =changed_voice_audio,model_path= rvc_model)
        merge_audio_with_music(speech_file = changed_voice_audio, music_file = music_path , output_file= final_audio)
        create_video_with_subtitles(final_audio, final_video, pre_subtitle_video,subtitle, video_size,subtitle_style)
        logging.info("Video generation completed successfully.")
        return final_video
    except Exception as e:
        logging.error(f"Error during video generation process: {e}")
        raise


