from moviepy.editor import *
import pysrt
from auto_subtitle.cli import VideoTranscriber
import yake
from bing_image_downloader import downloader
import os
import random
from moviepy.editor import ImageClip, TextClip, CompositeVideoClip
from moviepy.video.fx.all import resize
from PIL import Image
import subprocess

def convert_srt_to_ass(srt_file, ass_file):
    command = [
        'ffmpeg',
        '-i', srt_file,
        ass_file
    ]
    subprocess.run(command, check=True)

def add_styled_subtitles_to_video(video_file, subtitle_file, output_file):
    style_options = "FontSize=16,PrimaryColour=&H00FFFF&"  

    command = [
        'ffmpeg',
        '-i', video_file,
        '-vf', f"subtitles={subtitle_file}:force_style='{style_options}'",
        '-c:v', 'libx264',
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

def get_image(text_input):
    key_phrase = extract_key_phrase(text_input)
    folder_path = downloader.download(key_phrase, limit=5, output_dir='images', adult_filter_off=True, force_replace=False, timeout=60, verbose=False)
    image_path = pick_random_file(folder_path)
    if image_path is None:
        return "assets/Image.jpg"
    return image_path

vt = VideoTranscriber(model="base", output_dir="assets", output_srt=True, srt_only=True, verbose=False)

def create_subtitled_video_from_audio(audio_file_path, output_video_path=None, ass_subtitles_path=None):
    base_name = os.path.splitext(os.path.basename(audio_file_path))[0]
    default_output_video = os.path.join(os.getcwd(), f"{base_name}_video.mp4")
    default_ass_subtitle = os.path.join(os.getcwd(), f"{base_name}_subtitles.ass")

    output_video_path = output_video_path or default_output_video
    ass_subtitles_path = ass_subtitles_path or default_ass_subtitle

    subtitle_dict = vt.transcribe_video([audio_file_path])  
    subtitles_path = subtitle_dict.get(audio_file_path)
    audio_clip = AudioFileClip(audio_file_path)
    video_clip = ColorClip(size=(1080, 1920), color=(0,0,0), duration=audio_clip.duration).set_audio(audio_clip)
    subs = pysrt.open(subtitles_path)
    clips = []

    for sub in subs:
        start_time = srt_time_to_seconds(sub.start)
        end_time = srt_time_to_seconds(sub.end)
        duration = end_time - start_time
        image_path = get_image(sub.text)  # Ensure get_image returns a valid image path
        with Image.open(image_path) as img:
            if img.mode != 'RGB':
                img = img.convert('RGB')
            img.save(image_path)
        img_clip = ImageClip(image_path).resize(newsize=(1080, 1920)).set_duration(duration).set_start(start_time)
        clips.append(img_clip)

    final_video = CompositeVideoClip([video_clip, *clips])
    final_video.write_videofile(output_video_path, codec="libx264", fps=24)

    convert_srt_to_ass(subtitles_path, ass_subtitles_path)
    temp_output_video_path = os.path.join(os.getcwd(), f"{base_name}_temp_video.mp4")
    add_styled_subtitles_to_video(output_video_path, ass_subtitles_path, temp_output_video_path)
    os.rename(temp_output_video_path, output_video_path)


create_subtitled_video_from_audio("assets/speech_with_music.wav", output_video_path=None, ass_subtitles_path=None)
