import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    def __init__(self):
        self.CORS_ORIGINS = self.get_required_env("CORS_ORIGINS")
        self.BANGLA_ASR_MODEL = self.get_required_env("BANGLA_ASR_MODEL")
        self.ENGLISH_ASR_MODEL = self.get_required_env("ENGLISH_ASR_MODEL")
        self.HUGGINGFACE_PIPELINE = self.get_required_env("HUGGINGFACE_PIPELINE")

        self.A_SPEECH_CLIENT_ID = self.get_required_env("A_SPEECH_CLIENT_ID") 
        self.A_SPEECH_CLIENT_SECRET = self.get_required_env("A_SPEECH_CLIENT_SECRET") 
        self.A_SPEECH_SERVER_SECRET = self.get_required_env("A_SPEECH_SERVER_SECRET") 

        self.B_SPEECH_CLIENT_ID = self.get_required_env("B_SPEECH_CLIENT_ID") 
        self.B_SPEECH_CLIENT_SECRET = self.get_required_env("B_SPEECH_CLIENT_SECRET") 
        self.B_SPEECH_SERVER_SECRET = self.get_required_env("B_SPEECH_SERVER_SECRET") 

        self.C_SPEECH_CLIENT_ID = self.get_required_env("C_SPEECH_CLIENT_ID") 
        self.C_SPEECH_CLIENT_SECRET = self.get_required_env("C_SPEECH_CLIENT_SECRET")     
        self.C_SPEECH_SERVER_SECRET = self.get_required_env("C_SPEECH_SERVER_SECRET")     
        
        
    def get_required_env(self, env_variable):
        value = os.getenv(env_variable)
        if value is None:
            error_message = f"Invalid or missing '{env_variable}' in the environment variables"
            return error_message
        return value