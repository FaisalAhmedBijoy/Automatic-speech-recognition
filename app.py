from flask import Flask, request, jsonify
from transformers import pipeline
from flask_cors import CORS
import tempfile
import os
import wave
import numpy as np

app = Flask(__name__)
CORS(app)
transcriber = pipeline("automatic-speech-recognition", model="openai/whisper-base.en")

@app.route('/transcribe', methods=['POST'])
def transcribe():
    if 'audio' not in request.files:
        return jsonify({"error": "No audio file provided"}), 400

    audio_file = request.files['audio']
    temp_dir = 'uploads_audio'
    file_path = os.path.join(temp_dir, 'temp_audio.wav')
    audio_file.save(file_path)

    print('audio file: ',audio_file)
    print('file_path: ',file_path)

    with wave.open(file_path, 'rb') as wav_file:
        sr = wav_file.getframerate()
        frames = wav_file.readframes(wav_file.getnframes())
        audio_data = np.frombuffer(frames, dtype=np.int16)

    # Normalize and convert to float32
    audio_data = audio_data.astype(np.float32) / np.iinfo(np.int16).max
    transcription = transcriber({"sampling_rate": sr, "raw": audio_data})["text"]

    return jsonify({"transcription": transcription})

if __name__ == '__main__':
    app.run(debug=True)
