from moviepy.editor import AudioFileClip, CompositeAudioClip



speech_clip = AudioFileClip("../output_audios/rvc_output_20240126-122416.wav")
music_clip = AudioFileClip("assets/music.wav")
music_clip = music_clip.volumex(0.01)
speech_duration = speech_clip.duration
music_clip = music_clip.subclip(0, speech_duration)
combined = CompositeAudioClip([music_clip, speech_clip.set_start(0)])
combined.write_audiofile("assets/speech_with_music.wav", fps=44100)
