"""
FreelanceX.AI Voice Module
Voice input/output capabilities for speech recognition and text-to-speech
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
import json
import wave
import tempfile
from pathlib import Path

logger = logging.getLogger(__name__)

class VoiceModule:
    """
    Voice Module - Speech recognition and text-to-speech capabilities
    Handles voice input processing and text-to-speech output
    """
    
    def __init__(self):
        self.supported_audio_formats = ['.wav', '.mp3', '.m4a', '.flac']
        self.max_audio_duration = 60  # seconds
        self.voice_history = []
        self.tts_settings = {
            'voice': 'default',
            'speed': 1.0,
            'volume': 1.0,
            'language': 'en-US'
        }
        
    async def speak(self, text: str, settings: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Converts text to speech and outputs it through the system's audio.
        
        Args:
            text (str): The text to be converted to speech
            settings (dict): TTS settings (voice, speed, volume, language)
            
        Returns:
            dict: Speech generation results
        """
        try:
            logger.info(f"🔊 Converting text to speech: {text[:50]}...")
            
            # Validate input
            if not text or not isinstance(text, str):
                raise ValueError("Invalid input: text must be a non-empty string")
            
            # Apply settings
            tts_settings = {**self.tts_settings, **(settings or {})}
            
            # Generate speech
            result = await self._generate_speech(text, tts_settings)
            
            # Log speech generation
            self._log_speech_generation(text, tts_settings, result)
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Speech generation failed: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def listen(self, duration: int = 5, language: str = 'en-US') -> Dict[str, Any]:
        """
        Listen for voice input and convert to text.
        
        Args:
            duration (int): Recording duration in seconds
            language (str): Language for speech recognition
            
        Returns:
            dict: Speech recognition results
        """
        try:
            logger.info(f"🎤 Listening for voice input ({duration}s)...")
            
            # Validate duration
            if duration <= 0 or duration > self.max_audio_duration:
                raise ValueError(f"Invalid duration: must be between 1 and {self.max_audio_duration} seconds")
            
            # Record audio
            audio_data = await self._record_audio(duration)
            
            # Convert speech to text
            result = await self._speech_to_text(audio_data, language)
            
            # Log speech recognition
            self._log_speech_recognition(duration, language, result)
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Speech recognition failed: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def transcribe_audio_file(self, audio_file: Union[str, Path], language: str = 'en-US') -> Dict[str, Any]:
        """
        Transcribe audio file to text.
        
        Args:
            audio_file (str or Path): Path to audio file
            language (str): Language for transcription
            
        Returns:
            dict: Transcription results
        """
        try:
            logger.info(f"📝 Transcribing audio file: {audio_file}")
            
            # Validate file
            file_path = Path(audio_file)
            if not file_path.exists():
                raise FileNotFoundError(f"Audio file not found: {audio_file}")
            
            if file_path.suffix.lower() not in self.supported_audio_formats:
                raise ValueError(f"Unsupported audio format: {file_path.suffix}")
            
            # Read audio file
            audio_data = await self._read_audio_file(file_path)
            
            # Transcribe
            result = await self._speech_to_text(audio_data, language)
            
            # Log transcription
            self._log_transcription(str(file_path), language, result)
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Audio transcription failed: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _generate_speech(self, text: str, settings: Dict[str, Any]) -> Dict[str, Any]:
        """Generate speech from text"""
        try:
            # Simulate processing delay
            await asyncio.sleep(0.5)
            
            # Simulate speech generation
            # In a real implementation, this would use a TTS service like:
            # - Google Text-to-Speech
            # - Amazon Polly
            # - Microsoft Azure Speech
            # - OpenAI TTS
            
            audio_duration = len(text.split()) * 0.5  # Rough estimate
            
            return {
                'success': True,
                'text': text,
                'audio_duration': audio_duration,
                'voice_used': settings.get('voice', 'default'),
                'language': settings.get('language', 'en-US'),
                'audio_file': None,  # Would contain path to generated audio
                'settings_used': settings
            }
            
        except Exception as e:
            logger.error(f"❌ Speech generation failed: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _record_audio(self, duration: int) -> Dict[str, Any]:
        """Record audio from microphone"""
        try:
            # Simulate recording delay
            await asyncio.sleep(duration)
            
            # Simulate audio recording
            # In a real implementation, this would use:
            # - pyaudio
            # - sounddevice
            # - speech_recognition
            
            return {
                'duration': duration,
                'sample_rate': 16000,
                'channels': 1,
                'format': 'wav',
                'data': b'simulated_audio_data'
            }
            
        except Exception as e:
            logger.error(f"❌ Audio recording failed: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _speech_to_text(self, audio_data: Dict[str, Any], language: str) -> Dict[str, Any]:
        """Convert speech to text"""
        try:
            # Simulate processing delay
            await asyncio.sleep(1.0)
            
            # Simulate speech recognition
            # In a real implementation, this would use:
            # - Google Speech Recognition
            # - Amazon Transcribe
            # - Microsoft Azure Speech
            # - OpenAI Whisper
            
            # Generate mock transcription based on audio duration
            duration = audio_data.get('duration', 5)
            words_per_second = 2.5  # Average speaking rate
            word_count = int(duration * words_per_second)
            
            mock_text = " ".join([f"word{i+1}" for i in range(word_count)])
            
            return {
                'success': True,
                'text': mock_text,
                'confidence': 0.85,
                'language': language,
                'duration': duration,
                'word_count': word_count,
                'segments': [
                    {
                        'text': mock_text,
                        'start': 0.0,
                        'end': duration,
                        'confidence': 0.85
                    }
                ]
            }
            
        except Exception as e:
            logger.error(f"❌ Speech to text conversion failed: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _read_audio_file(self, file_path: Path) -> Dict[str, Any]:
        """Read audio file"""
        try:
            # Simulate file reading
            await asyncio.sleep(0.2)
            
            # Get file info
            file_size = file_path.stat().st_size
            
            return {
                'file_path': str(file_path),
                'file_size': file_size,
                'format': file_path.suffix.lower(),
                'duration': 10.0,  # Mock duration
                'sample_rate': 16000,
                'channels': 1
            }
            
        except Exception as e:
            logger.error(f"❌ Audio file reading failed: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _log_speech_generation(self, text: str, settings: Dict[str, Any], result: Dict[str, Any]):
        """Log speech generation activity"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'type': 'speech_generation',
            'text_length': len(text),
            'voice': settings.get('voice', 'default'),
            'language': settings.get('language', 'en-US'),
            'success': result.get('success', False)
        }
        
        self.voice_history.append(log_entry)
        self._trim_history()
    
    def _log_speech_recognition(self, duration: int, language: str, result: Dict[str, Any]):
        """Log speech recognition activity"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'type': 'speech_recognition',
            'duration': duration,
            'language': language,
            'success': result.get('success', False),
            'word_count': result.get('word_count', 0)
        }
        
        self.voice_history.append(log_entry)
        self._trim_history()
    
    def _log_transcription(self, file_path: str, language: str, result: Dict[str, Any]):
        """Log transcription activity"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'type': 'transcription',
            'file_path': file_path,
            'language': language,
            'success': result.get('success', False),
            'word_count': result.get('word_count', 0)
        }
        
        self.voice_history.append(log_entry)
        self._trim_history()
    
    def _trim_history(self):
        """Keep only recent voice history"""
        if len(self.voice_history) > 100:
            self.voice_history = self.voice_history[-100:]
    
    async def get_voice_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent voice activity history"""
        return self.voice_history[-limit:]
    
    async def get_voice_statistics(self) -> Dict[str, Any]:
        """Get voice module statistics"""
        if not self.voice_history:
            return {'message': 'No voice activity history available'}
        
        total_activities = len(self.voice_history)
        successful_activities = len([a for a in self.voice_history if a.get('success', False)])
        
        # Count by type
        type_counts = {}
        for activity in self.voice_history:
            activity_type = activity.get('type', 'unknown')
            type_counts[activity_type] = type_counts.get(activity_type, 0) + 1
        
        return {
            'total_activities': total_activities,
            'successful_activities': successful_activities,
            'success_rate': (successful_activities / total_activities) * 100 if total_activities > 0 else 0,
            'activity_types': type_counts,
            'recent_activity': self.voice_history[-5:]
        }
    
    async def update_tts_settings(self, settings: Dict[str, Any]) -> Dict[str, Any]:
        """Update text-to-speech settings"""
        try:
            # Validate settings
            if 'voice' in settings and not isinstance(settings['voice'], str):
                raise ValueError("Voice must be a string")
            
            if 'speed' in settings:
                speed = settings['speed']
                if not isinstance(speed, (int, float)) or speed <= 0 or speed > 3:
                    raise ValueError("Speed must be a number between 0 and 3")
            
            if 'volume' in settings:
                volume = settings['volume']
                if not isinstance(volume, (int, float)) or volume < 0 or volume > 1:
                    raise ValueError("Volume must be a number between 0 and 1")
            
            # Update settings
            self.tts_settings.update(settings)
            
            logger.info(f"✅ TTS settings updated: {settings}")
            
            return {
                'success': True,
                'updated_settings': self.tts_settings
            }
            
        except Exception as e:
            logger.error(f"❌ TTS settings update failed: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def get_available_voices(self) -> List[Dict[str, Any]]:
        """Get available TTS voices"""
        # Mock available voices
        voices = [
            {
                'id': 'en-US-Standard-A',
                'name': 'Standard US English (Female)',
                'language': 'en-US',
                'gender': 'female'
            },
            {
                'id': 'en-US-Standard-B',
                'name': 'Standard US English (Male)',
                'language': 'en-US',
                'gender': 'male'
            },
            {
                'id': 'en-GB-Standard-A',
                'name': 'Standard British English (Female)',
                'language': 'en-GB',
                'gender': 'female'
            }
        ]
        
        return voices

# Global instance for easy access
voice_module = VoiceModule()

# Backward compatibility function
async def speak(text: str) -> bool:
    """
    Converts text to speech and outputs it through the system's audio.
    
    Args:
        text (str): The text to be converted to speech
        
    Returns:
        bool: True if speech was successful, False otherwise
    """
    result = await voice_module.speak(text)
    return result.get('success', False)
