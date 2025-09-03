import io
import jwt  
import json
import torch
import ffmpeg
import base64

import soundfile as sf
import numpy as np
import noisereduce as nr
from starlette.websockets import WebSocketState
from silero_vad import load_silero_vad, get_speech_timestamps
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import nemo.collections.asr as nemo_asr
import torchaudio

from app.config.configurations import Config
from app.processing.audio_processing import encode_response_key, decode_key, highpass_filter, get_secrets

config = Config()

BANGLA_ASR_MODEL = config.BANGLA_ASR_MODEL
HUGGINGFACE_PIPELINE = config.HUGGINGFACE_PIPELINE

router = APIRouter()
vad_model = load_silero_vad() 
client_audio_buffers = {} 

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
asr_model = nemo_asr.models.ASRModel.from_pretrained(BANGLA_ASR_MODEL)
asr_model.to(device)

# Get model's expected sample rate
expected_sample_rate = asr_model.cfg.train_ds.sample_rate

def clear_client_buffer(client_id: str, unique_key: str) -> None:
    """Clear the audio buffer for a specific client and key."""
    if client_id in client_audio_buffers and unique_key in client_audio_buffers[client_id]:
        del client_audio_buffers[client_id][unique_key]
        if not client_audio_buffers[client_id]:  # If no more keys for this client
            del client_audio_buffers[client_id]
        print(f"Cleared buffer for client_id: {client_id}, unique_key: {unique_key}")

@router.get("/")
async def get_index():  
    return {"message": "Welcome to the Bangla Speech Recognition API!"}

@router.websocket("/bn_audio")
async def process_audio(websocket: WebSocket):
    await websocket.accept()
    current_client_id = None
    current_unique_key = None

    try:
        while WebSocketState.CONNECTED:
            message = await websocket.receive_text()
            data = json.loads(message)

            client_id = data.get("client_id")
            frontend_secret, backend_secret = get_secrets(client_id)

            if not frontend_secret or not backend_secret:
                await websocket.send_json({"status": "error", "message": "Invalid client_id."})
                continue

            encoded_key = data.get("key")
            unique_key = decode_key(encoded_key, frontend_secret)

            if not unique_key:
                await websocket.send_json({"status": "error", "message": "Invalid or expired key."})
                continue

            # Store current session identifiers
            current_client_id = client_id
            current_unique_key = unique_key

            if data.get("stop"):
                print('stop button clicked')
                clear_client_buffer(client_id, unique_key)
                await websocket.send_json({"status": "success", "message": "Recording stopped."})
                continue

            audio_base64 = data.get("audio")
            if not audio_base64:
                await websocket.send_json({"status": "error", "message": "No audio data received."})
                continue

            # Clear any existing buffer before starting new recording
            if client_id not in client_audio_buffers or unique_key not in client_audio_buffers.get(client_id, {}):
                clear_client_buffer(client_id, unique_key)
            
            # Initialize buffer if needed
            client_audio_buffers.setdefault(client_id, {}).setdefault(unique_key, [])
            
            audio_bytes = io.BytesIO(base64.b64decode(audio_base64))
            client_audio_buffers[client_id][unique_key].append(audio_bytes.read())

            # Rest of the processing code remains the same
            combined_audio = b''.join(client_audio_buffers[client_id][unique_key])
            wav_data = ffmpeg.input('pipe:0', format='webm').output('pipe:1', format='wav', ac=1, ar=16000).run(input=combined_audio, capture_stdout=True)[0]

            audio_array, sample_rate = sf.read(io.BytesIO(wav_data))
            
            filtered_audio = highpass_filter(audio_array, cutoff=100, sr=sample_rate)

            reduced_noise_audio = nr.reduce_noise(y=filtered_audio, 
                                                  sr=sample_rate, 
                                                  prop_decrease=0.8,
                                                  n_fft=1024,
                                                  hop_length=512)
            speech_timestamps = get_speech_timestamps(reduced_noise_audio, 
                                                      vad_model, 
                                                      sampling_rate=sample_rate, 
                                                      return_seconds=True)

            if not speech_timestamps:
                await websocket.send_json({"status": "success", "message": "No speech detected."})
                continue
           
            # Ensure audio is float32
            if audio_array.dtype != np.float32:
                audio_array = audio_array.astype(np.float32)

            # Normalize audio (NeMo ASR expects normalized audio)
            audio_array = audio_array / np.max(np.abs(audio_array))
                    
            # If sampling rate is different, resample audio
            if sample_rate != expected_sample_rate:
                resampler = torchaudio.transforms.Resample(orig_freq=sample_rate, new_freq=expected_sample_rate)
                audio_array = resampler(torch.tensor(audio_array)).numpy()
            
            # Transcribe using NeMo
            transcription = asr_model.transcribe([audio_array])

            # print(f"Transcription: {transcription}")
            print(f"Transcription: {transcription[0].text}")
            
            response_key = encode_response_key(unique_key, backend_secret)

            await websocket.send_json({
                "status": "success",
                "client_id": client_id,
                "response_key": response_key,
                "transcription": transcription[0].text,
            })

    except WebSocketDisconnect:
        print("WebSocket disconnected")
        if current_client_id and current_unique_key:
            clear_client_buffer(current_client_id, current_unique_key)
        await websocket.close()
    except Exception as e:
        print(f"Error occurred: {e}")
        if current_client_id and current_unique_key:
            clear_client_buffer(current_client_id, current_unique_key)
        await websocket.close()