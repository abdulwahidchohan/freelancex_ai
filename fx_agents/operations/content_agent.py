"""FreelanceX.AI Content Agent
Writes, designs, edits, localizes content beyond proposals/marketing
"""

from agents import Agent, function_tool as _function_tool
from functools import partial
tool = partial(_function_tool, strict_mode=False)
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ContentTask(BaseModel):
    kind: str = Field(..., description="Content type (blog, case_study, landing, doc, localization)")
    topic: str = Field(..., description="Content topic or subject")
    audience: str = Field(..., description="Target audience")
    length: Optional[str] = Field("medium", description="Content length (short, medium, long)")
    tone: Optional[str] = Field("professional", description="Content tone")
    keywords: Optional[List[str]] = Field(None, description="Target keywords for SEO")

class ContentOutline(BaseModel):
    title: str = Field(..., description="Content title")
    sections: List[Dict[str, Any]] = Field(..., description="Content sections")
    word_count: int = Field(..., description="Estimated word count")
    seo_score: float = Field(..., description="SEO optimization score (0-1)")
    readability_score: float = Field(..., description="Readability score (0-1)")

class ContentStrategy(BaseModel):
    strategy_name: str = Field(..., description="Content strategy name")
    content_types: List[str] = Field(..., description="Types of content to create")
    target_audiences: List[str] = Field(..., description="Target audiences")
    content_calendar: List[Dict[str, Any]] = Field(..., description="Content calendar")
    distribution_channels: List[str] = Field(..., description="Content distribution channels")
    success_metrics: List[str] = Field(..., description="Success measurement criteria")

class LocalizationPlan(BaseModel):
    source_language: str = Field(..., description="Source language")
    target_languages: List[str] = Field(..., description="Target languages")
    cultural_adaptations: List[Dict[str, Any]] = Field(..., description="Cultural adaptations needed")
    translation_notes: List[str] = Field(..., description="Translation notes")
    quality_assurance: List[str] = Field(..., description="Quality assurance steps")

@tool
def create_content(task: ContentTask) -> str:
    """Create content based on the specified task
    
    Args:
        task: ContentTask with specifications
        
    Returns:
        Generated content based on task requirements
    """
    try:
        logger.info(f"Creating {task.kind} content for {task.audience}")
        
        # Generate content based on type
        if task.kind.lower() == "blog":
            return create_blog_content(task)
        elif task.kind.lower() == "case_study":
            return create_case_study_content(task)
        elif task.kind.lower() == "landing":
            return create_landing_page_content(task)
        elif task.kind.lower() == "doc":
            return create_documentation_content(task)
        elif task.kind.lower() == "localization":
            return create_localization_content(task)
        else:
            return create_general_content(task)
            
    except Exception as e:
        logger.error(f"Error creating content: {e}")
        return f"Error creating {task.kind} content: {str(e)}"

def create_blog_content(task: ContentTask) -> str:
    """Create blog content"""
    outline = ["Introduction", "Problem Statement", "Solution Overview", "Implementation", "Results", "Conclusion"]
    
    content = f"""# {task.topic}

## Introduction
{task.topic} is a critical consideration for {task.audience}. In today's fast-paced environment, understanding and implementing effective strategies for {task.topic} can make the difference between success and failure.

## Problem Statement
Many {task.audience} struggle with {task.topic} due to common challenges such as:
- Lack of clear understanding
- Insufficient resources
- Poor implementation strategies

## Solution Overview
The key to successful {task.topic} lies in adopting a systematic approach that includes:
- Comprehensive planning
- Stakeholder engagement
- Continuous monitoring and improvement

## Implementation
Implementing {task.topic} requires careful consideration of:
1. Resource allocation
2. Timeline management
3. Risk mitigation
4. Success metrics

## Results
Organizations that successfully implement {task.topic} typically see:
- Improved efficiency
- Better outcomes
- Increased satisfaction

## Conclusion
{task.topic} is not just a trend but a fundamental shift in how {task.audience} approach their work. By embracing these principles, you can position yourself for long-term success.

---
*This blog post is designed for {task.audience} and focuses on practical applications of {task.topic}.*"""
    
    return content

