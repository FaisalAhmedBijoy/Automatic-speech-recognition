import jwt  
import soundfile as sf
import numpy as np
import noisereduce as nr
from transformers import pipeline
from starlette.websockets import WebSocketState
from jwt import ExpiredSignatureError, InvalidTokenError
from scipy.signal import butter, lfilter

from app.config.configurations import Config
config = Config()

A_SPEECH_CLIENT_ID = config.A_SPEECH_CLIENT_ID
A_SPEECH_CLIENT_SECRET = config.A_SPEECH_CLIENT_SECRET
A_SPEECH_SERVER_SECRET  = config.A_SPEECH_SERVER_SECRET

B_SPEECH_CLIENT_ID = config.B_SPEECH_CLIENT_ID
B_SPEECH_CLIENT_SECRET  = config.B_SPEECH_CLIENT_SECRET
B_SPEECH_SERVER_SECRET  = config.B_SPEECH_SERVER_SECRET

C_SPEECH_CLIENT_ID = config.C_SPEECH_CLIENT_ID
C_SPEECH_CLIENT_SECRET  = config.C_SPEECH_CLIENT_SECRET
C_SPEECH_SERVER_SECRET  = config.C_SPEECH_SERVER_SECRET

def butter_highpass(cutoff, sr, order=5):
    nyquist = 0.5 * sr
    normal_cutoff = cutoff / nyquist
    b, a = butter(order, normal_cutoff, btype='high', analog=False)
    return b, a

def highpass_filter(audio, cutoff=100, sr=16000, order=5):
    b, a = butter_highpass(cutoff, sr, order)
    return lfilter(b, a, audio)

def encode_response_key(unique_key, backend_secret):
    payload = {"key": unique_key}
    return jwt.encode(payload, backend_secret, algorithm="HS256")

def decode_key(encoded_key, frontend_secret):
    try:
        decoded = jwt.decode(
            encoded_key, 
            frontend_secret, 
            algorithms=["HS256"],
            options={"verify_aud": False}  
        )
        return decoded.get("key")
    except ExpiredSignatureError:
        print("Token has expired.")
        return None
    except InvalidTokenError as e:
        print(f"Invalid token: {e}")
        return None

def get_secrets(client_id):
    if client_id == A_SPEECH_CLIENT_ID:
        return A_SPEECH_CLIENT_SECRET, A_SPEECH_SERVER_SECRET
    elif client_id == B_SPEECH_CLIENT_ID:
        return B_SPEECH_CLIENT_SECRET, B_SPEECH_SERVER_SECRET
    elif client_id == C_SPEECH_CLIENT_ID:
        return C_SPEECH_CLIENT_SECRET, C_SPEECH_SERVER_SECRET
    return None, None
