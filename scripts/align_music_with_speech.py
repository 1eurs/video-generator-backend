from moviepy.editor import AudioFileClip, CompositeAudioClip
from moviepy.audio.fx.all import volumex

def merge_audio_with_music(speech_file, music_file, output_file, loop_music=True, volume_factor=0.1):
    speech_clip = AudioFileClip(speech_file)
    music_clip = AudioFileClip(music_file)

    if loop_music and music_clip.duration < speech_clip.duration:
        loops_required = int(speech_clip.duration / music_clip.duration) + 1
        music_clips = [music_clip.copy() for _ in range(loops_required)]
        music_clip = CompositeAudioClip(music_clips)
        music_clip = music_clip.set_duration(speech_clip.duration)

    music_clip = music_clip.fx(volumex, volume_factor)

    music_clip = music_clip.set_duration(speech_clip.duration)

    combined = CompositeAudioClip([music_clip.set_start(0), speech_clip.set_start(0)])
    combined.write_audiofile(output_file, fps=44100)