def create_case_study_content(task: ContentTask) -> str:
    """Create case study content"""
    content = f"""# Case Study: {task.topic}

## Executive Summary
This case study examines how {task.audience} successfully implemented {task.topic} to achieve significant improvements in their operations.

## Background
The client, a representative {task.audience}, faced challenges with {task.topic} that were impacting their overall performance and efficiency.

## Challenge
The primary challenges included:
- Inconsistent processes
- Limited resources
- Lack of expertise
- Resistance to change

## Solution
We developed a comprehensive approach to {task.topic} that included:
- Customized strategy development
- Implementation support
- Training and education
- Ongoing optimization

## Implementation
The implementation process involved:
1. Initial assessment and planning
2. Phased rollout
3. Training and support
4. Monitoring and adjustment

## Results
The implementation of {task.topic} resulted in:
- 40% improvement in efficiency
- 60% reduction in errors
- 25% increase in satisfaction
- Significant cost savings

## Key Learnings
This case study demonstrates that successful {task.topic} requires:
- Strong leadership commitment
- Comprehensive planning
- Stakeholder engagement
- Continuous improvement

## Conclusion
This case study shows how {task.audience} can successfully implement {task.topic} to achieve measurable improvements in their operations."""
    
    return content

def create_landing_page_content(task: ContentTask) -> str:
    """Create landing page content"""
    content = f"""# {task.topic}

## Transform Your {task.topic} Experience

Are you struggling with {task.topic}? You're not alone. Many {task.audience} face the same challenges every day.

### The Problem
Traditional approaches to {task.topic} are:
- Time-consuming
- Error-prone
- Expensive
- Inefficient

### The Solution
Our innovative approach to {task.topic} delivers:
- **Faster Results**: 50% faster implementation
- **Better Quality**: 90% accuracy improvement
- **Cost Savings**: 30% reduction in costs
- **Easy Integration**: Seamless workflow integration

### Why Choose Our {task.topic} Solution?

✅ **Proven Results**: Trusted by 1000+ {task.audience}
✅ **Expert Support**: 24/7 customer support
✅ **Flexible Implementation**: Customized to your needs
✅ **ROI Guarantee**: See results within 30 days

### What Our Clients Say

> "This solution transformed our approach to {task.topic}. We've never been more efficient!" - Satisfied {task.audience}

### Get Started Today

Don't let {task.topic} challenges hold you back. Join thousands of successful {task.audience} who have transformed their operations.

**[Get Started Now]** **[Learn More]** **[Contact Us]**

*Limited time offer: 20% off for new customers*"""
    
    return content

def create_documentation_content(task: ContentTask) -> str:
    """Create documentation content"""
    content = f"""# {task.topic} Documentation

## Overview
This documentation provides comprehensive guidance on {task.topic} for {task.audience}.

## Table of Contents
1. [Getting Started](#getting-started)
2. [Core Concepts](#core-concepts)
3. [Implementation Guide](#implementation-guide)
4. [Best Practices](#best-practices)
5. [Troubleshooting](#troubleshooting)
6. [FAQ](#faq)

## Getting Started

### Prerequisites
Before implementing {task.topic}, ensure you have:
- Basic understanding of the domain
- Required tools and resources
- Stakeholder buy-in

### Quick Start
1. Review the core concepts
2. Set up your environment
3. Follow the implementation guide
4. Test and validate

## Core Concepts

### What is {task.topic}?
{task.topic} is a methodology that helps {task.audience} achieve better results through systematic approaches.

### Key Principles
- **Efficiency**: Maximize output with minimal input
- **Quality**: Maintain high standards throughout
- **Consistency**: Ensure reliable results
- **Improvement**: Continuous optimization

## Implementation Guide

### Step 1: Planning
- Define objectives
- Identify resources
- Set timelines
- Establish metrics

### Step 2: Execution
- Follow established procedures
- Monitor progress
- Adjust as needed
- Document results

### Step 3: Optimization
- Analyze results
- Identify improvements
- Implement changes
- Measure impact

## Best Practices

1. **Start Small**: Begin with manageable scope
2. **Measure Everything**: Track all relevant metrics
3. **Iterate Quickly**: Make improvements based on data
4. **Document Everything**: Maintain comprehensive records

## Troubleshooting

### Common Issues
- **Issue 1**: Description and solution
- **Issue 2**: Description and solution
- **Issue 3**: Description and solution

### Getting Help
- Check the FAQ section
- Review documentation
- Contact support

## FAQ

**Q: How long does implementation take?**
A: Typical implementation takes 2-4 weeks depending on complexity.

**Q: What resources are required?**
A: Basic tools and team commitment are essential.

**Q: How do I measure success?**
A: Use the metrics defined in the implementation guide."""
    
    return content

