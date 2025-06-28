"""
Speech Processing Module for Voice Chat Application
Handles speech-to-text and text-to-speech operations
"""

import os
import sys
import warnings
import pygame
import time
import shutil
from datetime import datetime
from pathlib import Path

# Add parent directories to path to access existing models
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'FastWhisper'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'XTTS'))

try:
    # Try relative imports first (when used as a module)
    from .config import *
    from .ai_chat import AIChat
except ImportError:
    # Fall back to absolute imports (when run as a script)
    import sys
    import os
    sys.path.append(os.path.dirname(__file__))
    from config import *
    from ai_chat import AIChat

# Suppress warnings for cleaner output
warnings.filterwarnings("ignore")

class SpeechProcessor:
    def __init__(self):
        self.whisper_model = None
        self.tts_model = None
        self.pygame_initialized = False
        self.ai_chat = None
        
        # Initialize pygame mixer for audio playback
        self._init_pygame()
        
        # Initialize AI chat
        self._init_ai_chat()
        
    def _init_pygame(self):
        """Initialize pygame mixer for audio playback with enhanced buffering"""
        try:
            # Use larger buffer size for smoother playback when buffering is enabled
            buffer_size = 4096 if BUFFER_AUDIO_BEFORE_PLAYBACK else 1024
            
            pygame.mixer.pre_init(
                frequency=SAMPLE_RATE, 
                size=-16, 
                channels=CHANNELS, 
                buffer=buffer_size
            )
            pygame.mixer.init()
            
            self.pygame_initialized = True
            if VERBOSE_MODE:
                print(f"✅ Pygame mixer initialized (buffer: {buffer_size})")
        except Exception as e:
            print(f"⚠️  Warning: Could not initialize pygame mixer: {e}")
            self.pygame_initialized = False
    
    def _init_ai_chat(self):
        """Initialize AI chat component"""
        try:
            self.ai_chat = AIChat()
            if VERBOSE_MODE:
                print("✅ AI chat initialized")
        except Exception as e:
            print(f"⚠️  Warning: Could not initialize AI chat: {e}")
            self.ai_chat = None
    
    def load_whisper_model(self):
        """Load the FastWhisper model"""
        try:
            if VERBOSE_MODE:
                print(f"🔄 Loading Whisper model ({WHISPER_MODEL_SIZE})...")
            
            from faster_whisper import WhisperModel
            
            # Load model with specified configuration
            self.whisper_model = WhisperModel(
                WHISPER_MODEL_SIZE, 
                device=WHISPER_DEVICE, 
                compute_type=WHISPER_COMPUTE_TYPE
            )
            
            if VERBOSE_MODE:
                print("✅ Whisper model loaded successfully")
            return True
            
        except Exception as e:
            print(f"❌ Failed to load Whisper model: {e}")
            print("💡 Tip: Make sure FastWhisper environment is set up correctly")
            return False
    
    def load_tts_model(self):
        """Load the XTTS model"""
        try:
            if VERBOSE_MODE:
                print("🔄 Loading XTTS model...")
            
            from TTS.api import TTS
            
            # Load XTTS model
            self.tts_model = TTS(XTTS_MODEL)
            
            if VERBOSE_MODE:
                print("✅ XTTS model loaded successfully")
            return True
            
        except Exception as e:
            print(f"❌ Failed to load XTTS model: {e}")
            print("💡 Tip: Make sure XTTS environment is set up correctly")
            return False
    
    def initialize_models(self):
        """Initialize both speech models"""
        print("🚀 Initializing speech models...")
        
        whisper_success = self.load_whisper_model()
        tts_success = self.load_tts_model()
        
        if whisper_success and tts_success:
            print("✅ All models loaded successfully!")
            return True
        else:
            print("❌ Failed to load one or more models")
            return False
    
    def transcribe_audio(self, audio_file):
        """Transcribe audio file to text using FastWhisper"""
        if not self.whisper_model:
            print("❌ Whisper model not loaded")
            return None
        
        try:
            if VERBOSE_MODE:
                print("🔄 Transcribing audio...")
            
            # Transcribe the audio file
            segments, info = self.whisper_model.transcribe(audio_file, beam_size=5)
            
            # Extract text from segments
            transcribed_text = ""
            for segment in segments:
                transcribed_text += segment.text + " "
            
            transcribed_text = transcribed_text.strip()
            
            if VERBOSE_MODE:
                print(f"🎯 Detected language: {info.language} (confidence: {info.language_probability:.2f})")
            
            return transcribed_text if transcribed_text else None
            
        except Exception as e:
            print(f"❌ Transcription error: {e}")
            return None
    
    def synthesize_speech(self, text):
        """Convert text to speech using XTTS with buffering support"""
        if not self.tts_model:
            print("❌ TTS model not loaded")
            return None
        
        if not text or text.strip() == "":
            print("⚠️  No text to synthesize")
            return None
        
        try:
            if VERBOSE_MODE:
                print("🔄 Synthesizing speech...")
            
            output_file = os.path.join(TEMP_AUDIO_DIR, TEMP_OUTPUT_FILE)
            
            # Remove existing output file to ensure clean generation
            if os.path.exists(output_file):
                try:
                    os.remove(output_file)
                except Exception as e:
                    print(f"⚠️  Warning: Could not remove existing output file: {e}")
            
            # Split text into sentences for better TTS processing
            sentences = self._split_text_to_sentences(text)
            print(f" > Text splitted to sentences.")
            print(sentences)
            
            start_time = time.time()
            
            # Generate speech
            if XTTS_VOICE_SAMPLE and os.path.exists(XTTS_VOICE_SAMPLE):
                # Use voice cloning if sample is available
                print("🦜 Using cloned voice...")
                self.tts_model.tts_to_file(
                    text=text,
                    speaker_wav=XTTS_VOICE_SAMPLE,
                    language=XTTS_LANGUAGE,
                    file_path=output_file
                )
            else:
                print("⚠️ Using default voice...")
                # Use default voice
                self.tts_model.tts_to_file(
                    text=text,
                    file_path=output_file
                )
            
            processing_time = time.time() - start_time
            
            # Calculate real-time factor
            if os.path.exists(output_file):
                import wave
                with wave.open(output_file, 'rb') as wf:
                    audio_duration = wf.getnframes() / wf.getframerate()
                    real_time_factor = processing_time / audio_duration if audio_duration > 0 else 0
                    print(f" > Processing time: {processing_time}")
                    print(f" > Real-time factor: {real_time_factor}")
            
            # Wait for file stabilization if buffering is enabled
            if BUFFER_AUDIO_BEFORE_PLAYBACK:
                if VERBOSE_MODE:
                    print("⏳ Waiting for audio file stabilization...")
                time.sleep(AUDIO_VALIDATION_DELAY)
            
            # Validate the generated audio file
            if self._validate_audio_file(output_file):
                if VERBOSE_MODE:
                    print("✅ Speech synthesis completed and validated")
                
                # Save AI-generated audio to permanent storage
                self._save_ai_audio(output_file)
                
                return output_file
            else:
                print("❌ Speech synthesis failed - invalid output file")
                return None
                
        except Exception as e:
            print(f"❌ Speech synthesis error: {e}")
            return None
    
    def _split_text_to_sentences(self, text):
        """Split text into sentences for better TTS processing"""
        import re
        # Simple sentence splitting - can be improved with more sophisticated NLP
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        return sentences
    
    def _validate_audio_file(self, audio_file):
        """Validate that the audio file was generated correctly"""
        if not AUDIO_QUALITY_CHECK:
            return os.path.exists(audio_file)
        
        try:
            if not os.path.exists(audio_file):
                if VERBOSE_MODE:
                    print("❌ Audio file does not exist")
                return False
            
            # Check file size
            file_size = os.path.getsize(audio_file)
            if file_size < AUDIO_MIN_FILE_SIZE:
                if VERBOSE_MODE:
                    print(f"❌ Audio file too small: {file_size} bytes")
                return False
            
            # Additional validation: try to load the file with pygame
            try:
                pygame.mixer.music.load(audio_file)
                if VERBOSE_MODE:
                    print(f"✅ Audio file validated: {file_size} bytes")
                return True
            except pygame.error as e:
                if VERBOSE_MODE:
                    print(f"❌ Audio file corrupted: {e}")
                return False
                
        except Exception as e:
            if VERBOSE_MODE:
                print(f"❌ Audio validation error: {e}")
            return False
    
    def _save_ai_audio(self, audio_file):
        """Save AI-generated audio to permanent storage"""
        if not SAVE_AI_AUDIO or not audio_file or not os.path.exists(audio_file):
            return None
        
        try:
            # Create AI audio directory if it doesn't exist
            Path(AI_AUDIO_DIR).mkdir(parents=True, exist_ok=True)
            
            # Generate unique filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Find next available counter for this timestamp
            counter = 1
            while True:
                filename = AI_AUDIO_FILENAME_FORMAT.format(
                    timestamp=timestamp,
                    counter=counter
                )
                saved_path = os.path.join(AI_AUDIO_DIR, filename)
                
                if not os.path.exists(saved_path):
                    break
                counter += 1
            
            # Copy the audio file to permanent storage
            shutil.copy2(audio_file, saved_path)
            
            if VERBOSE_MODE:
                print(f"💾 AI audio saved: {filename}")
            
            # Clean up old files if limit is set
            self._cleanup_old_audio_files()
            
            return saved_path
            
        except Exception as e:
            print(f"⚠️  Warning: Could not save AI audio: {e}")
            return None
    
    def _cleanup_old_audio_files(self):
        """Remove old audio files if MAX_SAVED_AUDIO_FILES limit is exceeded"""
        if MAX_SAVED_AUDIO_FILES <= 0:
            return  # No limit set
        
        try:
            # Get all audio files in the directory
            audio_files = []
            for file in os.listdir(AI_AUDIO_DIR):
                if file.endswith('.wav') and file.startswith('ai_audio_'):
                    file_path = os.path.join(AI_AUDIO_DIR, file)
                    audio_files.append((file_path, os.path.getctime(file_path)))
            
            # Sort by creation time (oldest first)
            audio_files.sort(key=lambda x: x[1])
            
            # Remove oldest files if we exceed the limit
            while len(audio_files) > MAX_SAVED_AUDIO_FILES:
                oldest_file = audio_files.pop(0)[0]
                try:
                    os.remove(oldest_file)
                    if VERBOSE_MODE:
                        print(f"🧹 Removed old audio file: {os.path.basename(oldest_file)}")
                except Exception as e:
                    if VERBOSE_MODE:
                        print(f"⚠️  Could not remove old audio file: {e}")
                    
        except Exception as e:
            if VERBOSE_MODE:
                print(f"⚠️  Warning: Could not cleanup old audio files: {e}")
    
    def play_audio(self, audio_file):
        """Play audio file using pygame with enhanced buffering"""
        if not audio_file or not os.path.exists(audio_file):
            print("❌ Audio file not found")
            return False
        
        try:
            if not self.pygame_initialized:
                print("❌ Pygame mixer not initialized")
                return False
            
            # Additional validation before playback if buffering is enabled
            if BUFFER_AUDIO_BEFORE_PLAYBACK:
                if not self._validate_audio_file(audio_file):
                    print("❌ Audio file validation failed")
                    return False
            
            if VERBOSE_MODE:
                print("🔊 Playing audio...")
            
            # Stop any currently playing audio
            if pygame.mixer.music.get_busy():
                pygame.mixer.music.stop()
            
            # Load and play the audio file
            pygame.mixer.music.load(audio_file)
            pygame.mixer.music.play()
            
            # Wait for playback to complete with better error handling
            playback_timeout = time.time() + TTS_GENERATION_TIMEOUT
            while pygame.mixer.music.get_busy():
                if time.time() > playback_timeout:
                    print("⚠️  Audio playback timeout, stopping...")
                    pygame.mixer.music.stop()
                    return False
                time.sleep(0.1)
            
            if VERBOSE_MODE:
                print("✅ Audio playback completed")
            return True
            
        except Exception as e:
            print(f"❌ Audio playback error: {e}")
            return False
    
    def process_speech_cycle(self, audio_file):
        """Complete speech processing cycle: transcribe -> get AI response -> synthesize -> play"""
        # Step 1: Transcribe audio to text
        print("📝 Transcribing...")
        transcribed_text = self.transcribe_audio(audio_file)
        
        if not transcribed_text:
            print("⚠️  No speech detected or transcription failed")
            return False
        
        # Show transcription if enabled
        if SHOW_TRANSCRIPTION:
            print(f"💬 You said: \"{transcribed_text}\"")
        
        # Check for exit commands
        if any(exit_cmd in transcribed_text.lower() for exit_cmd in EXIT_COMMANDS):
            print("👋 Exit command detected")
            return "exit"
        
        # Step 2: Get AI response
        print("🤖 Getting AI response...")
        if self.ai_chat:
            ai_response = self.ai_chat.get_response(transcribed_text)
        else:
            # Fallback to echo mode if AI chat is not available
            print("⚠️  AI chat not available, falling back to echo mode")
            ai_response = transcribed_text
        
        # Show AI response if enabled
        if SHOW_AI_RESPONSE and ai_response != transcribed_text:
            print(f"🤖 AI responds: \"{ai_response}\"")
        
        # Step 3: Synthesize AI response to speech
        print("🎵 Generating speech...")
        output_audio = self.synthesize_speech(ai_response)
        
        if not output_audio:
            print("❌ Speech synthesis failed")
            return False
        
        # Step 4: Play the generated audio
        print("🔊 Playing back...")
        playback_success = self.play_audio(output_audio)
        
        if playback_success:
            print("✅ Speech cycle completed")
            return True
        else:
            print("❌ Audio playback failed")
            return False
    
    def cleanup(self):
        """Clean up resources"""
        try:
            if self.pygame_initialized:
                pygame.mixer.quit()
        except:
            pass
        
        # Clean up temporary files if enabled
        if CLEANUP_ON_EXIT:
            self._cleanup_temp_files()
    
    def _cleanup_temp_files(self):
        """Remove temporary audio files"""
        temp_files = [
            os.path.join(TEMP_AUDIO_DIR, TEMP_INPUT_FILE),
            os.path.join(TEMP_AUDIO_DIR, TEMP_OUTPUT_FILE)
        ]
        
        for file in temp_files:
            try:
                if os.path.exists(file):
                    os.remove(file)
                    if VERBOSE_MODE:
                        print(f"🧹 Cleaned up: {file}")
            except:
                pass
    
    def __del__(self):
        """Destructor to ensure cleanup"""
        self.cleanup()
