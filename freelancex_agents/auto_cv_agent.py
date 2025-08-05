"""
FreelanceX.AI Auto CV Agent
Specialized agent for automatic CV/resume management and optimization
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import json

from core.agent_manager import BaseAgent

logger = logging.getLogger(__name__)

class AutoCVAgent(BaseAgent):
    """
    Auto CV Agent - Manages and optimizes CV/resume automatically
    Updates CV sections, optimizes content, and generates tailored versions
    """
    
    def __init__(self):
        super().__init__(
            agent_id="auto_cv_agent",
            name="AutoCVAgent",
            description="Manages and optimizes CV/resume automatically"
        )
        self.cv_sections = {
            'personal_info': {},
            'work_experience': [],
            'education': [],
            'skills': [],
            'certifications': [],
            'projects': [],
            'languages': [],
            'interests': []
        }
        self.cv_versions = {}
        self.optimization_history = []
        
    def get_capabilities(self) -> List[str]:
        """Return auto CV agent capabilities"""
        return [
            'cv_management',
            'content_optimization',
            'section_updates',
            'version_control',
            'tailoring',
            'formatting'
        ]
    
    async def process_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process CV related tasks"""
        try:
            content = task_data.get('content', '').lower()
            task_type = task_data.get('task_type', 'general')
            
            if 'update' in content or 'add' in content or 'modify' in content:
                return await self._update_cv_section(task_data)
            elif 'optimize' in content or 'improve' in content:
                return await self._optimize_cv(task_data)
            elif 'generate' in content or 'create' in content:
                return await self._generate_cv_version(task_data)
            elif 'tailor' in content or 'customize' in content:
                return await self._tailor_cv(task_data)
            elif 'format' in content or 'style' in content:
                return await self._format_cv(task_data)
            else:
                return await self._general_cv_assistance(task_data)
                
        except Exception as e:
            logger.error(f"❌ Auto CV agent task processing failed: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _update_cv_section(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update CV section with new information"""
        try:
            content = task_data.get('content', '')
            
            # Extract section and content information
            update_info = self._extract_update_info(content)
            
            if not update_info:
                return {
                    'success': False,
                    'error': 'Could not extract update information from content'
                }
            
            # Update CV section
            success = await self._update_section(update_info)
            
            if success:
                return {
                    'success': True,
                    'task_type': 'cv_update',
                    'section_updated': update_info.get('section'),
                    'update_summary': update_info,
                    'current_cv': self._get_cv_summary()
                }
            else:
                return {
                    'success': False,
                    'error': 'Failed to update CV section'
                }
            
        except Exception as e:
            logger.error(f"❌ CV section update failed: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _optimize_cv(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize CV content and structure"""
        try:
            content = task_data.get('content', '')
            
            # Analyze current CV
            analysis = await self._analyze_cv()
            
            # Generate optimization suggestions
            suggestions = await self._generate_optimization_suggestions(analysis)
            
            # Apply optimizations
            optimizations = await self._apply_optimizations(suggestions)
            
            return {
                'success': True,
                'task_type': 'cv_optimization',
                'analysis': analysis,
                'suggestions': suggestions,
                'optimizations_applied': optimizations,
                'optimization_score': self._calculate_optimization_score()
            }
            
        except Exception as e:
            logger.error(f"❌ CV optimization failed: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _generate_cv_version(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate new CV version"""
        try:
            content = task_data.get('content', '')
            
            # Extract version requirements
            version_info = self._extract_version_info(content)
            
            # Generate version
            version = await self._create_cv_version(version_info)
            
            return {
                'success': True,
                'task_type': 'cv_generation',
                'version_created': version,
                'version_info': version_info,
                'available_versions': list(self.cv_versions.keys())
            }
            
        except Exception as e:
            logger.error(f"❌ CV version generation failed: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _tailor_cv(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Tailor CV for specific job or industry"""
        try:
            content = task_data.get('content', '')
            
            # Extract tailoring requirements
            tailoring_info = self._extract_tailoring_info(content)
            
            # Tailor CV
            tailored_cv = await self._create_tailored_cv(tailoring_info)
            
            return {
                'success': True,
                'task_type': 'cv_tailoring',
                'tailored_cv': tailored_cv,
                'tailoring_info': tailoring_info,
                'tailoring_score': self._calculate_tailoring_score()
            }
            
        except Exception as e:
            logger.error(f"❌ CV tailoring failed: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _format_cv(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Format and style CV"""
        try:
            content = task_data.get('content', '')
            
            # Extract formatting requirements
            format_info = self._extract_format_info(content)
            
            # Apply formatting
            formatted_cv = await self._apply_formatting(format_info)
            
            return {
                'success': True,
                'task_type': 'cv_formatting',
                'formatted_cv': formatted_cv,
                'format_info': format_info,
                'formatting_options': self._get_formatting_options()
            }
            
        except Exception as e:
            logger.error(f"❌ CV formatting failed: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _general_cv_assistance(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Provide general CV assistance"""
        try:
            content = task_data.get('content', '')
            
            # Provide guidance
            guidance = self._generate_cv_guidance(content)
            
            return {
                'success': True,
                'task_type': 'cv_assistance',
                'guidance': guidance,
                'cv_tips': self._get_cv_tips(),
                'cv_best_practices': self._get_cv_best_practices()
            }
            
        except Exception as e:
            logger.error(f"❌ CV assistance failed: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _extract_update_info(self, content: str) -> Optional[Dict[str, Any]]:
        """Extract update information from content"""
        # Simple extraction - in a real implementation, this would use NLP
        sections = list(self.cv_sections.keys())
        
        for section in sections:
            if section.replace('_', ' ') in content.lower():
                return {
                    'section': section,
                    'content': content,
                    'action': 'add' if 'add' in content else 'update'
                }
        
        return None
    
    async def _update_section(self, update_info: Dict[str, Any]) -> bool:
        """Update CV section"""
        try:
            section = update_info.get('section')
            content = update_info.get('content')
            action = update_info.get('action', 'add')
            
            if section not in self.cv_sections:
                logger.error(f"❌ Invalid section: {section}")
                return False
            
            if action == 'add':
                if isinstance(self.cv_sections[section], list):
                    self.cv_sections[section].append({
                        'content': content,
                        'date_added': datetime.now().isoformat()
                    })
                else:
                    self.cv_sections[section].update({
                        'content': content,
                        'date_updated': datetime.now().isoformat()
                    })
            else:
                # Update existing content
                if isinstance(self.cv_sections[section], list):
                    if self.cv_sections[section]:
                        self.cv_sections[section][-1]['content'] = content
                        self.cv_sections[section][-1]['date_updated'] = datetime.now().isoformat()
                else:
                    self.cv_sections[section]['content'] = content
                    self.cv_sections[section]['date_updated'] = datetime.now().isoformat()
            
            logger.info(f"✅ Updated CV section: {section}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Section update failed: {str(e)}")
            return False
    
    async def _analyze_cv(self) -> Dict[str, Any]:
        """Analyze current CV"""
        analysis = {
            'total_sections': len(self.cv_sections),
            'filled_sections': sum(1 for section in self.cv_sections.values() if section),
            'completeness_score': 0,
            'section_analysis': {},
            'overall_assessment': ''
        }
        
        # Analyze each section
        for section_name, section_content in self.cv_sections.items():
            if isinstance(section_content, list):
                analysis['section_analysis'][section_name] = {
                    'type': 'list',
                    'item_count': len(section_content),
                    'completeness': 'complete' if section_content else 'empty'
                }
            else:
                analysis['section_analysis'][section_name] = {
                    'type': 'object',
                    'has_content': bool(section_content),
                    'completeness': 'complete' if section_content else 'empty'
                }
        
        # Calculate completeness score
        filled_sections = analysis['filled_sections']
        total_sections = analysis['total_sections']
        analysis['completeness_score'] = (filled_sections / total_sections) * 100
        
        # Overall assessment
        if analysis['completeness_score'] >= 80:
            analysis['overall_assessment'] = 'Excellent - CV is well-structured and complete'
        elif analysis['completeness_score'] >= 60:
            analysis['overall_assessment'] = 'Good - CV has most essential sections filled'
        elif analysis['completeness_score'] >= 40:
            analysis['overall_assessment'] = 'Fair - CV needs more content in key sections'
        else:
            analysis['overall_assessment'] = 'Poor - CV is missing many essential sections'
        
        return analysis
    
    async def _generate_optimization_suggestions(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate optimization suggestions"""
        suggestions = []
        
        # Completeness suggestions
        if analysis['completeness_score'] < 80:
            suggestions.append({
                'category': 'completeness',
                'priority': 'high',
                'suggestion': 'Fill missing sections to improve CV completeness',
                'action': 'Add content to empty sections'
            })
        
        # Section-specific suggestions
        section_analysis = analysis.get('section_analysis', {})
        
        # Work experience suggestions
        work_exp = section_analysis.get('work_experience', {})
        if work_exp.get('item_count', 0) < 2:
            suggestions.append({
                'category': 'work_experience',
                'priority': 'high',
                'suggestion': 'Add more work experience entries',
                'action': 'Include relevant work history with achievements'
            })
        
        # Skills suggestions
        skills = section_analysis.get('skills', {})
        if skills.get('item_count', 0) < 5:
            suggestions.append({
                'category': 'skills',
                'priority': 'medium',
                'suggestion': 'Expand skills section with relevant technical and soft skills',
                'action': 'Add technical skills, soft skills, and tools'
            })
        
        # Education suggestions
        education = section_analysis.get('education', {})
        if education.get('item_count', 0) < 1:
            suggestions.append({
                'category': 'education',
                'priority': 'high',
                'suggestion': 'Add education information',
                'action': 'Include degree, institution, and graduation date'
            })
        
        return suggestions
    
    async def _apply_optimizations(self, suggestions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Apply optimization suggestions"""
        applied_optimizations = []
        
        for suggestion in suggestions:
            # Simulate optimization application
            applied_optimizations.append({
                'suggestion': suggestion,
                'applied': True,
                'result': f"Applied {suggestion.get('category')} optimization"
            })
        
        # Log optimization
        self._log_optimization(suggestions, applied_optimizations)
        
        return applied_optimizations
    
    def _calculate_optimization_score(self) -> int:
        """Calculate CV optimization score"""
        # Simple scoring based on completeness and content quality
        analysis = asyncio.run(self._analyze_cv())
        base_score = analysis.get('completeness_score', 0)
        
        # Bonus for having key sections
        bonus = 0
        if self.cv_sections.get('work_experience'):
            bonus += 10
        if self.cv_sections.get('skills'):
            bonus += 10
        if self.cv_sections.get('education'):
            bonus += 10
        
        return min(100, base_score + bonus)
    
    def _extract_version_info(self, content: str) -> Dict[str, Any]:
        """Extract version information from content"""
        return {
            'version_name': 'custom_version',
            'format': 'standard',
            'target_industry': 'general',
            'customizations': []
        }
    
    async def _create_cv_version(self, version_info: Dict[str, Any]) -> Dict[str, Any]:
        """Create new CV version"""
        version_name = version_info.get('version_name', f'version_{len(self.cv_versions) + 1}')
        
        # Create version based on current CV
        version = {
            'name': version_name,
            'created_at': datetime.now().isoformat(),
            'base_cv': self.cv_sections.copy(),
            'customizations': version_info.get('customizations', []),
            'format': version_info.get('format', 'standard')
        }
        
        self.cv_versions[version_name] = version
        
        return version
    
    def _extract_tailoring_info(self, content: str) -> Dict[str, Any]:
        """Extract tailoring information from content"""
        return {
            'target_job': 'general',
            'target_industry': 'general',
            'key_requirements': [],
            'tailoring_focus': 'general'
        }
    
    async def _create_tailored_cv(self, tailoring_info: Dict[str, Any]) -> Dict[str, Any]:
        """Create tailored CV version"""
        tailored_cv = self.cv_sections.copy()
        
        # Apply tailoring based on requirements
        target_job = tailoring_info.get('target_job', 'general')
        target_industry = tailoring_info.get('target_industry', 'general')
        
        # Simulate tailoring
        tailored_cv['tailoring_info'] = {
            'target_job': target_job,
            'target_industry': target_industry,
            'tailored_at': datetime.now().isoformat()
        }
        
        return tailored_cv
    
    def _calculate_tailoring_score(self) -> int:
        """Calculate CV tailoring score"""
        # Mock tailoring score
        return 85
    
    def _extract_format_info(self, content: str) -> Dict[str, Any]:
        """Extract formatting information from content"""
        return {
            'style': 'professional',
            'template': 'modern',
            'color_scheme': 'blue',
            'font': 'arial'
        }
    
    async def _apply_formatting(self, format_info: Dict[str, Any]) -> Dict[str, Any]:
        """Apply formatting to CV"""
        formatted_cv = {
            'content': self.cv_sections,
            'formatting': format_info,
            'formatted_at': datetime.now().isoformat()
        }
        
        return formatted_cv
    
    def _get_formatting_options(self) -> List[Dict[str, Any]]:
        """Get available formatting options"""
        return [
            {'style': 'professional', 'description': 'Clean and formal'},
            {'style': 'creative', 'description': 'Modern and artistic'},
            {'style': 'minimalist', 'description': 'Simple and clean'},
            {'style': 'traditional', 'description': 'Classic and conservative'}
        ]
    
    def _generate_cv_guidance(self, content: str) -> str:
        """Generate CV guidance"""
        if 'experience' in content:
            return "Focus on quantifiable achievements and use action verbs to describe your responsibilities."
        elif 'skills' in content:
            return "Include both technical and soft skills, and match them to the job requirements."
        elif 'education' in content:
            return "List your most recent education first and include relevant certifications."
        else:
            return "Keep your CV concise, relevant, and tailored to the specific job you're applying for."
    
    def _get_cv_tips(self) -> List[str]:
        """Get CV writing tips"""
        return [
            "Use action verbs to describe your achievements",
            "Quantify your accomplishments with numbers and percentages",
            "Tailor your CV to each job application",
            "Keep it concise (1-2 pages)",
            "Use a clean, professional format",
            "Proofread carefully for errors",
            "Include relevant keywords from job descriptions"
        ]
    
    def _get_cv_best_practices(self) -> List[str]:
        """Get CV best practices"""
        return [
            "Start with a strong summary or objective",
            "List work experience in reverse chronological order",
            "Focus on achievements rather than just responsibilities",
            "Include relevant skills and certifications",
            "Use consistent formatting throughout",
            "Keep contact information up to date",
            "Customize for each application"
        ]
    
    def _get_cv_summary(self) -> Dict[str, Any]:
        """Get CV summary"""
        return {
            'total_sections': len(self.cv_sections),
            'filled_sections': sum(1 for section in self.cv_sections.values() if section),
            'completeness': f"{sum(1 for section in self.cv_sections.values() if section) / len(self.cv_sections) * 100:.1f}%",
            'last_updated': datetime.now().isoformat()
        }
    
    def _log_optimization(self, suggestions: List[Dict[str, Any]], applied: List[Dict[str, Any]]):
        """Log optimization activity"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'suggestions_count': len(suggestions),
            'applied_count': len(applied),
            'optimization_score': self._calculate_optimization_score()
        }
        
        self.optimization_history.append(log_entry)
        
        # Keep only last 50 optimizations
        if len(self.optimization_history) > 50:
            self.optimization_history = self.optimization_history[-50:]
    
    async def get_cv(self) -> dict:
        """Returns the current CV content"""
        return self.cv_sections