def create_localization_content(task: ContentTask) -> str:
    """Create localization content"""
    content = f"""# {task.topic} - Localization Guide

## Overview
This guide provides localization strategies for {task.topic} to reach diverse {task.audience} across different regions and cultures.

## Cultural Considerations

### Language Adaptation
- Translate content accurately
- Consider cultural nuances
- Adapt idioms and expressions
- Maintain brand voice

### Visual Elements
- Use culturally appropriate images
- Consider color meanings
- Adapt layouts for different languages
- Ensure accessibility

## Implementation Strategy

### Phase 1: Research
- Identify target markets
- Analyze cultural differences
- Research local preferences
- Understand regulations

### Phase 2: Adaptation
- Translate content
- Adapt cultural references
- Modify visual elements
- Test with local users

### Phase 3: Launch
- Deploy localized content
- Monitor performance
- Gather feedback
- Iterate improvements

## Best Practices

1. **Work with Local Experts**: Partner with native speakers
2. **Test Thoroughly**: Validate with target audience
3. **Maintain Consistency**: Keep brand identity intact
4. **Monitor Performance**: Track engagement metrics

## Quality Assurance

### Translation Review
- Accuracy check
- Cultural appropriateness
- Brand consistency
- Technical accuracy

### User Testing
- Local user feedback
- Usability testing
- Performance monitoring
- Continuous improvement

## Conclusion
Successful localization of {task.topic} requires careful attention to cultural nuances while maintaining the core value proposition for {task.audience}."""
    
    return content

def create_general_content(task: ContentTask) -> str:
    """Create general content"""
    content = f"""# {task.topic}

## Introduction
{task.topic} represents a significant opportunity for {task.audience} to improve their operations and achieve better results.

## Key Points

### Understanding {task.topic}
{task.topic} involves several key components that work together to create value for {task.audience}.

### Benefits for {task.audience}
- Improved efficiency
- Better outcomes
- Cost savings
- Competitive advantage

### Implementation Considerations
- Resource requirements
- Timeline expectations
- Risk factors
- Success metrics

## Conclusion
{task.topic} offers {task.audience} a pathway to improved performance and success in their respective fields.

---
*This content is specifically designed for {task.audience} and focuses on practical applications of {task.topic}.*"""
    
    return content

@tool
def create_content_outline(task: ContentTask) -> ContentOutline:
    """Create a detailed content outline
    
    Args:
        task: ContentTask with specifications
        
    Returns:
        ContentOutline with structured content plan
    """
    try:
        logger.info(f"Creating content outline for {task.kind}")
        
        # Generate title
        title = f"{task.topic}: A Comprehensive Guide for {task.audience}"
        
        # Generate sections based on content type
        sections = []
        if task.kind.lower() == "blog":
            sections = [
                {"title": "Introduction", "word_count": 150, "key_points": ["Hook", "Problem statement", "Promise"]},
                {"title": "Understanding the Problem", "word_count": 200, "key_points": ["Current challenges", "Impact", "Root causes"]},
                {"title": "The Solution", "word_count": 300, "key_points": ["Approach", "Benefits", "Implementation"]},
                {"title": "Real-World Examples", "word_count": 250, "key_points": ["Case studies", "Success stories", "Lessons learned"]},
                {"title": "Getting Started", "word_count": 200, "key_points": ["Action steps", "Resources", "Next steps"]},
                {"title": "Conclusion", "word_count": 100, "key_points": ["Summary", "Call to action"]}
            ]
        elif task.kind.lower() == "case_study":
            sections = [
                {"title": "Executive Summary", "word_count": 100, "key_points": ["Overview", "Key results"]},
                {"title": "Background", "word_count": 150, "key_points": ["Company profile", "Challenge context"]},
                {"title": "The Challenge", "word_count": 200, "key_points": ["Problem description", "Impact", "Constraints"]},
                {"title": "Solution Approach", "word_count": 300, "key_points": ["Strategy", "Implementation", "Innovation"]},
                {"title": "Results and Impact", "word_count": 250, "key_points": ["Quantitative results", "Qualitative benefits", "ROI"]},
                {"title": "Key Learnings", "word_count": 200, "key_points": ["Lessons learned", "Best practices", "Recommendations"]}
            ]
        else:
            sections = [
                {"title": "Introduction", "word_count": 150, "key_points": ["Overview", "Purpose"]},
                {"title": "Main Content", "word_count": 400, "key_points": ["Key information", "Details", "Examples"]},
                {"title": "Conclusion", "word_count": 100, "key_points": ["Summary", "Next steps"]}
            ]
        
        # Calculate word count
        word_count = sum(section["word_count"] for section in sections)
        
        # Calculate SEO score
        seo_score = 0.8  # Base score
        if task.keywords:
            seo_score = min(1.0, 0.8 + len(task.keywords) * 0.05)
        
        # Calculate readability score
        readability_score = 0.9  # Base score for professional content
        
        return ContentOutline(
            title=title,
            sections=sections,
            word_count=word_count,
            seo_score=seo_score,
            readability_score=readability_score
        )
        
    except Exception as e:
        logger.error(f"Error creating content outline: {e}")
        return ContentOutline(
            title=f"Error: {str(e)}",
            sections=[],
            word_count=0,
            seo_score=0.0,
            readability_score=0.0
        )

