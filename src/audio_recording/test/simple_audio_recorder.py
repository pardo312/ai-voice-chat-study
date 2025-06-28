#!/usr/bin/env python3
"""
Simple Audio Recorder Script
A standalone script for recording audio to file with minimal dependencies.
"""

import pyaudio
import wave
import numpy as np
import os
import sys
import time
from datetime import datetime
from pathlib import Path

class SimpleAudioRecorder:
    def __init__(self, 
                 sample_rate=44100, 
                 channels=1, 
                 chunk_size=1024,
                 audio_format=pyaudio.paInt16):
        """
        Initialize the audio recorder with configurable parameters.
        
        Args:
            sample_rate (int): Sample rate in Hz (default: 44100)
            channels (int): Number of audio channels (default: 1 for mono)
            chunk_size (int): Buffer size for audio chunks (default: 1024)
            audio_format: PyAudio format (default: paInt16)
        """
        self.sample_rate = sample_rate
        self.channels = channels
        self.chunk_size = chunk_size
        self.audio_format = audio_format
        self.audio = None
        self.stream = None
        self.frames = []
        self.is_recording = False
        
    def initialize(self):
        """Initialize PyAudio and find available input devices."""
        try:
            self.audio = pyaudio.PyAudio()
            print("🎵 Audio system initialized")
            
            # List available input devices
            self._list_input_devices()
            return True
            
        except Exception as e:
            print(f"❌ Failed to initialize audio: {e}")
            return False
    
    def _list_input_devices(self):
        """List all available input devices."""
        print("\n🎤 Available Input Devices:")
        print("-" * 40)
        
        device_count = self.audio.get_device_count()
        input_devices = []
        
        for i in range(device_count):
            try:
                device_info = self.audio.get_device_info_by_index(i)
                if device_info['maxInputChannels'] > 0:
                    input_devices.append((i, device_info))
                    print(f"[{i}] {device_info['name']} - {device_info['maxInputChannels']} channels")
            except:
                continue
        
        if not input_devices:
            print("❌ No input devices found!")
            return False
        
        print("-" * 40)
        return True
    
    def record_fixed_duration(self, duration_seconds, output_file=None, device_index=None):
        """
        Record audio for a fixed duration.
        
        Args:
            duration_seconds (float): Duration to record in seconds
            output_file (str): Output filename (optional, auto-generated if None)
            device_index (int): Input device index (optional, uses default if None)
        
        Returns:
            str: Path to the recorded file, or None if failed
        """
        if output_file is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"recording_{timestamp}.wav"
        
        try:
            # Open audio stream
            self.stream = self.audio.open(
                format=self.audio_format,
                channels=self.channels,
                rate=self.sample_rate,
                input=True,
                input_device_index=device_index,
                frames_per_buffer=self.chunk_size
            )
            
            print(f"🔴 Recording for {duration_seconds} seconds...")
            print("🎤 Speak now!")
            
            self.frames = []
            self.is_recording = True
            
            # Calculate number of chunks to record
            chunks_to_record = int(self.sample_rate / self.chunk_size * duration_seconds)
            
            # Record audio
            for i in range(chunks_to_record):
                try:
                    data = self.stream.read(self.chunk_size, exception_on_overflow=False)
                    self.frames.append(data)
                    
                    # Show progress
                    progress = (i + 1) / chunks_to_record * 100
                    if i % (chunks_to_record // 10) == 0:  # Update every 10%
                        print(f"📊 Progress: {progress:.0f}%")
                        
                except Exception as e:
                    print(f"⚠️ Warning during recording: {e}")
                    break
            
            self.is_recording = False
            print("⏹️ Recording completed!")
            
            # Stop and close stream
            self.stream.stop_stream()
            self.stream.close()
            
            # Save to file
            return self._save_to_file(output_file)
            
        except Exception as e:
            print(f"❌ Recording failed: {e}")
            self.is_recording = False
            if self.stream:
                try:
                    self.stream.stop_stream()
                    self.stream.close()
                except:
                    pass
            return None
    
    def record_with_silence_detection(self, output_file=None, device_index=None, 
                                    silence_threshold=500, silence_duration=2.0, 
                                    max_duration=30):
        """
        Record audio with automatic silence detection to stop recording.
        
        Args:
            output_file (str): Output filename (optional)
            device_index (int): Input device index (optional)
            silence_threshold (int): RMS threshold for silence detection
            silence_duration (float): Seconds of silence before stopping
            max_duration (float): Maximum recording duration in seconds
        
        Returns:
            str: Path to the recorded file, or None if failed
        """
        if output_file is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"recording_vad_{timestamp}.wav"
        
        try:
            # Open audio stream
            self.stream = self.audio.open(
                format=self.audio_format,
                channels=self.channels,
                rate=self.sample_rate,
                input=True,
                input_device_index=device_index,
                frames_per_buffer=self.chunk_size
            )
            
            print("🎤 Listening... Start speaking!")
            print(f"🔇 Will stop after {silence_duration}s of silence")
            
            self.frames = []
            self.is_recording = True
            silent_chunks = 0
            recording_started = False
            total_chunks = 0
            max_chunks = int(self.sample_rate / self.chunk_size * max_duration)
            
            while self.is_recording and total_chunks < max_chunks:
                try:
                    data = self.stream.read(self.chunk_size, exception_on_overflow=False)
                    
                    # Calculate RMS for volume detection
                    audio_data = np.frombuffer(data, dtype=np.int16)
                    rms = np.sqrt(np.mean(audio_data**2))
                    
                    if rms > silence_threshold:
                        if not recording_started:
                            print("🔴 Voice detected! Recording started...")
                            recording_started = True
                        
                        self.frames.append(data)
                        silent_chunks = 0
                        
                        # Show volume indicator
                        volume_bars = int(min(rms / 100, 20))
                        volume_indicator = "█" * volume_bars + "░" * (20 - volume_bars)
                        print(f"\r🎵 Volume: [{volume_indicator}] {rms:.0f}", end="", flush=True)
                        
                    else:
                        if recording_started:
                            self.frames.append(data)
                            silent_chunks += 1
                            
                            # Check if we've been silent long enough
                            silence_time = silent_chunks * self.chunk_size / self.sample_rate
                            if silence_time >= silence_duration:
                                print(f"\n🔇 {silence_duration}s of silence detected. Stopping...")
                                break
                    
                    total_chunks += 1
                    
                except KeyboardInterrupt:
                    print("\n⏹️ Recording stopped by user")
                    break
                except Exception as e:
                    print(f"\n⚠️ Warning during recording: {e}")
                    break
            
            if total_chunks >= max_chunks:
                print(f"\n⏰ Maximum recording time ({max_duration}s) reached")
            
            self.is_recording = False
            
            # Stop and close stream
            self.stream.stop_stream()
            self.stream.close()
            
            if not self.frames:
                print("❌ No audio recorded")
                return None
            
            print(f"\n✅ Recording completed! Duration: {len(self.frames) * self.chunk_size / self.sample_rate:.1f}s")
            
            # Save to file
            return self._save_to_file(output_file)
            
        except Exception as e:
            print(f"❌ Recording failed: {e}")
            self.is_recording = False
            if self.stream:
                try:
                    self.stream.stop_stream()
                    self.stream.close()
                except:
                    pass
            return None
    
    def _save_to_file(self, filename):
        """Save recorded frames to a WAV file."""
        try:
            # Ensure directory exists
            Path(filename).parent.mkdir(parents=True, exist_ok=True)
            
            with wave.open(filename, 'wb') as wf:
                wf.setnchannels(self.channels)
                wf.setsampwidth(self.audio.get_sample_size(self.audio_format))
                wf.setframerate(self.sample_rate)
                wf.writeframes(b''.join(self.frames))
            
            file_size = os.path.getsize(filename)
            print(f"💾 Audio saved to: {filename}")
            print(f"📊 File size: {file_size / 1024:.1f} KB")
            
            return filename
            
        except Exception as e:
            print(f"❌ Failed to save audio: {e}")
            return None
    
    def cleanup(self):
        """Clean up audio resources."""
        if self.stream:
            try:
                if self.is_recording:
                    self.stream.stop_stream()
                self.stream.close()
            except:
                pass
            self.stream = None
        
        if self.audio:
            try:
                self.audio.terminate()
            except:
                pass
            self.audio = None

def main():
    """Main function with interactive menu."""
    print("🎵 Simple Audio Recorder")
    print("=" * 30)
    
    # Initialize recorder
    recorder = SimpleAudioRecorder()
    if not recorder.initialize():
        print("❌ Failed to initialize audio system")
        return
    
    try:
        while True:
            print("\n📋 Recording Options:")
            print("1. Record for fixed duration")
            print("2. Record with voice activity detection")
            print("3. List input devices")
            print("4. Exit")
            
            choice = input("\n👉 Select option (1-4): ").strip()
            
            if choice == "1":
                try:
                    duration = float(input("⏱️ Enter duration in seconds: "))
                    device_input = input("🎤 Enter device index (or press Enter for default): ").strip()
                    device_index = int(device_input) if device_input else None
                    filename = input("💾 Enter filename (or press Enter for auto): ").strip()
                    filename = filename if filename else None
                    
                    result = recorder.record_fixed_duration(duration, filename, device_index)
                    if result:
                        print(f"✅ Recording saved successfully!")
                    
                except ValueError:
                    print("❌ Invalid input. Please enter a valid number.")
                except KeyboardInterrupt:
                    print("\n⏹️ Recording cancelled")
            
            elif choice == "2":
                try:
                    device_input = input("🎤 Enter device index (or press Enter for default): ").strip()
                    device_index = int(device_input) if device_input else None
                    filename = input("💾 Enter filename (or press Enter for auto): ").strip()
                    filename = filename if filename else None
                    
                    print("\n💡 Tip: Press Ctrl+C to stop recording manually")
                    result = recorder.record_with_silence_detection(filename, device_index)
                    if result:
                        print(f"✅ Recording saved successfully!")
                    
                except ValueError:
                    print("❌ Invalid device index.")
                except KeyboardInterrupt:
                    print("\n⏹️ Recording cancelled")
            
            elif choice == "3":
                recorder._list_input_devices()
            
            elif choice == "4":
                print("👋 Goodbye!")
                break
            
            else:
                print("❌ Invalid choice. Please select 1-4.")
    
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    
    finally:
        recorder.cleanup()

if __name__ == "__main__":
    main()
