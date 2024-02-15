from moviepy.editor import *
import pysrt
from auto_subtitle.cli import VideoTranscriber
import yake
from bing_image_downloader import downloader
import os
import random
from moviepy.editor import ImageClip, TextClip, CompositeVideoClip
from PIL import Image
import subprocess
import logging

def convert_srt_to_ass(srt_file, ass_file):
    command = [
        'ffmpeg',
        '-i', srt_file,
        ass_file
    ]
    subprocess.run(command, check=True)

def add_styled_subtitles_to_video(video_file, subtitle_file, output_file, subtitle_style='', ):
    command = [
        'ffmpeg',
        '-i', video_file,
        '-vf', f"subtitles={subtitle_file}:force_style='{subtitle_style}'",
        '-c:v', "libx264",
        '-c:a', 'copy',

        output_file
    ]


    subprocess.run(command, check=True)

def srt_time_to_seconds(srt_time):
    return srt_time.hours * 3600 + srt_time.minutes * 60 + srt_time.seconds + srt_time.milliseconds / 1000

def extract_key_phrase(sentence):
    kw_extractor = yake.KeywordExtractor(top=1, stopwords=None)
    keywords = kw_extractor.extract_keywords(sentence)
    if keywords:
        return keywords[0][0]
    else:
        return sentence

def pick_random_file(directory):
    files = [os.path.join(directory, f) for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
    if files:
        return random.choice(files)
    else:
        return None


def validate_path(path, default_path=""):
    if path is None or not os.path.exists(path):
        logging.warning(f"Invalid path: {path}. Using default: {default_path}")
        return default_path
    return path

def get_image(text_input):
    key_phrase = extract_key_phrase(text_input)
    try:
        folder_path = downloader.download(key_phrase, limit=5, output_dir='images', adult_filter_off=True, force_replace=False, timeout=60, verbose=False)
        image_path = pick_random_file(folder_path)
        if image_path is None:
            raise FileNotFoundError("No images found; using default.")
        return image_path
    except Exception as e:
        script_directory = os.path.dirname(os.path.abspath(__file__))
        print("Script directory:", script_directory)
        logging.info(f"Script directory: {script_directory}")
        logging.error(f"Error fetching image for {text_input}: {e}")
        return "./assets/image.jpg" 

vt = VideoTranscriber(model="base", output_dir="assets", output_srt=True, srt_only=True, verbose=False)

def create_video_with_subtitles(audio_file_path, output_video_path, pre_sub_video_name, ass_subtitles_path, video_size, subtitle_style):
    subtitle_dict = vt.transcribe_video([audio_file_path])  
    subtitles_path = subtitle_dict.get(audio_file_path)
    if subtitles_path is None:
        raise ValueError(f"No subtitles generated for {audio_file_path}")
    subtitles_path = validate_path(subtitles_path, "path/to/default/subtitles.srt")  
    audio_clip = AudioFileClip(audio_file_path)
    video_clip = ColorClip(size=video_size, color=(0, 0, 0), duration=audio_clip.duration).set_audio(audio_clip)
    subs = pysrt.open(subtitles_path)
    clips = []
    for sub in subs:
        start_time = srt_time_to_seconds(sub.start)
        end_time = srt_time_to_seconds(sub.end)
        duration = end_time - start_time
        image_path = get_image(sub.text)
        image_path = validate_path(image_path)  
        with Image.open(image_path) as img:
            if img.mode != 'RGB':
                img = img.convert('RGB')
            img.save(image_path)
        img_clip = ImageClip(image_path).resize(newsize=video_size).set_duration(duration).set_start(start_time)
        clips.append(img_clip)

    final_video = CompositeVideoClip([video_clip, *clips])
    final_video.write_videofile(pre_sub_video_name, codec="libx264", fps=30)
    convert_srt_to_ass(subtitles_path, ass_subtitles_path)
    add_styled_subtitles_to_video(pre_sub_video_name, ass_subtitles_path, output_video_path, subtitle_style)

logging.basicConfig(level=logging.INFO)

