from pydub import AudioSegment
from pydub.silence import split_on_silence
import collections
import contextlib
import sys
import wave
import webrtcvad
import pyttsx3
import os


def generate_auido(text):
    print('Audio start')
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')       #getting details of current voice
    #engine.setProperty('voice', voices[0].id)  #changing index, changes voices. o for male
    engine.setProperty('voice', voices[1].id) 
    engine.setProperty('rate', 180)
    filename = "./src/static/audio/temp.wav"
    engine.save_to_file(text, filename)
    engine.runAndWait()
    engine.stop()
    print('Audio Completed!')
    remove_silence(filename)
    return filename

# Reading and splitting the audio file into chunks
def remove_silence(file_name):
    sound = AudioSegment.from_file(file_name, format = "wav")
    audio_chunks = split_on_silence(sound
                                ,min_silence_len = 100
                                ,silence_thresh = -45
                                ,keep_silence = 50
                            )

    # Putting the file back together
    combined = AudioSegment.empty()
    for chunk in audio_chunks:
        combined += chunk
    combined.export(file_name, format = "wav")
    
    