#!/usr/bin/env python3
"""
Test script for audio buffering improvements
Tests the new buffering system to ensure smooth audio playback
"""

import os
import sys
import time
from pathlib import Path

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from speech_processor import SpeechProcessor
from config import *

def test_audio_buffering():
    """Test the audio buffering system"""
    print("🧪 Testing Audio Buffering System")
    print("=" * 40)
    
    # Create temp directory if it doesn't exist
    Path(TEMP_AUDIO_DIR).mkdir(parents=True, exist_ok=True)
    
    # Initialize speech processor
    print("\n🔄 Initializing speech processor...")
    processor = SpeechProcessor()
    
    # Load only TTS model for this test
    print("🔄 Loading TTS model...")
    if not processor.load_tts_model():
        print("❌ Failed to load TTS model")
        return False
    
    # Test phrases
    test_phrases = [
        "Hello, this is a test of the audio buffering system.",
        "The new buffering should make audio playback much smoother.",
        "No more choppy audio during text-to-speech generation!"
    ]
    
    print(f"\n🎵 Testing {len(test_phrases)} phrases with buffering...")
    print(f"📊 Buffering enabled: {BUFFER_AUDIO_BEFORE_PLAYBACK}")
    print(f"📊 Quality check enabled: {AUDIO_QUALITY_CHECK}")
    print(f"📊 Validation delay: {AUDIO_VALIDATION_DELAY}s")
    
    success_count = 0
    
    for i, phrase in enumerate(test_phrases, 1):
        print(f"\n🔄 Test {i}/{len(test_phrases)}: \"{phrase[:30]}...\"")
        
        start_time = time.time()
        
        # Generate speech
        audio_file = processor.synthesize_speech(phrase)
        
        if audio_file:
            # Play audio
            if processor.play_audio(audio_file):
                end_time = time.time()
                duration = end_time - start_time
                print(f"✅ Test {i} completed in {duration:.2f}s")
                success_count += 1
            else:
                print(f"❌ Test {i} failed during playback")
        else:
            print(f"❌ Test {i} failed during synthesis")
        
        # Small delay between tests
        time.sleep(1)
    
    # Results
    print(f"\n📊 Test Results:")
    print(f"   ✅ Successful: {success_count}/{len(test_phrases)}")
    print(f"   ❌ Failed: {len(test_phrases) - success_count}/{len(test_phrases)}")
    
    if success_count == len(test_phrases):
        print("🎉 All tests passed! Audio buffering is working correctly.")
    else:
        print("⚠️  Some tests failed. Check the configuration.")
    
    # Cleanup
    processor.cleanup()
    
    return success_count == len(test_phrases)

def test_configuration():
    """Test and display current configuration"""
    print("\n📊 Current Audio Buffering Configuration:")
    print(f"   🔄 Buffer audio before playback: {BUFFER_AUDIO_BEFORE_PLAYBACK}")
    print(f"   ✅ Audio quality check: {AUDIO_QUALITY_CHECK}")
    print(f"   ⏱️  TTS generation timeout: {TTS_GENERATION_TIMEOUT}s")
    print(f"   📏 Minimum file size: {AUDIO_MIN_FILE_SIZE} bytes")
    print(f"   ⏳ Validation delay: {AUDIO_VALIDATION_DELAY}s")
    print(f"   🎤 Sample rate: {SAMPLE_RATE}Hz")
    print(f"   📁 Temp directory: {TEMP_AUDIO_DIR}")

def main():
    """Main test function"""
    print("🧪 Audio Buffering Test Suite")
    print("=" * 50)
    
    try:
        # Show configuration
        test_configuration()
        
        # Run buffering test
        if test_audio_buffering():
            print("\n🎉 Audio buffering system is working correctly!")
            print("💡 Your voice chat should now have smoother audio playback.")
        else:
            print("\n❌ Audio buffering test failed.")
            print("💡 Check your TTS model configuration and try again.")
            
    except KeyboardInterrupt:
        print("\n🛑 Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("\n🏁 Test completed")

if __name__ == "__main__":
    main()
