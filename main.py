from flask import Flask, request, jsonify
from transformers import pipeline
from flask_cors import CORS
import tempfile
import os
import wave
import numpy as np
from scipy.io.wavfile import write, read
import librosa
import soundfile as sf


transcriber = pipeline("automatic-speech-recognition", model="openai/whisper-base.en")


filename='uploads_audio/temp_audio.wav'

# sampling_rate, audio_array = read(filename)
# sampling_rate, audio_array =librosa.load(filename, sr=16000, mono=True)
# sampling_rate, audio_array =sf.read(filename)
audio_array, sampling_rate = sf.read(filename, channels=1, samplerate=44100, subtype='FLOAT')
print('sampling_rate: ', sampling_rate)
print('audio_array: ', audio_array)

# Normalize the audio
if audio_array.ndim > 1:  # Convert to mono if stereo
    audio_array = audio_array.mean(axis=1)
audio_array = audio_array.astype(np.float32)
audio_array /= np.max(np.abs(audio_array))


# Perform transcription
result = transcriber({
    "sampling_rate": sampling_rate,
    "raw": audio_array,
    "language": "en",
})["text"]

print('result: ', result)


transcription = result  # Store actual transcription result

