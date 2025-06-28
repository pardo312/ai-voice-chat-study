#!/usr/bin/env python3
"""
Audio Recorder Usage Examples
Demonstrates how to use the SimpleAudioRecorder class programmatically.
"""

try:
    # Try relative imports first (when used as a module)
    from .simple_audio_recorder import SimpleAudioRecorder
except ImportError:
    # Fall back to absolute imports (when run as a script)
    from simple_audio_recorder import SimpleAudioRecorder
import time

def example_fixed_duration_recording():
    """Example: Record for a fixed duration."""
    print("🎯 Example 1: Fixed Duration Recording")
    print("-" * 40)
    
    # Create recorder instance
    recorder = SimpleAudioRecorder(sample_rate=44100, channels=1)
    
    if not recorder.initialize():
        print("❌ Failed to initialize recorder")
        return
    
    try:
        # Record for 5 seconds
        print("Recording for 5 seconds...")
        result = recorder.record_fixed_duration(
            duration_seconds=5.0,
            output_file="example_fixed_5sec.wav"
        )
        
        if result:
            print(f"✅ Recording saved to: {result}")
        else:
            print("❌ Recording failed")
    
    finally:
        recorder.cleanup()

def example_voice_activity_detection():
    """Example: Record with voice activity detection."""
    print("\n🎯 Example 2: Voice Activity Detection")
    print("-" * 40)
    
    # Create recorder instance with custom settings
    recorder = SimpleAudioRecorder(
        sample_rate=16000,  # Lower sample rate for speech
        channels=1,
        chunk_size=1024
    )
    
    if not recorder.initialize():
        print("❌ Failed to initialize recorder")
        return
    
    try:
        # Record with voice activity detection
        print("Recording with voice activity detection...")
        result = recorder.record_with_silence_detection(
            output_file="example_vad.wav",
            silence_threshold=300,  # Lower threshold for sensitive detection
            silence_duration=1.5,   # Stop after 1.5 seconds of silence
            max_duration=20         # Maximum 20 seconds
        )
        
        if result:
            print(f"✅ Recording saved to: {result}")
        else:
            print("❌ Recording failed")
    
    finally:
        recorder.cleanup()

def example_batch_recording():
    """Example: Record multiple files in sequence."""
    print("\n🎯 Example 3: Batch Recording")
    print("-" * 40)
    
    recorder = SimpleAudioRecorder()
    
    if not recorder.initialize():
        print("❌ Failed to initialize recorder")
        return
    
    try:
        # Record 3 short clips
        for i in range(3):
            print(f"\nRecording clip {i+1}/3...")
            input("Press Enter when ready to record...")
            
            result = recorder.record_fixed_duration(
                duration_seconds=3.0,
                output_file=f"batch_recording_{i+1}.wav"
            )
            
            if result:
                print(f"✅ Clip {i+1} saved to: {result}")
            else:
                print(f"❌ Clip {i+1} failed")
            
            time.sleep(1)  # Brief pause between recordings
    
    finally:
        recorder.cleanup()

def example_custom_settings():
    """Example: Using custom audio settings."""
    print("\n🎯 Example 4: Custom Audio Settings")
    print("-" * 40)
    
    # High-quality stereo recording
    recorder = SimpleAudioRecorder(
        sample_rate=48000,  # High sample rate
        channels=2,         # Stereo
        chunk_size=2048     # Larger buffer
    )
    
    if not recorder.initialize():
        print("❌ Failed to initialize recorder")
        return
    
    try:
        print("High-quality stereo recording...")
        result = recorder.record_fixed_duration(
            duration_seconds=3.0,
            output_file="high_quality_stereo.wav"
        )
        
        if result:
            print(f"✅ High-quality recording saved to: {result}")
        else:
            print("❌ Recording failed")
    
    finally:
        recorder.cleanup()

def main():
    """Run all examples."""
    print("🎵 Audio Recorder Examples")
    print("=" * 50)
    
    try:
        # Run examples
        example_fixed_duration_recording()
        
        input("\nPress Enter to continue to next example...")
        example_voice_activity_detection()
        
        input("\nPress Enter to continue to batch recording example...")
        example_batch_recording()
        
        input("\nPress Enter to continue to custom settings example...")
        example_custom_settings()
        
        print("\n🎉 All examples completed!")
        
    except KeyboardInterrupt:
        print("\n👋 Examples interrupted by user")
    except Exception as e:
        print(f"\n❌ Error running examples: {e}")

if __name__ == "__main__":
    main()
