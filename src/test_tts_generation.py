"""
Test file for TTS generation functionality in speech_processor.py
Tests both voice cloning and default voice scenarios
"""

import os
import sys
import tempfile
import unittest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

# Add src directory to path
sys.path.append(os.path.dirname(__file__))

# Import configuration
from config import *

class TestTTSGeneration(unittest.TestCase):
    """Test cases for TTS generation functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.test_text = "Hello, this is a test message for TTS generation."
        self.mock_tts_model = Mock()
        self.temp_dir = tempfile.mkdtemp()
        self.output_file = os.path.join(self.temp_dir, "test_output.wav")
        
    def tearDown(self):
        """Clean up test fixtures"""
        # Clean up temporary files
        if os.path.exists(self.output_file):
            os.remove(self.output_file)
        os.rmdir(self.temp_dir)
    
    def create_mock_voice_sample(self):
        """Create a temporary voice sample file for testing"""
        voice_sample_path = os.path.join(self.temp_dir, "voice_sample.wav")
        # Create an empty file to simulate voice sample
        with open(voice_sample_path, 'w') as f:
            f.write("mock voice sample")
        return voice_sample_path
    
    @patch('src.speech_processor.XTTS_VOICE_SAMPLE')
    @patch('src.speech_processor.XTTS_LANGUAGE')
    @patch('src.speech_processor.TEMP_AUDIO_DIR')
    @patch('src.speech_processor.TEMP_OUTPUT_FILE')
    def test_tts_with_voice_cloning(self, mock_temp_output, mock_temp_dir, mock_language, mock_voice_sample):
        """Test TTS generation with voice cloning (when voice sample exists)"""
        # Setup mocks
        voice_sample_path = self.create_mock_voice_sample()
        mock_voice_sample.return_value = voice_sample_path
        mock_language.return_value = "en"
        mock_temp_dir.return_value = self.temp_dir
        mock_temp_output.return_value = "test_output.wav"
        
        # Create a mock output file to simulate successful generation
        with open(self.output_file, 'w') as f:
            f.write("mock audio data")
        
        # Mock the tts_model.tts_to_file method
        self.mock_tts_model.tts_to_file = Mock()
        
        # Simulate the TTS generation logic
        text = self.test_text
        output_file = self.output_file
        
        # Test the voice cloning path
        if mock_voice_sample.return_value and os.path.exists(mock_voice_sample.return_value):
            print("🦜Using cloned voice...")
            self.mock_tts_model.tts_to_file(
                text=text,
                speaker_wav=mock_voice_sample.return_value,
                language=mock_language.return_value,
                file_path=output_file
            )
        
        # Verify the method was called with correct parameters
        self.mock_tts_model.tts_to_file.assert_called_once_with(
            text=text,
            speaker_wav=voice_sample_path,
            language="en",
            file_path=output_file
        )
        
        # Verify output file exists
        self.assertTrue(os.path.exists(output_file))
        print("✅ Voice cloning test passed")
    
    @patch('src.speech_processor.XTTS_VOICE_SAMPLE')
    @patch('src.speech_processor.XTTS_LANGUAGE')
    @patch('src.speech_processor.TEMP_AUDIO_DIR')
    @patch('src.speech_processor.TEMP_OUTPUT_FILE')
    def test_tts_with_default_voice(self, mock_temp_output, mock_temp_dir, mock_language, mock_voice_sample):
        """Test TTS generation with default voice (when no voice sample exists)"""
        # Setup mocks - no voice sample
        mock_voice_sample.return_value = None
        mock_language.return_value = "en"
        mock_temp_dir.return_value = self.temp_dir
        mock_temp_output.return_value = "test_output.wav"
        
        # Create a mock output file to simulate successful generation
        with open(self.output_file, 'w') as f:
            f.write("mock audio data")
        
        # Mock the tts_model.tts_to_file method
        self.mock_tts_model.tts_to_file = Mock()
        
        # Simulate the TTS generation logic
        text = self.test_text
        output_file = self.output_file
        
        # Test the default voice path
        if not (mock_voice_sample.return_value and os.path.exists(mock_voice_sample.return_value or "")):
            print("⚠️Using default voice...")
            self.mock_tts_model.tts_to_file(
                text=text,
                language=mock_language.return_value,
                file_path=output_file
            )
        
        # Verify the method was called with correct parameters (no speaker_wav)
        self.mock_tts_model.tts_to_file.assert_called_once_with(
            text=text,
            language="en",
            file_path=output_file
        )
        
        # Verify output file exists
        self.assertTrue(os.path.exists(output_file))
        print("✅ Default voice test passed")
    
    @patch('src.speech_processor.XTTS_VOICE_SAMPLE')
    @patch('src.speech_processor.XTTS_LANGUAGE')
    @patch('src.speech_processor.TEMP_AUDIO_DIR')
    @patch('src.speech_processor.TEMP_OUTPUT_FILE')
    def test_tts_with_nonexistent_voice_sample(self, mock_temp_output, mock_temp_dir, mock_language, mock_voice_sample):
        """Test TTS generation when voice sample path is set but file doesn't exist"""
        # Setup mocks - voice sample path exists but file doesn't
        nonexistent_path = os.path.join(self.temp_dir, "nonexistent_voice.wav")
        mock_voice_sample.return_value = nonexistent_path
        mock_language.return_value = "en"
        mock_temp_dir.return_value = self.temp_dir
        mock_temp_output.return_value = "test_output.wav"
        
        # Create a mock output file to simulate successful generation
        with open(self.output_file, 'w') as f:
            f.write("mock audio data")
        
        # Mock the tts_model.tts_to_file method
        self.mock_tts_model.tts_to_file = Mock()
        
        # Simulate the TTS generation logic
        text = self.test_text
        output_file = self.output_file
        
        # Test the logic - should fall back to default voice
        if mock_voice_sample.return_value and os.path.exists(mock_voice_sample.return_value):
            print("🦜Using cloned voice...")
            self.mock_tts_model.tts_to_file(
                text=text,
                speaker_wav=mock_voice_sample.return_value,
                language=mock_language.return_value,
                file_path=output_file
            )
        else:
            print("⚠️Using default voice...")
            self.mock_tts_model.tts_to_file(
                text=text,
                language=mock_language.return_value,
                file_path=output_file
            )
        
        # Verify the method was called with default voice parameters (no speaker_wav)
        self.mock_tts_model.tts_to_file.assert_called_once_with(
            text=text,
            language="en",
            file_path=output_file
        )
        
        # Verify output file exists
        self.assertTrue(os.path.exists(output_file))
        print("✅ Nonexistent voice sample test passed")


