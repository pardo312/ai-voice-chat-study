"""
Voice Chat Application
Main application that creates a voice chat loop with AI
"""

import os
import sys
import signal
import time
import threading
import logging
from pathlib import Path
from typing import Optional

from ..config import (
    TEMP_AUDIO_DIR, OPENROUTER_API_KEY, OPENROUTER_MODEL,
    SAMPLE_RATE, CHANNELS, WHISPER_MODEL_SIZE, WHISPER_DEVICE,
    XTTS_MODEL, XTTS_LANGUAGE, XTTS_VOICE_SAMPLE,
    BUFFER_AUDIO_BEFORE_PLAYBACK, AUDIO_QUALITY_CHECK,
    CONVERSATION_MEMORY_LENGTH, SHOW_TRANSCRIPTION, SHOW_AI_RESPONSE,
    SAVE_AI_AUDIO, AI_AUDIO_DIR, MAX_SAVED_AUDIO_FILES, VERBOSE_MODE
)
from ..audio import AudioRecorder
from .speech_processor import SpeechProcessor

logger = logging.getLogger(__name__)


class VoiceChatApp:
    """Main Voice Chat Application"""
    
    def __init__(self):
        self.recorder: Optional[AudioRecorder] = None
        self.processor: Optional[SpeechProcessor] = None
        self.running = False
        self.processing_lock = threading.Lock()
        self.current_cycle = 0
        
        # Set up signal handler for graceful exit
        signal.signal(signal.SIGINT, self._signal_handler)
        
        if VERBOSE_MODE:
            logger.info("VoiceChatApp initialized")
        
    def _signal_handler(self, signum, frame):
        """Handle Ctrl+C gracefully"""
        print("\n\n🛑 Interrupt received, shutting down...")
        logger.info("Interrupt signal received")
        self.running = False
        self.cleanup()
        sys.exit(0)
    
    def initialize(self) -> bool:
        """Initialize all components"""
        print("🎙️  Voice Chat Application")
        print("=" * 50)
        print("This app will listen to your voice and respond with AI-generated responses.")
        print("The AI will remember your last 5 exchanges for context.")
        print("Press Ctrl+C to exit, or say 'exit', 'quit', or 'stop'")
        print("=" * 50)
        
        logger.info("Initializing Voice Chat Application")
        
        # Create temp directory
        Path(TEMP_AUDIO_DIR).mkdir(parents=True, exist_ok=True)
        
        # Initialize audio recorder
        print("\n🎤 Initializing audio recorder...")
        try:
            self.recorder = AudioRecorder()
            if not self.recorder.initialize():
                print("❌ Failed to initialize audio recorder")
                print("💡 Make sure your microphone is connected and accessible")
                logger.error("Failed to initialize audio recorder")
                return False
            print("✅ Audio recorder initialized")
            logger.info("Audio recorder initialized successfully")
        except Exception as e:
            error_msg = f"Failed to initialize audio recorder: {e}"
            logger.error(error_msg)
            print(f"❌ {error_msg}")
            print("💡 Make sure your microphone is connected and accessible")
            return False
        
        # Initialize speech processor
        print("\n🧠 Initializing speech processor...")
        try:
            self.processor = SpeechProcessor()
            if not self.processor.initialize_models():
                logger.error("Failed to initialize speech processor")
                return False
            logger.info("Speech processor initialized successfully")
        except Exception as e:
            error_msg = f"Failed to initialize speech processor: {e}"
            logger.error(error_msg)
            print(f"❌ {error_msg}")
            return False
        
        print("\n✅ All components initialized successfully!")
        logger.info("All components initialized successfully")
        return True
    
    def show_status(self) -> None:
        """Show current configuration status"""
        print("\n📊 Current Configuration:")
        print(f"   🎤 Audio: {SAMPLE_RATE}Hz, {CHANNELS} channel(s)")
        print(f"   🧠 Whisper: {WHISPER_MODEL_SIZE} model on {WHISPER_DEVICE}")
        print(f"   🎵 XTTS: {XTTS_MODEL}")
        print(f"   🗣️  Language: {XTTS_LANGUAGE}")
        
        if XTTS_VOICE_SAMPLE and os.path.exists(XTTS_VOICE_SAMPLE):
            print(f"   🎭 Voice cloning: {os.path.basename(XTTS_VOICE_SAMPLE)}")
        else:
            print("   🎭 Voice cloning: Default voice")
        
        # Audio Buffering Configuration
        if BUFFER_AUDIO_BEFORE_PLAYBACK:
            print("   🔄 Audio buffering: Enabled (smoother playback)")
            if AUDIO_QUALITY_CHECK:
                print("   ✅ Audio validation: Enabled")
        else:
            print("   🔄 Audio buffering: Disabled (real-time)")
        
        # AI Configuration
        if OPENROUTER_API_KEY and OPENROUTER_API_KEY != "your-api-key-here":
            print(f"   🤖 AI Model: {OPENROUTER_MODEL}")
            print(f"   💭 Memory: {CONVERSATION_MEMORY_LENGTH} exchanges")
            print("   🔗 OpenRouter: Connected")
        else:
            print("   🤖 AI Model: Not configured (will echo)")
            print("   💡 Set OPENROUTER_API_KEY in your .env file")
        
        print(f"   📝 Show transcription: {SHOW_TRANSCRIPTION}")
        print(f"   🤖 Show AI response: {SHOW_AI_RESPONSE}")
        print(f"   🔊 Voice activity detection: Enabled")
        
        # Audio Saving Configuration
        if SAVE_AI_AUDIO:
            print(f"   💾 AI audio saving: Enabled")
            print(f"   📁 Save directory: {AI_AUDIO_DIR}")
            if MAX_SAVED_AUDIO_FILES > 0:
                print(f"   📊 Max saved files: {MAX_SAVED_AUDIO_FILES}")
            else:
                print("   📊 Max saved files: Unlimited")
        else:
            print("   💾 AI audio saving: Disabled")
        
        print()
    
    def run_chat_loop(self) -> None:
        """Main chat loop"""
        self.running = True
        cycle_count = 0
        
        self.show_status()
        
        print("🚀 Starting voice chat loop...")
        print("💡 Tip: Speak clearly and wait for the beep before speaking")
        print("-" * 50)
        
        logger.info("Starting voice chat loop")
        
        while self.running:
            try:
                # Use processing lock to prevent duplicate cycles
                with self.processing_lock:
                    if not self.running:
                        break
                        
                    cycle_count += 1
                    self.current_cycle = cycle_count
                    print(f"\n🔄 Cycle {cycle_count}")
                    print("-" * 20)
                    
                    logger.info(f"Starting cycle {cycle_count}")
                    
                    # Step 1: Record audio
                    audio_file = self.recorder.record_and_save(use_vad=True)
                    
                    if not audio_file:
                        print("⚠️  No audio recorded, trying again...")
                        logger.warning("No audio recorded in cycle")
                        continue
                    
                    # Step 2: Process the speech (transcribe -> synthesize -> play)
                    result = self.processor.process_speech_cycle(audio_file)
                    
                    if result == "exit":
                        print("👋 Exit command detected, goodbye!")
                        logger.info("Exit command detected")
                        break
                    elif result:
                        print("✅ Cycle completed successfully")
                        logger.info(f"Cycle {cycle_count} completed successfully")
                    else:
                        print("⚠️  Cycle failed, trying again...")
                        logger.warning(f"Cycle {cycle_count} failed")
                
                # Small delay between cycles (outside the lock)
                time.sleep(0.5)
                
            except KeyboardInterrupt:
                print("\n🛑 Interrupted by user")
                logger.info("Interrupted by user")
                break
            except Exception as e:
                error_msg = f"Error in chat loop: {e}"
                logger.error(error_msg)
                print(f"❌ {error_msg}")
                print("🔄 Continuing...")
                continue
        
        print(f"\n📊 Total cycles completed: {cycle_count}")
        logger.info(f"Voice chat loop ended. Total cycles: {cycle_count}")
    
    def cleanup(self) -> None:
        """Clean up all resources"""
        print("\n🧹 Cleaning up...")
        logger.info("Starting cleanup")
        
        if self.recorder:
            try:
                self.recorder.cleanup()
                logger.info("Audio recorder cleaned up")
            except Exception as e:
                logger.warning(f"Error cleaning up recorder: {e}")
        
        if self.processor:
            try:
                self.processor.cleanup()
                logger.info("Speech processor cleaned up")
            except Exception as e:
                logger.warning(f"Error cleaning up processor: {e}")
        
        print("✅ Cleanup completed")
        logger.info("Cleanup completed")
    
    def run(self) -> bool:
        """Main application entry point"""
        try:
            # Initialize components
            if not self.initialize():
                print("❌ Initialization failed, exiting...")
                logger.error("Initialization failed")
                return False
            
            # Run the main chat loop
            self.run_chat_loop()
            
            return True
            
        except Exception as e:
            error_msg = f"Unexpected error: {e}"
            logger.error(error_msg)
            print(f"❌ {error_msg}")
            return False
        finally:
            self.cleanup()


