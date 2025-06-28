"""
Enhanced Audio Device Management for Voice Chat Application
Handles audio device detection, validation, and selection with robust error handling
"""

import pyaudio
import sys
import platform
import logging
from typing import List, Dict, Optional, Tuple

from ..config import VERBOSE_MODE

logger = logging.getLogger(__name__)


class AudioDeviceInfo:
    """Container for audio device information"""
    
    def __init__(self, index: int, info: dict):
        self.index = index
        self.name = info.get('name', 'Unknown Device')
        self.max_input_channels = info.get('maxInputChannels', 0)
        self.max_output_channels = info.get('maxOutputChannels', 0)
        self.default_sample_rate = info.get('defaultSampleRate', 44100)
        self.host_api = info.get('hostApi', 0)
        self.is_input_device = self.max_input_channels > 0
        self.is_output_device = self.max_output_channels > 0
    
    def __str__(self):
        device_type = []
        if self.is_input_device:
            device_type.append(f"Input({self.max_input_channels}ch)")
        if self.is_output_device:
            device_type.append(f"Output({self.max_output_channels}ch)")
        
        return f"[{self.index}] {self.name} - {'/'.join(device_type)} @ {self.default_sample_rate}Hz"


class AudioManager:
    """Enhanced audio device manager with robust error handling"""
    
    def __init__(self):
        self.audio = None
        self.available_input_devices: List[AudioDeviceInfo] = []
        self.available_output_devices: List[AudioDeviceInfo] = []
        self.selected_input_device: Optional[AudioDeviceInfo] = None
        self.selected_output_device: Optional[AudioDeviceInfo] = None
        self.system_info = self._get_system_info()
        
        if VERBOSE_MODE:
            logger.info("AudioManager initialized")
        
    def _get_system_info(self) -> Dict[str, str]:
        """Get system information for audio troubleshooting"""
        return {
            'platform': platform.system(),
            'platform_version': platform.version(),
            'architecture': platform.architecture()[0]
        }
    
    def initialize(self) -> bool:
        """Initialize PyAudio and discover devices"""
        try:
            print("🔍 Initializing audio system...")
            logger.info("Initializing audio system")
            self.audio = pyaudio.PyAudio()
            
            # Discover and validate devices
            if not self._discover_devices():
                return False
            
            # Select best devices
            if not self._select_devices():
                return False
            
            print("✅ Audio system initialized successfully")
            logger.info("Audio system initialized successfully")
            return True
            
        except Exception as e:
            error_msg = f"Failed to initialize audio system: {e}"
            logger.error(error_msg)
            print(f"❌ {error_msg}")
            self._print_troubleshooting_info()
            return False
    
    def _discover_devices(self) -> bool:
        """Discover and catalog all available audio devices"""
        try:
            device_count = self.audio.get_device_count()
            print(f"🔍 Found {device_count} audio devices")
            logger.info(f"Found {device_count} audio devices")
            
            self.available_input_devices = []
            self.available_output_devices = []
            
            for i in range(device_count):
                try:
                    device_info = self.audio.get_device_info_by_index(i)
                    device = AudioDeviceInfo(i, device_info)
                    
                    if device.is_input_device:
                        # Test if the input device actually works
                        if self._test_input_device(device):
                            self.available_input_devices.append(device)
                            if VERBOSE_MODE:
                                print(f"✅ Input: {device}")
                            logger.debug(f"Working input device: {device}")
                        else:
                            if VERBOSE_MODE:
                                print(f"⚠️  Input (failed test): {device}")
                            logger.warning(f"Input device failed test: {device}")
                    
                    if device.is_output_device:
                        self.available_output_devices.append(device)
                        if VERBOSE_MODE:
                            print(f"✅ Output: {device}")
                        logger.debug(f"Output device: {device}")
                        
                except Exception as e:
                    if VERBOSE_MODE:
                        print(f"⚠️  Device {i}: Error getting info - {e}")
                    logger.warning(f"Error getting device {i} info: {e}")
                    continue
            
            print(f"\n📊 Summary:")
            print(f"   🎤 Working input devices: {len(self.available_input_devices)}")
            print(f"   🔊 Output devices: {len(self.available_output_devices)}")
            
            logger.info(f"Device discovery complete: {len(self.available_input_devices)} input, {len(self.available_output_devices)} output")
            
            if len(self.available_input_devices) == 0:
                print("❌ No working input devices found!")
                logger.error("No working input devices found")
                self._print_input_device_troubleshooting()
                return False
            
            return True
            
        except Exception as e:
            error_msg = f"Error during device discovery: {e}"
            logger.error(error_msg)
            print(f"❌ {error_msg}")
            return False
    
    def _test_input_device(self, device: AudioDeviceInfo, sample_rate: int = 16000) -> bool:
        """Test if an input device can actually be opened for recording"""
        try:
            # Try to open a stream with the device
            stream = self.audio.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=sample_rate,
                input=True,
                input_device_index=device.index,
                frames_per_buffer=1024
            )
            
            # Try to read a small amount of data
            stream.read(1024, exception_on_overflow=False)
            
            # Close the stream
            stream.stop_stream()
            stream.close()
            
            logger.debug(f"Input device test passed: {device.name}")
            return True
            
        except Exception as e:
            # Device failed the test
            logger.debug(f"Input device test failed: {device.name} - {e}")
            return False
    
    def _select_devices(self) -> bool:
        """Select the best available input and output devices"""
        # Select input device
        if not self.available_input_devices:
            logger.error("No input devices available for selection")
            print("❌ No input devices available for selection")
            return False
        
        # Try to get default input device first
        try:
            default_input = self.audio.get_default_input_device_info()
            default_index = default_input['index']
            
            # Check if default device is in our working list
            for device in self.available_input_devices:
                if device.index == default_index:
                    self.selected_input_device = device
                    print(f"🎤 Selected default input device: {device}")
                    logger.info(f"Selected default input device: {device.name}")
                    break
        except Exception as e:
            logger.warning(f"Could not get default input device: {e}")
        
        # If no default device found, use the first working device
        if not self.selected_input_device:
            self.selected_input_device = self.available_input_devices[0]
            print(f"🎤 Selected first available input device: {self.selected_input_device}")
            logger.info(f"Selected first available input device: {self.selected_input_device.name}")
        
        # Select output device (for future use)
        if self.available_output_devices:
            try:
                default_output = self.audio.get_default_output_device_info()
                default_index = default_output['index']
                
                for device in self.available_output_devices:
                    if device.index == default_index:
                        self.selected_output_device = device
                        if VERBOSE_MODE:
                            print(f"🔊 Selected default output device: {device}")
                        logger.info(f"Selected default output device: {device.name}")
                        break
            except Exception as e:
                logger.warning(f"Could not get default output device: {e}")
            
            if not self.selected_output_device:
                self.selected_output_device = self.available_output_devices[0]
                if VERBOSE_MODE:
                    print(f"🔊 Selected first available output device: {self.selected_output_device}")
                logger.info(f"Selected first available output device: {self.selected_output_device.name}")
        
        return True
    
    def get_input_device_index(self) -> Optional[int]:
        """Get the index of the selected input device"""
        return self.selected_input_device.index if self.selected_input_device else None
    
    def get_output_device_index(self) -> Optional[int]:
        """Get the index of the selected output device"""
        return self.selected_output_device.index if self.selected_output_device else None
    
    def list_devices(self) -> None:
        """Print a detailed list of all available devices"""
        print("\n🎵 Available Audio Devices:")
        print("=" * 50)
        
        if self.available_input_devices:
            print("\n🎤 Input Devices (Microphones):")
            for device in self.available_input_devices:
                marker = "👉" if device == self.selected_input_device else "  "
                print(f"{marker} {device}")
        else:
            print("\n❌ No working input devices found")
        
        if self.available_output_devices:
            print("\n🔊 Output Devices (Speakers):")
            for device in self.available_output_devices:
                marker = "👉" if device == self.selected_output_device else "  "
                print(f"{marker} {device}")
        else:
            print("\n❌ No output devices found")
        
        print("=" * 50)
    
    def _print_input_device_troubleshooting(self) -> None:
        """Print troubleshooting information for input device issues"""
        print("\n🔧 Input Device Troubleshooting:")
        print("=" * 40)
        
        system = self.system_info['platform']
        
        if system == "Windows":
            print("Windows Troubleshooting:")
            print("1. Check if microphone is connected and recognized in Device Manager")
            print("2. Go to Settings > Privacy > Microphone and ensure app permissions are enabled")
            print("3. Check Windows Sound settings - ensure microphone is set as default")
            print("4. Try running as administrator")
            print("5. Update audio drivers")
            
        elif system == "Darwin":  # macOS
            print("macOS Troubleshooting:")
            print("1. Go to System Preferences > Security & Privacy > Privacy > Microphone")
            print("2. Ensure your terminal/IDE has microphone access")
            print("3. Check System Preferences > Sound > Input")
            print("4. Try disconnecting and reconnecting external microphones")
            
        elif system == "Linux":
            print("Linux Troubleshooting:")
            print("1. Check if user is in 'audio' group: groups $USER")
            print("2. Install/configure PulseAudio: sudo apt install pulseaudio")
            print("3. Check ALSA devices: arecord -l")
            print("4. Test microphone: arecord -d 5 test.wav")
            print("5. Check permissions on /dev/snd/*")
            
        print("\nGeneral troubleshooting:")
        print("- Ensure no other applications are using the microphone")
        print("- Try different USB ports for external microphones")
        print("- Restart the audio service/daemon")
        print("- Check if microphone is muted in system settings")
    
    def _print_troubleshooting_info(self) -> None:
        """Print general troubleshooting information"""
        print("\n🔧 Audio System Troubleshooting:")
        print("=" * 40)
        print(f"System: {self.system_info['platform']} {self.system_info['platform_version']}")
        print(f"Architecture: {self.system_info['architecture']}")
        
        try:
            print(f"PyAudio version: {pyaudio.__version__}")
        except:
            print("PyAudio version: Unknown")
        
        print("\nCommon solutions:")
        print("1. Restart the application")
        print("2. Check microphone connections")
        print("3. Verify microphone permissions")
        print("4. Close other audio applications")
        print("5. Update audio drivers")
    
    def cleanup(self) -> None:
        """Clean up audio resources"""
        if self.audio:
            try:
                self.audio.terminate()
                logger.info("Audio system cleaned up")
            except Exception as e:
                logger.warning(f"Error during audio cleanup: {e}")
            self.audio = None
    
    def __del__(self):
        """Destructor to ensure cleanup"""
        self.cleanup()
