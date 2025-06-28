"""
Configuration settings for Voice Chat Application
Loads settings from environment variables with sensible defaults
"""

import os
from pathlib import Path
from typing import List
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def get_bool_env(key: str, default: bool = False) -> bool:
    """Get boolean value from environment variable"""
    value = os.getenv(key, str(default)).lower()
    return value in ('true', '1', 'yes', 'on')

def get_int_env(key: str, default: int) -> int:
    """Get integer value from environment variable"""
    try:
        return int(os.getenv(key, str(default)))
    except ValueError:
        return default

def get_float_env(key: str, default: float) -> float:
    """Get float value from environment variable"""
    try:
        return float(os.getenv(key, str(default)))
    except ValueError:
        return default

def get_list_env(key: str, default: List[str]) -> List[str]:
    """Get list value from environment variable (comma-separated)"""
    value = os.getenv(key)
    if value:
        return [item.strip() for item in value.split(',')]
    return default

# Base directory for the project
BASE_DIR = Path(__file__).parent.parent.parent

# Audio Recording Settings
CHUNK_SIZE = get_int_env('CHUNK_SIZE', 1024)
SAMPLE_RATE = get_int_env('SAMPLE_RATE', 16000)
CHANNELS = get_int_env('CHANNELS', 1)
RECORD_DURATION = get_int_env('RECORD_DURATION', 4)
AUDIO_FORMAT = os.getenv('AUDIO_FORMAT', 'wav')

# Voice Activity Detection
SILENCE_THRESHOLD = get_int_env('SILENCE_THRESHOLD', 20)
SILENCE_DURATION = get_float_env('SILENCE_DURATION', 3.5)
MIN_RECORDING_DURATION = get_float_env('MIN_RECORDING_DURATION', 1.5)
PRE_BUFFER_DURATION = get_float_env('PRE_BUFFER_DURATION', 2.0)
VOLUME_SMOOTHING_WINDOW = get_int_env('VOLUME_SMOOTHING_WINDOW', 5)
AMBIENT_NOISE_CALIBRATION_TIME = get_float_env('AMBIENT_NOISE_CALIBRATION_TIME', 1.0)

# Model Settings
WHISPER_MODEL_SIZE = os.getenv('WHISPER_MODEL_SIZE', 'base')
WHISPER_DEVICE = os.getenv('WHISPER_DEVICE', 'cuda')
WHISPER_COMPUTE_TYPE = os.getenv('WHISPER_COMPUTE_TYPE', 'int8_float16')

# XTTS Settings
XTTS_MODEL = os.getenv('XTTS_MODEL', 'tts_models/multilingual/multi-dataset/xtts_v2')
XTTS_LANGUAGE = os.getenv('XTTS_LANGUAGE', 'es')

# File Paths - Using environment variables with fallbacks
TEMP_AUDIO_DIR = BASE_DIR / os.getenv('TEMP_AUDIO_DIR', 'temp/audio')
AI_AUDIO_DIR = BASE_DIR / os.getenv('AI_AUDIO_DIR', 'ai-generated-audio')
VOICE_SAMPLE_PATH = BASE_DIR / os.getenv('VOICE_SAMPLE_PATH', 'voice-samples/sample.wav')

# Derived file paths
TEMP_INPUT_FILE = "temp_input.wav"
TEMP_OUTPUT_FILE = "temp_output.wav"

# Ensure directories exist
TEMP_AUDIO_DIR.mkdir(parents=True, exist_ok=True)
AI_AUDIO_DIR.mkdir(parents=True, exist_ok=True)

# Convert paths to strings for backward compatibility
TEMP_AUDIO_DIR = str(TEMP_AUDIO_DIR)
AI_AUDIO_DIR = str(AI_AUDIO_DIR)
XTTS_VOICE_SAMPLE = str(VOICE_SAMPLE_PATH) if VOICE_SAMPLE_PATH.exists() else None

# Exit Commands
EXIT_COMMANDS = get_list_env('EXIT_COMMANDS', ['exit', 'quit', 'stop', 'goodbye', 'bye'])

# OpenRouter AI Settings
OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY', '')
OPENROUTER_MODEL = os.getenv('OPENROUTER_MODEL', 'openai/gpt-4')
OPENROUTER_BASE_URL = os.getenv('OPENROUTER_BASE_URL', 'https://openrouter.ai/api/v1')

# AI Personality & Behavior
AI_SYSTEM_PROMPT = os.getenv(
    'AI_SYSTEM_PROMPT',
    """You are a casual, friendly AI companion. Respond in a conversational, 
relaxed way like you're chatting with a good friend. Keep responses concise but engaging, 
and feel free to use casual language and expressions. Keep your responses relatively short 
since they will be spoken aloud."""
)

CONVERSATION_MEMORY_LENGTH = get_int_env('CONVERSATION_MEMORY_LENGTH', 5)

# Audio Buffering Settings
BUFFER_AUDIO_BEFORE_PLAYBACK = get_bool_env('BUFFER_AUDIO_BEFORE_PLAYBACK', True)
AUDIO_QUALITY_CHECK = get_bool_env('AUDIO_QUALITY_CHECK', True)
TTS_GENERATION_TIMEOUT = get_int_env('TTS_GENERATION_TIMEOUT', 30)
AUDIO_MIN_FILE_SIZE = get_int_env('AUDIO_MIN_FILE_SIZE', 1024)
AUDIO_VALIDATION_DELAY = get_float_env('AUDIO_VALIDATION_DELAY', 0.5)

# Application Settings
SHOW_TRANSCRIPTION = get_bool_env('SHOW_TRANSCRIPTION', True)
SHOW_AI_RESPONSE = get_bool_env('SHOW_AI_RESPONSE', True)
CLEANUP_ON_EXIT = get_bool_env('CLEANUP_ON_EXIT', True)
VERBOSE_MODE = get_bool_env('VERBOSE_MODE', False)

# AI Audio Saving Settings
SAVE_AI_AUDIO = get_bool_env('SAVE_AI_AUDIO', True)
AI_AUDIO_FILENAME_FORMAT = os.getenv('AI_AUDIO_FILENAME_FORMAT', 'ai_audio_{timestamp}_{counter:03d}.wav')
MAX_SAVED_AUDIO_FILES = get_int_env('MAX_SAVED_AUDIO_FILES', 100)

# Configuration validation
def validate_config():
    """Validate configuration settings"""
    errors = []
    
    if not OPENROUTER_API_KEY or OPENROUTER_API_KEY == 'your-api-key-here':
        errors.append("OPENROUTER_API_KEY is not set. Please configure your API key in .env file.")
    
    if WHISPER_DEVICE not in ['cpu', 'cuda']:
        errors.append(f"Invalid WHISPER_DEVICE: {WHISPER_DEVICE}. Must be 'cpu' or 'cuda'.")
    
    if WHISPER_MODEL_SIZE not in ['tiny', 'base', 'small', 'medium', 'large-v3']:
        errors.append(f"Invalid WHISPER_MODEL_SIZE: {WHISPER_MODEL_SIZE}")
    
    if SAMPLE_RATE not in [8000, 16000, 22050, 44100, 48000]:
        errors.append(f"Unusual SAMPLE_RATE: {SAMPLE_RATE}. Recommended: 16000")
    
    return errors

# Print configuration warnings if any
config_errors = validate_config()
if config_errors and not os.getenv('SUPPRESS_CONFIG_WARNINGS'):
    print("⚠️  Configuration warnings:")
    for error in config_errors:
        print(f"   - {error}")
    print()