def check_dependencies() -> bool:
    """Check if required dependencies are available"""
    print("🔍 Checking dependencies...")
    logger.info("Checking dependencies")
    
    missing_deps = []
    
    # Check PyAudio
    try:
        import pyaudio
        print("✅ PyAudio available")
    except ImportError:
        missing_deps.append("pyaudio")
    
    # Check pygame
    try:
        import pygame
        print("✅ Pygame available")
    except ImportError:
        missing_deps.append("pygame")
    
    # Check numpy
    try:
        import numpy
        print("✅ NumPy available")
    except ImportError:
        missing_deps.append("numpy")
    
    # Check faster-whisper
    try:
        from faster_whisper import WhisperModel
        print("✅ faster-whisper available")
    except ImportError:
        print("❌ faster-whisper not available")
        print("💡 Install with: pip install faster-whisper")
        missing_deps.append("faster-whisper")
    
    # Check TTS
    try:
        from TTS.api import TTS
        print("✅ TTS available")
    except ImportError:
        print("❌ TTS not available")
        print("💡 Install with: pip install TTS")
        missing_deps.append("TTS")
    
    # Check python-dotenv
    try:
        import dotenv
        print("✅ python-dotenv available")
    except ImportError:
        print("❌ python-dotenv not available")
        print("💡 Install with: pip install python-dotenv")
        missing_deps.append("python-dotenv")
    
    if missing_deps:
        print(f"\n❌ Missing dependencies: {', '.join(missing_deps)}")
        print("💡 Install missing dependencies with:")
        print("   pip install " + " ".join(missing_deps))
        logger.error(f"Missing dependencies: {missing_deps}")
        return False
    
    print("✅ All dependencies available")
    logger.info("All dependencies available")
    return True


