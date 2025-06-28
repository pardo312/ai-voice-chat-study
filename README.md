# Voice Chat with AI

A real-time voice chat application that listens to your speech, transcribes it using FastWhisper, and repeats it back to you using XTTS text-to-speech synthesis.

## 🎯 Features

- **Real-time Voice Processing**: Continuous speech-to-text and text-to-speech loop
- **Voice Activity Detection**: Automatically starts/stops recording based on speech detection
- **Multiple Exit Options**: Exit via Ctrl+C or voice commands ("exit", "quit", "stop")
- **Voice Cloning Support**: Optional voice cloning using XTTS
- **Configurable Settings**: Adjustable audio quality, model sizes, and processing options
- **Clean Interface**: Clear status updates and progress indicators

## 🏗️ Architecture

The application consists of four main components:

1. **Audio Recorder** (`audio_recorder.py`) - Handles microphone input and voice activity detection
2. **Speech Processor** (`speech_processor.py`) - Manages FastWhisper and XTTS models
3. **Main Application** (`voice_chat.py`) - Orchestrates the voice chat loop
4. **Configuration** (`config.py`) - Centralized settings management

## 📋 Prerequisites

This application requires the existing FastWhisper and XTTS projects to be set up:

- **FastWhisper**: Located in `../FastWhisper/` with faster-whisper installed
- **XTTS**: Located in `../XTTS/` with TTS library installed

## 🚀 Installation

1. **Install additional dependencies**:
   ```bash
   pip install pyaudio pygame numpy
   ```

2. **Verify existing setups**:
   - Ensure FastWhisper environment is working
   - Ensure XTTS environment is working
   - Test your microphone and speakers

3. **Optional: Voice Cloning Setup**:
   - Place a voice sample (10-30 seconds) as `voice_sample.wav` in the project directory
   - Update `XTTS_VOICE_SAMPLE` in `config.py` to point to your sample

## 🎮 Usage

### Basic Usage

```bash
cd VoiceAIChat
python voice_chat.py
```

### What Happens

1. **Initialization**: Models load (may take 30-60 seconds)
2. **Listening**: Application waits for speech input
3. **Recording**: Captures audio when speech is detected
4. **Processing**: Transcribes speech and generates response
5. **Playback**: Plays the synthesized speech back to you
6. **Loop**: Returns to listening state

### Exit Options

- **Keyboard**: Press `Ctrl+C`
- **Voice Commands**: Say "exit", "quit", "stop", "goodbye", or "bye"

## ⚙️ Configuration

Edit `config.py` to customize the application:

### Audio Settings
```python
SAMPLE_RATE = 16000        # Audio sample rate (Hz)
RECORD_DURATION = 4        # Recording chunk duration (seconds)
SILENCE_THRESHOLD = 500    # Voice activity detection sensitivity
```

### Model Settings
```python
WHISPER_MODEL_SIZE = "base"    # tiny, base, small, medium, large-v3
WHISPER_DEVICE = "cuda"        # cuda or cpu
XTTS_LANGUAGE = "en"           # Language for synthesis
```

### Voice Cloning
```python
XTTS_VOICE_SAMPLE = "voice_sample.wav"  # Path to voice sample
```

## 🔧 Troubleshooting

### Audio Diagnostics Tool

**NEW**: Run the audio diagnostics tool to test your audio setup:
```bash
python audio_diagnostics.py
```

This tool will:
- Test all available audio devices
- Verify microphone functionality
- Check volume levels and thresholds
- Provide specific troubleshooting guidance
- Save a test recording for verification

### Common Issues

**"Invalid input device" or "No default input device"**
- Run `python audio_diagnostics.py` first
- Check microphone permissions in system settings
- Ensure microphone is not being used by another application
- Try running as administrator (Windows) or with sudo (Linux)

**"PyAudio not found"**
```bash
# Windows
pip install pyaudio

# Linux/Ubuntu
sudo apt install portaudio19-dev
pip install pyaudio

# macOS
brew install portaudio
pip install pyaudio
```

**"No audio device found"**
- Check microphone permissions
- Verify microphone is connected and working
- Try adjusting `SILENCE_THRESHOLD` in config.py

**"Models not loading"**
- Ensure FastWhisper and XTTS environments are properly set up
- Check that model files are downloaded
- Verify CUDA availability for GPU acceleration

**"Audio playback issues"**
- Check speaker/headphone connections
- Verify pygame installation
- Try different audio output devices

### Performance Optimization

**For faster processing:**
- Use smaller Whisper models (`tiny` or `base`)
- Enable GPU acceleration
- Reduce `RECORD_DURATION` for shorter chunks

**For better quality:**
- Use larger Whisper models (`medium` or `large-v3`)
- Increase `SAMPLE_RATE` to 22050 Hz
- Use voice cloning with a good quality sample

## 📊 System Requirements

### Minimum Requirements
- **RAM**: 4GB
- **Storage**: 2GB free space
- **Audio**: Microphone and speakers/headphones
- **Python**: 3.8+

### Recommended Requirements
- **RAM**: 8GB+
- **GPU**: NVIDIA GPU with 4GB+ VRAM
- **Audio**: Good quality microphone
- **Python**: 3.10

## 🎛️ Advanced Usage

### Custom Voice Sample
1. Record a clear 10-30 second audio sample
2. Save as `voice_sample.wav` in the project directory
3. Update `config.py`:
   ```python
   XTTS_VOICE_SAMPLE = "voice_sample.wav"
   ```

### Verbose Mode
Enable detailed logging:
```python
VERBOSE_MODE = True
```

### Different Languages
Change the synthesis language:
```python
XTTS_LANGUAGE = "es"  # Spanish
XTTS_LANGUAGE = "fr"  # French
XTTS_LANGUAGE = "de"  # German
```

## 🔄 Application Flow

```
Start → Initialize Models → Listen for Speech → Record Audio → 
Transcribe → Check for Exit Commands → Synthesize Speech → 
Play Audio → Return to Listen (Loop until exit)
```

## 📁 File Structure

```
VoiceAIChat/
├── voice_chat.py          # Main application
├── audio_recorder.py      # Audio recording functionality
├── speech_processor.py    # STT/TTS processing
├── config.py             # Configuration settings
├── requirements.txt      # Python dependencies
├── README.md            # This file
├── temp_audio/          # Temporary audio files (auto-created)
│   ├── temp_input.wav   # Recorded audio
│   └── temp_output.wav  # Generated speech
└── voice_sample.wav     # Optional voice cloning sample
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is for educational and research purposes. Please ensure compliance with audio processing laws and regulations in your jurisdiction.

## 🙏 Acknowledgments

- **FastWhisper**: Speech-to-text processing
- **XTTS**: Text-to-speech synthesis
- **PyAudio**: Audio input/output
- **Pygame**: Audio playback

---

**Note**: This application processes audio in real-time and requires proper microphone and speaker setup for optimal performance.
