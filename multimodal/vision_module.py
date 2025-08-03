"""
FreelanceX.AI Vision Module
Computer vision capabilities for image analysis and processing
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
import json
import base64
from pathlib import Path

logger = logging.getLogger(__name__)

class VisionModule:
    """
    Vision Module - Computer vision capabilities for image analysis
    Processes images to extract text, objects, faces, and other visual information
    """
    
    def __init__(self):
        self.supported_formats = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff']
        self.max_file_size = 10 * 1024 * 1024  # 10MB
        self.analysis_history = []
        
    async def process_image(self, image_input: Union[str, bytes, Path], analysis_type: str = "full") -> Dict[str, Any]:
        """
        Process and analyze the input image using computer vision techniques.
        
        Args:
            image_input: Input image (file path, bytes, or Path object)
            analysis_type: Type of analysis (full, text_only, objects_only, faces_only)
            
        Returns:
            dict: Dictionary containing analysis results
        """
        try:
            logger.info(f"🖼️ Processing image with analysis type: {analysis_type}")
            
            # Validate and prepare image
            image_data = await self._prepare_image(image_input)
            
            # Perform analysis based on type
            if analysis_type == "text_only":
                results = await self._extract_text(image_data)
            elif analysis_type == "objects_only":
                results = await self._detect_objects(image_data)
            elif analysis_type == "faces_only":
                results = await self._detect_faces(image_data)
            else:
                results = await self._full_analysis(image_data)
            
            # Add metadata
            results['metadata'] = {
                'analysis_type': analysis_type,
                'timestamp': datetime.now().isoformat(),
                'processing_time': 0.5  # Simulated
            }
            
            # Log analysis
            self._log_analysis(image_input, analysis_type, results)
            
            return results
            
        except Exception as e:
            logger.error(f"❌ Image processing failed: {str(e)}")
            return {
                'error': str(e),
                'success': False
            }
    
    async def _prepare_image(self, image_input: Union[str, bytes, Path]) -> Dict[str, Any]:
        """Prepare image for processing"""
        try:
            if isinstance(image_input, str):
                # File path
                path = Path(image_input)
                if not path.exists():
                    raise FileNotFoundError(f"Image file not found: {image_input}")
                
                # Validate file format
                if path.suffix.lower() not in self.supported_formats:
                    raise ValueError(f"Unsupported image format: {path.suffix}")
                
                # Check file size
                if path.stat().st_size > self.max_file_size:
                    raise ValueError(f"Image file too large: {path.stat().st_size} bytes")
                
                return {
                    'type': 'file_path',
                    'path': str(path),
                    'size': path.stat().st_size,
                    'format': path.suffix.lower()
                }
                
            elif isinstance(image_input, bytes):
                # Image bytes
                return {
                    'type': 'bytes',
                    'data': image_input,
                    'size': len(image_input),
                    'format': 'unknown'
                }
                
            elif isinstance(image_input, Path):
                # Path object
                return await self._prepare_image(str(image_input))
                
            else:
                raise ValueError(f"Unsupported image input type: {type(image_input)}")
                
        except Exception as e:
            logger.error(f"❌ Image preparation failed: {str(e)}")
            raise
    
    async def _full_analysis(self, image_data: Dict[str, Any]) -> Dict[str, Any]:
        """Perform full image analysis"""
        try:
            # Simulate processing delay
            await asyncio.sleep(0.5)
            
            # Extract text
            text_results = await self._extract_text(image_data)
            
            # Detect objects
            object_results = await self._detect_objects(image_data)
            
            # Detect faces
            face_results = await self._detect_faces(image_data)
            
            # Analyze sentiment
            sentiment_results = await self._analyze_sentiment(image_data)
            
            # Generate tags
            tag_results = await self._generate_tags(image_data)
            
            # Combine results
            results = {
                'success': True,
                'text': text_results.get('text', ''),
                'objects': object_results.get('objects', []),
                'faces': face_results.get('faces', 0),
                'sentiment': sentiment_results.get('sentiment', 'neutral'),
                'tags': tag_results.get('tags', []),
                'confidence_scores': {
                    'text_extraction': text_results.get('confidence', 0.8),
                    'object_detection': object_results.get('confidence', 0.85),
                    'face_detection': face_results.get('confidence', 0.9),
                    'sentiment_analysis': sentiment_results.get('confidence', 0.75)
                }
            }
            
            return results
            
        except Exception as e:
            logger.error(f"❌ Full analysis failed: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _extract_text(self, image_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract text from image using OCR"""
        try:
            await asyncio.sleep(0.2)
            
            # Simulate OCR results based on image type
            if image_data.get('type') == 'file_path':
                path = image_data.get('path', '')
                if 'document' in path.lower() or 'text' in path.lower():
                    extracted_text = "Sample document text with multiple lines and formatting."
                else:
                    extracted_text = "Sample text extracted from image."
            else:
                extracted_text = "Sample text extracted from image data."
            
            return {
                'success': True,
                'text': extracted_text,
                'confidence': 0.85,
                'text_blocks': [
                    {
                        'text': extracted_text,
                        'bbox': [10, 10, 200, 50],
                        'confidence': 0.85
                    }
                ]
            }
            
        except Exception as e:
            logger.error(f"❌ Text extraction failed: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'text': '',
                'confidence': 0.0
            }
    
    async def _detect_objects(self, image_data: Dict[str, Any]) -> Dict[str, Any]:
        """Detect objects in image"""
        try:
            await asyncio.sleep(0.3)
            
            # Simulate object detection results
            objects = [
                {
                    'name': 'person',
                    'confidence': 0.95,
                    'bbox': [50, 30, 150, 200],
                    'category': 'person'
                },
                {
                    'name': 'laptop',
                    'confidence': 0.88,
                    'bbox': [200, 100, 300, 150],
                    'category': 'electronic'
                },
                {
                    'name': 'chair',
                    'confidence': 0.82,
                    'bbox': [100, 180, 180, 250],
                    'category': 'furniture'
                }
            ]
            
            return {
                'success': True,
                'objects': objects,
                'confidence': 0.88,
                'object_count': len(objects)
            }
            
        except Exception as e:
            logger.error(f"❌ Object detection failed: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'objects': [],
                'confidence': 0.0
            }
    
    async def _detect_faces(self, image_data: Dict[str, Any]) -> Dict[str, Any]:
        """Detect faces in image"""
        try:
            await asyncio.sleep(0.2)
            
            # Simulate face detection results
            faces = [
                {
                    'bbox': [60, 40, 140, 180],
                    'confidence': 0.92,
                    'landmarks': [],
                    'attributes': {
                        'age': '25-35',
                        'gender': 'unknown',
                        'expression': 'neutral'
                    }
                }
            ]
            
            return {
                'success': True,
                'faces': len(faces),
                'face_details': faces,
                'confidence': 0.92
            }
            
        except Exception as e:
            logger.error(f"❌ Face detection failed: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'faces': 0,
                'confidence': 0.0
            }
    
    async def _analyze_sentiment(self, image_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze image sentiment"""
        try:
            await asyncio.sleep(0.1)
            
            # Simulate sentiment analysis
            sentiment = 'positive'
            confidence = 0.75
            
            # Simple sentiment logic based on image content
            if image_data.get('type') == 'file_path':
                path = image_data.get('path', '').lower()
                if 'happy' in path or 'smile' in path:
                    sentiment = 'positive'
                    confidence = 0.85
                elif 'sad' in path or 'angry' in path:
                    sentiment = 'negative'
                    confidence = 0.80
                else:
                    sentiment = 'neutral'
                    confidence = 0.70
            
            return {
                'success': True,
                'sentiment': sentiment,
                'confidence': confidence,
                'sentiment_score': 0.7 if sentiment == 'positive' else -0.3 if sentiment == 'negative' else 0.0
            }
            
        except Exception as e:
            logger.error(f"❌ Sentiment analysis failed: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'sentiment': 'neutral',
                'confidence': 0.0
            }
    
    async def _generate_tags(self, image_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate descriptive tags for image"""
        try:
            await asyncio.sleep(0.1)
            
            # Simulate tag generation
            tags = [
                'indoor',
                'office',
                'professional',
                'technology',
                'modern'
            ]
            
            return {
                'success': True,
                'tags': tags,
                'confidence': 0.80
            }
            
        except Exception as e:
            logger.error(f"❌ Tag generation failed: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'tags': [],
                'confidence': 0.0
            }
    
    def _log_analysis(self, image_input: Union[str, bytes, Path], analysis_type: str, results: Dict[str, Any]):
        """Log image analysis activity"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'analysis_type': analysis_type,
            'success': results.get('success', False),
            'objects_detected': len(results.get('objects', [])),
            'faces_detected': results.get('faces', 0),
            'text_extracted': bool(results.get('text', ''))
        }
        
        self.analysis_history.append(log_entry)
        
        # Keep only last 100 analyses
        if len(self.analysis_history) > 100:
            self.analysis_history = self.analysis_history[-100:]
    
    async def get_analysis_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent analysis history"""
        return self.analysis_history[-limit:]
    
    async def get_analysis_statistics(self) -> Dict[str, Any]:
        """Get analysis statistics"""
        if not self.analysis_history:
            return {'message': 'No analysis history available'}
        
        total_analyses = len(self.analysis_history)
        successful_analyses = len([a for a in self.analysis_history if a.get('success', False)])
        
        return {
            'total_analyses': total_analyses,
            'successful_analyses': successful_analyses,
            'success_rate': (successful_analyses / total_analyses) * 100 if total_analyses > 0 else 0,
            'average_objects_per_image': sum(a.get('objects_detected', 0) for a in self.analysis_history) / total_analyses if total_analyses > 0 else 0,
            'average_faces_per_image': sum(a.get('faces_detected', 0) for a in self.analysis_history) / total_analyses if total_analyses > 0 else 0
        }
    
    async def validate_image(self, image_input: Union[str, bytes, Path]) -> Dict[str, Any]:
        """Validate image before processing"""
        try:
            image_data = await self._prepare_image(image_input)
            
            return {
                'valid': True,
                'format': image_data.get('format'),
                'size': image_data.get('size'),
                'supported': True
            }
            
        except Exception as e:
            return {
                'valid': False,
                'error': str(e),
                'supported': False
            }

# Global instance for easy access
vision_module = VisionModule()

# Backward compatibility function
async def process_image(image):
    """
    Process and analyze the input image using computer vision techniques.
    
    Args:
        image: Input image to be processed (can be path or image object)
        
    Returns:
        dict: Dictionary containing analysis results
    """
    return await vision_module.process_image(image)