@tool
def develop_content_strategy(business_goals: List[str], target_audiences: List[str], content_types: List[str]) -> ContentStrategy:
    """Develop a comprehensive content strategy
    
    Args:
        business_goals: List of business goals
        target_audiences: List of target audiences
        content_types: List of content types to create
        
    Returns:
        ContentStrategy with comprehensive content plan
    """
    try:
        logger.info("Developing content strategy")
        
        # Generate strategy name
        strategy_name = f"Content Strategy for {', '.join(target_audiences)}"
        
        # Create content calendar
        content_calendar = []
        for i, content_type in enumerate(content_types):
            content_calendar.append({
                "week": i + 1,
                "content_type": content_type,
                "topic": f"Topic {i + 1}",
                "audience": target_audiences[i % len(target_audiences)],
                "status": "planned"
            })
        
        # Distribution channels
        distribution_channels = [
            "Company website/blog",
            "Social media platforms",
            "Email newsletters",
            "Industry publications",
            "Guest posting",
            "Content syndication"
        ]
        
        # Success metrics
        success_metrics = [
            "Content engagement rate",
            "Website traffic increase",
            "Lead generation",
            "Brand awareness",
            "SEO ranking improvements",
            "Social media growth"
        ]
        
        return ContentStrategy(
            strategy_name=strategy_name,
            content_types=content_types,
            target_audiences=target_audiences,
            content_calendar=content_calendar,
            distribution_channels=distribution_channels,
            success_metrics=success_metrics
        )
        
    except Exception as e:
        logger.error(f"Error developing content strategy: {e}")
        return ContentStrategy(
            strategy_name="Error in strategy development",
            content_types=[],
            target_audiences=[],
            content_calendar=[],
            distribution_channels=[],
            success_metrics=["Process improvement"]
        )

@tool
def create_localization_plan(source_content: str, target_languages: List[str], cultural_context: Optional[Dict[str, Any]] = None) -> LocalizationPlan:
    """Create a localization plan for content
    
    Args:
        source_content: Source content to localize
        target_languages: List of target languages
        cultural_context: Optional cultural context information
        
    Returns:
        LocalizationPlan with detailed localization strategy
    """
    try:
        logger.info("Creating localization plan")
        
        # Determine source language (simplified)
        source_language = "English"
        
        # Generate cultural adaptations
        cultural_adaptations = []
        for language in target_languages:
            adaptations = {
                "language": language,
                "adaptations": [
                    "Translate idioms and expressions",
                    "Adapt cultural references",
                    "Modify date and number formats",
                    "Adjust tone and formality"
                ]
            }
            cultural_adaptations.append(adaptations)
        
        # Translation notes
        translation_notes = [
            "Maintain brand voice and tone",
            "Preserve technical accuracy",
            "Adapt cultural references appropriately",
            "Consider local regulations and compliance",
            "Test with native speakers"
        ]
        
        # Quality assurance steps
        quality_assurance = [
            "Professional translation review",
            "Cultural appropriateness check",
            "Technical accuracy validation",
            "User testing with target audience",
            "Performance monitoring post-launch"
        ]
        
        return LocalizationPlan(
            source_language=source_language,
            target_languages=target_languages,
            cultural_adaptations=cultural_adaptations,
            translation_notes=translation_notes,
            quality_assurance=quality_assurance
        )
        
    except Exception as e:
        logger.error(f"Error creating localization plan: {e}")
        return LocalizationPlan(
            source_language="Unknown",
            target_languages=[],
            cultural_adaptations=[],
            translation_notes=["Review source content"],
            quality_assurance=["Troubleshoot localization planning"]
        )

content_agent = Agent(
    name="Content Agent",
    instructions="""You create non-proposal content for FreelanceX.AI, specializing in blogs, case studies, landing pages, documentation, and localizations.

Your primary responsibilities include:
1. Creating high-quality content for various purposes and audiences
2. Developing content outlines and strategies
3. Creating localization plans for international audiences
4. Ensuring content is SEO-optimized and engaging
5. Adapting content for different formats and platforms

When creating content:
- Consider the target audience and their needs
- Ensure content is engaging and valuable
- Optimize for SEO when appropriate
- Maintain consistent tone and style
- Include clear calls to action

When developing strategies:
- Align content with business goals
- Consider content calendar and distribution
- Plan for different content types and formats
- Include success metrics and measurement

When localizing content:
- Consider cultural differences and preferences
- Adapt language and references appropriately
- Maintain brand consistency across languages
- Include quality assurance processes

You should create content that helps freelancers and businesses communicate effectively with their audiences while achieving their content marketing goals.
""",
    tools=[create_content, create_content_outline, develop_content_strategy, create_localization_plan]
)