def setup_logging() -> None:
    """Setup logging configuration"""
    log_level = logging.DEBUG if VERBOSE_MODE else logging.INFO
    
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('voice_chat.log'),
            logging.StreamHandler() if VERBOSE_MODE else logging.NullHandler()
        ]
    )


def main():
    """Main function"""
    # Setup logging
    setup_logging()
    
    print("🎙️  Voice Chat with AI")
    print("=" * 30)
    
    logger.info("Voice Chat Application starting")
    
    # Check dependencies first
    if not check_dependencies():
        print("\n❌ Dependency check failed")
        logger.error("Dependency check failed")
        return
    
    # Create and run the application 
    app = VoiceChatApp()
    
    try:
        success = app.run()
        if success:
            print("\n👋 Voice chat session ended successfully")
            logger.info("Voice chat session ended successfully")
        else:
            print("\n❌ Voice chat session ended with errors")
            logger.error("Voice chat session ended with errors")
    except KeyboardInterrupt:
        print("\n\n🛑 Application interrupted by user")
        logger.info("Application interrupted by user")
    except Exception as e:
        error_msg = f"Unexpected error: {e}"
        logger.error(error_msg)
        print(f"\n❌ {error_msg}")
    finally:
        print("🏁 Application finished")
        logger.info("Application finished")


if __name__ == "__main__":
    main()