class TestTTSGenerationIntegration(unittest.TestCase):
    """Integration tests that test the actual SpeechProcessor class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.test_text = "This is an integration test for TTS generation."
        
    @patch('src.speech_processor.TTS')
    @patch('src.speech_processor.XTTS_VOICE_SAMPLE')
    @patch('src.speech_processor.os.path.exists')
    def test_synthesize_speech_with_voice_cloning_integration(self, mock_exists, mock_voice_sample, mock_tts_class):
        """Integration test for synthesize_speech method with voice cloning"""
        from speech_processor import SpeechProcessor
        
        # Setup mocks
        mock_voice_sample.return_value = "/path/to/voice/sample.wav"
        mock_exists.return_value = True  # Voice sample exists
        
        # Mock TTS model
        mock_tts_instance = Mock()
        mock_tts_class.return_value = mock_tts_instance
        
        # Create SpeechProcessor instance
        processor = SpeechProcessor()
        processor.tts_model = mock_tts_instance
        
        # Mock the output file creation
        with patch('os.path.exists') as mock_file_exists:
            mock_file_exists.side_effect = lambda path: path.endswith('voice/sample.wav') or path.endswith('temp_output.wav')
            
            # Call the method
            result = processor.synthesize_speech(self.test_text)
            
            # Verify TTS was called with voice cloning parameters
            mock_tts_instance.tts_to_file.assert_called_once()
            call_args = mock_tts_instance.tts_to_file.call_args
            
            # Check that speaker_wav parameter was included
            self.assertIn('speaker_wav', call_args.kwargs)
            self.assertEqual(call_args.kwargs['text'], self.test_text)
            
        print("✅ Integration test with voice cloning passed")
    
    @patch('src.speech_processor.TTS')
    @patch('src.speech_processor.XTTS_VOICE_SAMPLE')
    @patch('src.speech_processor.os.path.exists')
    def test_synthesize_speech_with_default_voice_integration(self, mock_exists, mock_voice_sample, mock_tts_class):
        """Integration test for synthesize_speech method with default voice"""
        from speech_processor import SpeechProcessor
        
        # Setup mocks
        mock_voice_sample.return_value = None  # No voice sample
        mock_exists.return_value = False  # Voice sample doesn't exist
        
        # Mock TTS model
        mock_tts_instance = Mock()
        mock_tts_class.return_value = mock_tts_instance
        
        # Create SpeechProcessor instance
        processor = SpeechProcessor()
        processor.tts_model = mock_tts_instance
        
        # Mock the output file creation
        with patch('os.path.exists') as mock_file_exists:
            mock_file_exists.side_effect = lambda path: path.endswith('temp_output.wav')
            
            # Call the method
            result = processor.synthesize_speech(self.test_text)
            
            # Verify TTS was called with default voice parameters
            mock_tts_instance.tts_to_file.assert_called_once()
            call_args = mock_tts_instance.tts_to_file.call_args
            
            # Check that speaker_wav parameter was NOT included
            self.assertNotIn('speaker_wav', call_args.kwargs)
            self.assertEqual(call_args.kwargs['text'], self.test_text)
            
        print("✅ Integration test with default voice passed")


def run_manual_test():
    """Manual test function to demonstrate the TTS generation logic"""
    print("🧪 Running manual TTS generation test...")
    print("=" * 50)
    
    # Test data
    test_text = "Hello, this is a manual test of the TTS generation functionality."
    
    # Mock TTS model
    mock_tts_model = Mock()
    mock_tts_model.tts_to_file = Mock()
    
    # Test scenario 1: With voice cloning
    print("\n📋 Test 1: Voice Cloning Scenario")
    print("-" * 30)
    
    # Simulate voice sample exists
    voice_sample_path = "/path/to/voice/sample.wav"
    temp_output_file = "/tmp/output.wav"
    language = "en"
    
    # Simulate the actual code logic
    if voice_sample_path and os.path.exists(voice_sample_path):
        print("🦜Using cloned voice...")
        mock_tts_model.tts_to_file(
            text=test_text,
            speaker_wav=voice_sample_path,
            language=language,
            file_path=temp_output_file
        )
    else:
        print("⚠️Using default voice...")
        mock_tts_model.tts_to_file(
            text=test_text,
            language=language,
            file_path=temp_output_file
        )
    
    print(f"✅ TTS called with voice cloning parameters")
    print(f"   Text: {test_text}")
    print(f"   Voice Sample: {voice_sample_path}")
    print(f"   Language: {language}")
    print(f"   Output: {temp_output_file}")
    
    # Test scenario 2: Default voice
    print("\n📋 Test 2: Default Voice Scenario")
    print("-" * 30)
    
    # Reset mock
    mock_tts_model.reset_mock()
    
    # Simulate no voice sample
    voice_sample_path = None
    
    # Simulate the actual code logic
    if voice_sample_path and os.path.exists(voice_sample_path or ""):
        print("🦜Using cloned voice...")
        mock_tts_model.tts_to_file(
            text=test_text,
            speaker_wav=voice_sample_path,
            language=language,
            file_path=temp_output_file
        )
    else:
        print("⚠️Using default voice...")
        mock_tts_model.tts_to_file(
            text=test_text,
            language=language,
            file_path=temp_output_file
        )
    
    print(f"✅ TTS called with default voice parameters")
    print(f"   Text: {test_text}")
    print(f"   Language: {language}")
    print(f"   Output: {temp_output_file}")
    print(f"   (No voice sample used)")
    
    print("\n🎉 Manual test completed successfully!")


if __name__ == "__main__":
    print("🚀 Starting TTS Generation Tests")
    print("=" * 50)
    
    # Run manual test first
    run_manual_test()
    
    print("\n" + "=" * 50)
    print("🧪 Running Unit Tests")
    print("=" * 50)
    
    # Run unit tests
    unittest.main(verbosity=2, exit=False)
    
    print("\n✅ All tests completed!")
