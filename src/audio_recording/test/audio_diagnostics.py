#!/usr/bin/env python3
"""
Audio Diagnostics Tool for Voice Chat Application
Tests audio devices and provides troubleshooting information
"""

import sys
import time
import os

# Add the project root to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, project_root)

# Add the src directory to the Python path
src_dir = os.path.join(project_root, 'src')
sys.path.insert(0, src_dir)

try:
    # Try absolute imports first (when run as a script)
    from src.audio_recording.audio_manager import AudioManager
    from src.config import *
except ImportError:
    try:
        # Try relative imports (when used as a module)
        from ..audio_manager import AudioManager
        from ...config import *
    except ImportError:
        # Try direct imports from current directory structure
        sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
        sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
        from audio_manager import AudioManager
        import config
        # Import all config variables
        for attr in dir(config):
            if not attr.startswith('_'):
                globals()[attr] = getattr(config, attr)

def run_audio_diagnostics():
    """Run comprehensive audio diagnostics"""
    print("🔧 Audio Diagnostics Tool")
    print("=" * 50)
    
    # Initialize AudioManager
    audio_manager = AudioManager()
    
    print("\n1️⃣  Initializing audio system...")
    if not audio_manager.initialize():
        print("❌ Audio system initialization failed")
        print("\n🔧 Troubleshooting steps:")
        print("1. Check if microphone is connected")
        print("2. Verify microphone permissions")
        print("3. Close other applications using the microphone")
        print("4. Try running as administrator (Windows) or with sudo (Linux)")
        return False
    
    print("\n2️⃣  Audio device information:")
    audio_manager.list_devices()
    
    print("\n3️⃣  Testing selected input device...")
    input_device_index = audio_manager.get_input_device_index()
    
    if input_device_index is None:
        print("❌ No input device selected")
        return False
    
    # Test recording
    print(f"🎤 Testing recording with device index {input_device_index}")
    print("   This will record for 3 seconds...")
    
    try:
        import pyaudio
        import numpy as np
        
        # Test recording
        stream = audio_manager.audio.open(
            format=pyaudio.paInt16,
            channels=CHANNELS,
            rate=SAMPLE_RATE,
            input=True,
            input_device_index=input_device_index,
            frames_per_buffer=CHUNK_SIZE
        )
        
        print("🔴 Recording... speak now!")
        frames = []
        max_rms = 0
        
        for i in range(0, int(SAMPLE_RATE / CHUNK_SIZE * 10)):  # 3 seconds
            data = stream.read(CHUNK_SIZE, exception_on_overflow=False)
            frames.append(data)
            
            # Calculate RMS for volume monitoring with safe error handling
            try:
                audio_np = np.frombuffer(data, dtype=np.int16)
                
                # Validate the audio data
                if len(audio_np) == 0:
                    rms = 0.0
                elif np.any(np.isnan(audio_np)) or np.any(np.isinf(audio_np)):
                    print("⚠️  Warning: Invalid audio data detected, using fallback")
                    rms = 0.0
                else:
                    # Clip values to prevent overflow and calculate safely
                    audio_clipped = np.clip(audio_np, -32767, 32767)
                    mean_square = np.mean(audio_clipped.astype(np.float64)**2)
                    
                    if mean_square < 0 or np.isnan(mean_square) or np.isinf(mean_square):
                        rms = 0.0
                    else:
                        rms = np.sqrt(mean_square)
                        
            except Exception as e:
                print(f"⚠️  Warning: RMS calculation failed: {e}")
                rms = 0.0
            
            max_rms = max(max_rms, rms)
            
            # Show progress
            if i % 10 == 0:
                print(f"   📊 Current volume level: {rms:.0f}")
        
        stream.stop_stream()
        stream.close()
        
        print("⏹️  Recording test completed")
        print(f"📊 Maximum volume detected: {max_rms:.0f}")
        print(f"🔊 Silence threshold: {SILENCE_THRESHOLD}")
        
        if max_rms > SILENCE_THRESHOLD:
            print("✅ Audio input is working! Volume is above silence threshold.")
        else:
            print("⚠️  Audio input detected but volume is low.")
            print("💡 Try speaking louder or adjusting microphone sensitivity")
        
        # Save test recording
        if frames:
            import wave
            import os
            
            # Ensure the temp audio directory exists
            try:
                os.makedirs(TEMP_AUDIO_DIR, exist_ok=True)
                print(f"📁 Temp directory ready: {TEMP_AUDIO_DIR}")
            except Exception as e:
                print(f"⚠️  Warning: Could not create temp directory: {e}")
                print("💾 Skipping test file save...")
                return True  # Continue anyway, the main test passed
            
            test_file = os.path.join(TEMP_AUDIO_DIR, "audio_test.wav")
            
            try:
                with wave.open(test_file, 'wb') as wf:
                    wf.setnchannels(CHANNELS)
                    wf.setsampwidth(audio_manager.audio.get_sample_size(pyaudio.paInt16))
                    wf.setframerate(SAMPLE_RATE)
                    wf.writeframes(b''.join(frames))
                
                print(f"💾 Test recording saved to: {test_file}")
                
            except Exception as e:
                print(f"⚠️  Warning: Could not save test recording: {e}")
                print("💡 This doesn't affect the main audio functionality")
        
        return True
        
    except Exception as e:
        print(f"❌ Recording test failed: {e}")
        if "Invalid input device" in str(e) or "-9996" in str(e):
            print("💡 This is the same error you were experiencing!")
            audio_manager._print_input_device_troubleshooting()
        return False
    
    finally:
        audio_manager.cleanup()

def main():
    """Main function"""
    try:
        success = run_audio_diagnostics()
        
        if success:
            print("\n✅ Audio diagnostics completed successfully!")
            print("💡 Your audio system should now work with the voice chat application")
        else:
            print("\n❌ Audio diagnostics failed")
            print("💡 Please follow the troubleshooting steps above")
            
    except KeyboardInterrupt:
        print("\n\n🛑 Diagnostics interrupted by user")
    except Exception as e:
        print(f"\n❌ Unexpected error during diagnostics: {e}")

if __name__ == "__main__":
    main()
