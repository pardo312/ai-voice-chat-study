"""
Voice Chat Application
Main application that creates a voice chat loop with AI
"""

import os
import sys
import signal
import time
import threading
from pathlib import Path

# Import our modules
from src.audio_recording.audio_recorder import AudioRecorder
from src.speech_processor import SpeechProcessor
from src.config import *

class VoiceChatApp:
    def __init__(self):
        self.recorder = None
        self.processor = None
        self.running = False
        self.processing_lock = threading.Lock()
        self.current_cycle = 0
        
        # Set up signal handler for graceful exit
        signal.signal(signal.SIGINT, self._signal_handler)
        
    def _signal_handler(self, signum, frame):
        """Handle Ctrl+C gracefully"""
        print("\n\n🛑 Interrupt received, shutting down...")
        self.running = False
        self.cleanup()
        sys.exit(0)
    
    def initialize(self):
        """Initialize all components"""
        print("🎙️  Voice Chat Application")
        print("=" * 50)
        print("This app will listen to your voice and respond with AI-generated responses.")
        print("The AI will remember your last 5 exchanges for context.")
        print("Press Ctrl+C to exit, or say 'exit', 'quit', or 'stop'")
        print("=" * 50)
        
        # Create temp directory
        Path(TEMP_AUDIO_DIR).mkdir(exist_ok=True)
        
        # Initialize audio recorder
        print("\n🎤 Initializing audio recorder...")
        try:
            self.recorder = AudioRecorder()
            if not self.recorder.initialize():
                print("❌ Failed to initialize audio recorder")
                print("💡 Make sure your microphone is connected and accessible")
                return False
            print("✅ Audio recorder initialized")
        except Exception as e:
            print(f"❌ Failed to initialize audio recorder: {e}")
            print("💡 Make sure your microphone is connected and accessible")
            return False
        
        # Initialize speech processor
        print("\n🧠 Initializing speech processor...")
        try:
            self.processor = SpeechProcessor()
            if not self.processor.initialize_models():
                return False
        except Exception as e:
            print(f"❌ Failed to initialize speech processor: {e}")
            return False
        
        print("\n✅ All components initialized successfully!")
        return True
    
    def show_status(self):
        """Show current configuration status"""
        print("\n📊 Current Configuration:")
        print(f"   🎤 Audio: {SAMPLE_RATE}Hz, {CHANNELS} channel(s)")
        print(f"   🧠 Whisper: {WHISPER_MODEL_SIZE} model on {WHISPER_DEVICE}")
        print(f"   🎵 XTTS: {XTTS_MODEL}")
        print(f"   🗣️  Language: {XTTS_LANGUAGE}")
        
        if XTTS_VOICE_SAMPLE:
            print(f"   🎭 Voice cloning: {XTTS_VOICE_SAMPLE}")
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
        if OPENROUTER_API_KEY != "your-api-key-here" and OPENROUTER_API_KEY:
            print(f"   🤖 AI Model: {OPENROUTER_MODEL}")
            print(f"   💭 Memory: {CONVERSATION_MEMORY_LENGTH} exchanges")
            print("   🔗 OpenRouter: Connected")
        else:
            print("   🤖 AI Model: Not configured (will echo)")
            print("   💡 Set OPENROUTER_API_KEY in src/config.py")
        
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
    
    def run_chat_loop(self):
        """Main chat loop"""
        self.running = True
        cycle_count = 0
        
        self.show_status()
        
        print("🚀 Starting voice chat loop...")
        print("💡 Tip: Speak clearly and wait for the beep before speaking")
        print("-" * 50)
        
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
                    
                    # Step 1: Record audio
                    audio_file = self.recorder.record_and_save(use_vad=True)
                    
                    if not audio_file:
                        print("⚠️  No audio recorded, trying again...")
                        continue
                    
                    # Step 2: Process the speech (transcribe -> synthesize -> play)
                    result = self.processor.process_speech_cycle(audio_file)
                    
                    if result == "exit":
                        print("👋 Exit command detected, goodbye!")
                        break
                    elif result:
                        print("✅ Cycle completed successfully")
                    else:
                        print("⚠️  Cycle failed, trying again...")
                
                # Small delay between cycles (outside the lock)
                time.sleep(0.5)
                
            except KeyboardInterrupt:
                print("\n🛑 Interrupted by user")
                break
            except Exception as e:
                print(f"❌ Error in chat loop: {e}")
                print("🔄 Continuing...")
                continue
        
        print(f"\n📊 Total cycles completed: {cycle_count}")
    
    def cleanup(self):
        """Clean up all resources"""
        print("\n🧹 Cleaning up...")
        
        if self.recorder:
            self.recorder.cleanup()
        
        if self.processor:
            self.processor.cleanup()
        
        print("✅ Cleanup completed")
    
    def run(self):
        """Main application entry point"""
        try:
            # Initialize components
            if not self.initialize():
                print("❌ Initialization failed, exiting...")
                return False
            
            # Run the main chat loop
            self.run_chat_loop()
            
            return True
            
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            return False
        finally:
            self.cleanup()

def check_dependencies():
    """Check if required dependencies are available"""
    print("🔍 Checking dependencies...")
    
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
        print("💡 Make sure FastWhisper environment is activated")
        missing_deps.append("faster-whisper")
    
    # Check TTS
    try:
        from TTS.api import TTS
        print("✅ TTS available")
    except ImportError:
        print("❌ TTS not available")
        print("💡 Make sure XTTS environment is activated")
        missing_deps.append("TTS")
    
    if missing_deps:
        print(f"\n❌ Missing dependencies: {', '.join(missing_deps)}")
        print("💡 Install missing dependencies with:")
        print("   pip install " + " ".join(missing_deps))
        return False
    
    print("✅ All dependencies available")
    return True

def main():
    """Main function"""
    print("🎙️  Voice Chat with AI")
    print("=" * 30)
    
    # Check dependencies first
    if not check_dependencies():
        print("\n❌ Dependency check failed")
        return
    
    # Create and run the application 
    app = VoiceChatApp()
    
    try:
        success = app.run()
        if success:
            print("\n👋 Voice chat session ended successfully")
        else:
            print("\n❌ Voice chat session ended with errors")
    except KeyboardInterrupt:
        print("\n\n🛑 Application interrupted by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
    finally:
        print("🏁 Application finished")

if __name__ == "__main__":
    main()
