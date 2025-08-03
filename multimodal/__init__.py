"""
FreelanceX.AI Multimodal Package
Multimodal input/output capabilities (vision, voice, etc.)
"""

from .vision_module import VisionModule, vision_module
from .voice_module import VoiceModule, voice_module

__all__ = [
    'VisionModule',
    'vision_module',
    'VoiceModule', 
    'voice_module'
] 