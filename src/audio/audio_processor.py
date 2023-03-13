from moviepy.editor import *


def read_audio_clip(filename) -> CompositeAudioClip:
    audioclip = AudioFileClip(filename=filename)
    new_audioclip = CompositeAudioClip([audioclip])
    return new_audioclip


if __name__ == '__main__':
    clip = read_audio_clip('/Users/yauhenim/JACK/media-empire/tmp/en-US-Neural2-J_sample.mp3')
    print(clip)
