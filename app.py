import os
from flask_cors import CORS
from flask import Flask, request, jsonify
from transformers import pipeline
from pydub import AudioSegment

app = Flask(__name__)
CORS(app)

# Load the transcriber model
transcriber = pipeline("automatic-speech-recognition", model="openai/whisper-base.en")

@app.route('/transcribe', methods=['POST'])
def transcribe():
    if 'audio' not in request.files:
        return jsonify({"error": "No audio file provided"}), 400

    audio_file = request.files['audio']

    # Create a temporary directory if it doesn't exist
    temp_dir = 'uploads_audio'
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)

    file_path = os.path.join(temp_dir, 'temp_audio.wav')

    try:
        # Convert the audio file to WAV format if necessary
        audio = AudioSegment.from_file(audio_file)
        audio = audio.set_channels(1)  # Ensure mono audio
        audio.export(file_path, format="wav")
    except Exception as e:
        return jsonify({"error": f"Failed to process audio file: {str(e)}"}), 500

    try:
        # Use the transcriber pipeline
        transcription = transcriber(file_path)["text"]
    except Exception as e:
        return jsonify({"error": f"Failed to transcribe audio: {str(e)}"}), 500

    return jsonify({"transcription": transcription})

if __name__ == "__main__":
    app.run(debug=True)
