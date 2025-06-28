"""
Audio Recording Module for Voice Chat Application
Handles microphone input and audio file operations with enhanced device management
"""

import pyaudio
import wave
import numpy as np
import threading
import time
import os
from pathlib import Path
try:
    # Try relative imports first (when used as a module)
    from ..config import *
    from .audio_manager import AudioManager
except ImportError:
    # Fall back to absolute imports (when run as a script)
    import sys
    import os
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    from config import *
    from audio_manager import AudioManager

class AudioRecorder:
    def __init__(self):
        self.audio_manager = AudioManager()
        self.is_recording = False
        self.frames = []
        self.input_device_index = None
        
        # Create temp directory if it doesn't exist
        Path(TEMP_AUDIO_DIR).mkdir(exist_ok=True)
        
    def initialize(self):
        """Initialize the audio system with enhanced device management"""
        if not self.audio_manager.initialize():
            return False
        
        self.input_device_index = self.audio_manager.get_input_device_index()
        
        if self.input_device_index is None:
            print("❌ No valid input device available")
            return False
        
        # Show available devices
        self.audio_manager.list_devices()
        return True
    
    def _calculate_rms(self, audio_data):
        """Calculate RMS (Root Mean Square) for volume detection"""
        audio_np = np.frombuffer(audio_data, dtype=np.int16)
        return np.sqrt(np.mean(audio_np**2))
    
    def _calibrate_ambient_noise(self, stream):
        """Calibrate ambient noise level for dynamic threshold adjustment"""
        print("🔧 Calibrating ambient noise level...")
        noise_samples = []
        
        calibration_chunks = int(SAMPLE_RATE / CHUNK_SIZE * AMBIENT_NOISE_CALIBRATION_TIME)
        
        for _ in range(calibration_chunks):
            try:
                data = stream.read(CHUNK_SIZE, exception_on_overflow=False)
                rms = self._calculate_rms(data)
                noise_samples.append(rms)
            except Exception:
                break
        
        if noise_samples:
            ambient_noise = np.mean(noise_samples)
            # Set dynamic threshold as ambient noise + buffer
            dynamic_threshold = max(SILENCE_THRESHOLD, ambient_noise * 2.5)
            print(f"🎯 Ambient noise: {ambient_noise:.1f}, Dynamic threshold: {dynamic_threshold:.1f}")
            return dynamic_threshold
        
        return SILENCE_THRESHOLD
    
    def _smooth_volume(self, volume_history, current_rms):
        """Apply smoothing to volume detection to reduce false triggers"""
        volume_history.append(current_rms)
        
        # Keep only the last N samples for smoothing
        if len(volume_history) > VOLUME_SMOOTHING_WINDOW:
            volume_history.pop(0)
        
        # Return smoothed average
        return np.mean(volume_history)
    
    def record_chunk(self, duration=None):
        """Record a single audio chunk with enhanced error handling"""
        if duration is None:
            duration = RECORD_DURATION
        
        if self.input_device_index is None:
            print("❌ No input device available for recording")
            return None
            
        try:
            # Open stream using AudioManager's PyAudio instance
            stream = self.audio_manager.audio.open(
                format=pyaudio.paInt16,
                channels=CHANNELS,
                rate=SAMPLE_RATE,
                input=True,
                input_device_index=self.input_device_index,
                frames_per_buffer=CHUNK_SIZE
            )
            
            print("🎤 Recording... (speak now)")
            frames = []
            
            # Record for specified duration
            for _ in range(0, int(SAMPLE_RATE / CHUNK_SIZE * duration)):
                try:
                    data = stream.read(CHUNK_SIZE, exception_on_overflow=False)
                    frames.append(data)
                except Exception as e:
                    print(f"⚠️  Warning during recording: {e}")
                    break
            
            print("⏹️  Recording stopped")
            
            # Stop and close stream
            stream.stop_stream()
            stream.close()
            
            return frames
            
        except Exception as e:
            print(f"❌ Recording error: {e}")
            if "Invalid input device" in str(e) or "-9996" in str(e):
                print("💡 This usually means the microphone is not accessible or in use by another application")
                self.audio_manager._print_input_device_troubleshooting()
            return None
    
    def record_with_vad(self):
        """Record with enhanced Voice Activity Detection including pre-buffering"""
        if self.input_device_index is None:
            print("❌ No input device available for recording")
            return None
            
        try:
            # Open stream using AudioManager's PyAudio instance
            stream = self.audio_manager.audio.open(
                format=pyaudio.paInt16,
                channels=CHANNELS,
                rate=SAMPLE_RATE,
                input=True,
                input_device_index=self.input_device_index,
                frames_per_buffer=CHUNK_SIZE
            )
            
            # Calibrate ambient noise level for dynamic threshold
            dynamic_threshold = self._calibrate_ambient_noise(stream)
            
            print("🎤 Recording... (speak now)")
            
            # Pre-buffer to capture audio before voice detection
            pre_buffer_chunks = int(SAMPLE_RATE / CHUNK_SIZE * PRE_BUFFER_DURATION)
            pre_buffer = []
            all_frames = []
            volume_history = []
            silent_chunks = 0
            recording_started = False
            total_recording_time = 0
            
            while True:
                try:
                    data = stream.read(CHUNK_SIZE, exception_on_overflow=False)
                    rms = self._calculate_rms(data)
                    
                    # Apply volume smoothing
                    smoothed_rms = self._smooth_volume(volume_history, rms)
                    
                    # Always add to pre-buffer (circular buffer)
                    pre_buffer.append(data)
                    if len(pre_buffer) > pre_buffer_chunks:
                        pre_buffer.pop(0)
                    
                    # Check if sound is above dynamic threshold
                    if smoothed_rms > dynamic_threshold:
                        if not recording_started:
                            print("🔴 Voice detected, active recording...")
                            recording_started = True
                            # Add pre-buffered audio to capture speech that started before detection
                            all_frames.extend(pre_buffer)
                            pre_buffer = []  # Clear pre-buffer since we've used it
                        
                        all_frames.append(data)
                        silent_chunks = 0
                        total_recording_time += CHUNK_SIZE / SAMPLE_RATE
                    else:
                        if recording_started:
                            all_frames.append(data)
                            silent_chunks += 1
                            total_recording_time += CHUNK_SIZE / SAMPLE_RATE
                            
                            # Check if we've been silent long enough to stop
                            silence_duration = silent_chunks * CHUNK_SIZE / SAMPLE_RATE
                            
                            # Only stop if we've recorded for minimum duration and detected sufficient silence
                            if (silence_duration >= SILENCE_DURATION and 
                                total_recording_time >= MIN_RECORDING_DURATION):
                                print("⏹️  Natural pause detected, stopping recording")
                                break
                    
                    # Safety check - don't record forever
                    if total_recording_time > 30:  # 30 seconds max
                        print("⏰ Maximum recording time reached")
                        break
                        
                except Exception as e:
                    print(f"⚠️  Warning during VAD recording: {e}")
                    break
            
            stream.stop_stream()
            stream.close()
            
            if not all_frames:
                print("⚠️  No speech detected")
                return None
            
            # Ensure minimum recording duration was met
            if total_recording_time < MIN_RECORDING_DURATION:
                print(f"⚠️  Recording too short ({total_recording_time:.1f}s), minimum is {MIN_RECORDING_DURATION}s")
                return None
                
            print(f"✅ Recording completed ({total_recording_time:.1f}s)")
            return all_frames
            
        except Exception as e:
            print(f"❌ Recording with VAD error: {e}")
            if "Invalid input device" in str(e) or "-9996" in str(e):
                print("💡 This usually means the microphone is not accessible or in use by another application")
                self.audio_manager._print_input_device_troubleshooting()
            return None
    
    def save_audio(self, frames, filename=None):
        """Save recorded frames to a WAV file"""
        if not frames:
            return None
            
        if filename is None:
            filename = os.path.join(TEMP_AUDIO_DIR, TEMP_INPUT_FILE)
        
        try:
            with wave.open(filename, 'wb') as wf:
                wf.setnchannels(CHANNELS)
                wf.setsampwidth(self.audio_manager.audio.get_sample_size(pyaudio.paInt16))
                wf.setframerate(SAMPLE_RATE)
                wf.writeframes(b''.join(frames))
            
            return filename
            
        except Exception as e:
            print(f"❌ Error saving audio: {e}")
            return None
    
    def record_and_save(self, use_vad=True):
        """Record audio and save to file"""
        if use_vad:
            frames = self.record_with_vad()
        else:
            frames = self.record_chunk()
        
        if frames:
            return self.save_audio(frames)
        return None
    
    def cleanup(self):
        """Clean up audio resources"""
        if self.audio_manager:
            self.audio_manager.cleanup()
    
    def __del__(self):
        """Destructor to ensure cleanup"""
        self.cleanup()
