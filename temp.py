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

app = Flask(__name__)
CORS(app)
transcriber = pipeline("automatic-speech-recognition", model="openai/whisper-base.en")

@app.route('/transcribe', methods=['POST'])
def transcribe():
    if 'audio' not in request.files:
        return jsonify({"error": "No audio file provided"}), 400

    audio_file = request.files['audio']

    # Create the directory if it doesn't exist
    temp_dir = 'uploads_audio'
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)

    file_path = os.path.join(temp_dir, 'temp_audio.wav')

    try:
        # Save the audio file
        audio_file.save(file_path)
    except Exception as e:
        return jsonify({"error": f"Failed to save audio file: {str(e)}"}), 500

    try:
        # Load the audio file with librosa
        # audio_array, sampling_rate = librosa.load(file_path, sr=None)  # Keep original sampling rate
        # audio_array, sampling_rate = sf.read(file_path, dtype='float32')
        sampling_rate, audio_array = read(filename)
        print('sampling_rate: ', sampling_rate)
        print('audio_array: ', audio_array)

        # Normalize the audio
        if audio_array.ndim > 1:  # Convert to mono if stereo
            audio_array = audio_array.mean(axis=1)
        audio_array = audio_array.astype(np.float32)
        audio_array /= np.max(np.abs(audio_array))

        try:
            # Perform transcription
            result = transcriber({
                "sampling_rate": sampling_rate,
                "raw": audio_array,
                "language": "en",
            })["text"]

            print('result: ', result)
        except Exception as e:
            return jsonify({"error": str(e)}), 500

        transcription = result  # Store actual transcription result
    except Exception as e:
        return jsonify({"error": f"Failed to process audio file: {str(e)}"}), 500

    return jsonify({"transcription": transcription})

if __name__ == '__main__':
    app.run(debug=True)
