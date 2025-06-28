"""
Configuration settings for Voice Chat Application
"""

import os

# Audio Recording Settings
CHUNK_SIZE = 1024
SAMPLE_RATE = 16000  # 16kHz for optimal Whisper performance
CHANNELS = 1  # Mono audio
RECORD_DURATION = 4  # seconds per recording chunk
AUDIO_FORMAT = 'wav'

# Voice Activity Detection
SILENCE_THRESHOLD = 20  # Increased for more robust detection
SILENCE_DURATION = 3.5  # seconds of silence before stopping recording
MIN_RECORDING_DURATION = 1.5  # minimum recording time to prevent premature stops
PRE_BUFFER_DURATION = 2.0  # seconds to capture before voice activity detection
VOLUME_SMOOTHING_WINDOW = 5  # number of chunks to smooth volume detection
AMBIENT_NOISE_CALIBRATION_TIME = 1.0  # seconds to calibrate ambient noise level

# Model Settings
WHISPER_MODEL_SIZE = "base"  # Options: tiny, base, small, medium, large-v3
WHISPER_DEVICE = "cuda"  # or "cpu"
WHISPER_COMPUTE_TYPE = "int8_float16"  # or "float16" for more VRAM

# XTTS Settings
XTTS_MODEL = "tts_models/multilingual/multi-dataset/xtts_v2"
XTTS_LANGUAGE = "es"  # Default language
XTTS_VOICE_SAMPLE = "voice-samples/sample.wav"  # Path to voice sample for cloning (optional)

# File Paths - Using relative paths for cross-platform compatibility
_BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMP_AUDIO_DIR = os.path.join(_BASE_DIR, "src", "audio_recording", "test", "temp_audio")
TEMP_INPUT_FILE = "temp_input.wav"
TEMP_OUTPUT_FILE = "temp_output.wav"

# Exit Commands
EXIT_COMMANDS = ["exit", "quit", "stop", "goodbye", "bye"]

# OpenRouter AI Settings
OPENROUTER_API_KEY = "OPEN-AI-KEY-HERE"  
OPENROUTER_MODEL = "openai/gpt-4"  # GPT-4 model via OpenRouter
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

# AI Personality & Behavior
AI_SYSTEM_PROMPT = """You are a casual, friendly AI companion. Respond in a conversational, 
relaxed way like you're chatting with a good friend. Keep responses concise but engaging, 
and feel free to use casual language and expressions. Keep your responses relatively short 
since they will be spoken aloud."""

CONVERSATION_MEMORY_LENGTH = 5  # Remember last 5 message exchanges

# Audio Buffering Settings
BUFFER_AUDIO_BEFORE_PLAYBACK = True  # Wait for complete audio generation before playback
AUDIO_QUALITY_CHECK = True  # Verify audio file integrity before playback
TTS_GENERATION_TIMEOUT = 30  # Maximum time to wait for TTS generation (seconds)
AUDIO_MIN_FILE_SIZE = 1024  # Minimum expected file size in bytes
AUDIO_VALIDATION_DELAY = 0.5  # Seconds to wait after generation for file stabilization

# Application Settings
SHOW_TRANSCRIPTION = True  # Display what was transcribed
SHOW_AI_RESPONSE = True  # Display AI response text
CLEANUP_ON_EXIT = True  # Remove temporary files on exit
VERBOSE_MODE = False  # Show detailed processing information

# AI Audio Saving Settings
SAVE_AI_AUDIO = True  # Save all AI-generated audio to files
AI_AUDIO_DIR = os.path.join(_BASE_DIR, "ai-generated-audio")  # Directory to save AI audio
AI_AUDIO_FILENAME_FORMAT = "ai_audio_{timestamp}_{counter:03d}.wav"  # Filename format
MAX_SAVED_AUDIO_FILES = 100  # Maximum number of audio files to keep (0 = unlimited)
