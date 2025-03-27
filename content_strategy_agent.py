from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field
import json
import os
from datetime import datetime
import openai
import asyncio

class VideoData(BaseModel):
    """Data structure for viral video information"""
    title: str
    description: Optional[str] = None
    views: int
    publishedAt: str
    channel: Optional[str] = None

class ContentAnalysisRequest(BaseModel):
    """Request structure for content analysis"""
    videos: List[VideoData]
    analysis_type: str = "full"  # Options: "full", "hooks", "format", "engagement", "themes"

class ContentAnalysisResult(BaseModel):
    """Result structure for content analysis"""
    hook_patterns: List[Dict[str, str]]
    format_trends: List[str]
    engagement_tactics: List[str]
    content_themes: List[str]
    summary: str

class ContentStrategyAgent:
    """AI Agent for analyzing viral short-form video content"""
    
    def __init__(self, model_name: str = "gpt-4"):
        # Set up OpenAI client
        openai.api_key = os.environ.get("OPENAI_API_KEY")
        if not openai.api_key:
            print("Warning: OPENAI_API_KEY not found in environment variables. GPT analysis will fail.")
        
        self.model_name = model_name
    
    async def process_request(self, request: ContentAnalysisRequest) -> Dict[str, Any]:
        """Process an analysis request and return structured results"""
        result = await self.analyze_videos(request.videos, request.analysis_type)
        return {
            "hook_patterns": result.hook_patterns,
            "format_trends": result.format_trends,
            "engagement_tactics": result.engagement_tactics,
            "content_themes": result.content_themes,
            "summary": result.summary
        }
    
    async def analyze_videos(self, videos: List[VideoData], analysis_type: str = "full") -> ContentAnalysisResult:
        """Analyze a list of viral videos and extract insights using GPT"""
        try:
            if analysis_type == "full" or analysis_type == "all":
                # For full analysis, we'll run all the specialized analyses
                hook_patterns = await self._analyze_hooks_with_gpt(videos)
                format_trends = await self._analyze_format_with_gpt(videos)
                engagement_tactics = await self._analyze_engagement_with_gpt(videos)
                content_themes = await self._analyze_themes_with_gpt(videos)
                summary = await self._generate_summary_with_gpt(videos, hook_patterns, format_trends, engagement_tactics, content_themes)
            else:
                # Initialize with empty lists
                hook_patterns, format_trends, engagement_tactics, content_themes = [], [], [], []
                
                # Only run the requested analysis
                if analysis_type == "hooks":
                    hook_patterns = await self._analyze_hooks_with_gpt(videos)
                elif analysis_type == "format":
                    format_trends = await self._analyze_format_with_gpt(videos)
                elif analysis_type == "engagement":
                    engagement_tactics = await self._analyze_engagement_with_gpt(videos)
                elif analysis_type == "themes":
                    content_themes = await self._analyze_themes_with_gpt(videos)
                
                # Generate a summary based on the partial analysis
                summary = await self._generate_summary_with_gpt(videos, hook_patterns, format_trends, engagement_tactics, content_themes)
            
            # Return the analysis result
            return ContentAnalysisResult(
                hook_patterns=hook_patterns,
                format_trends=format_trends,
                engagement_tactics=engagement_tactics,
                content_themes=content_themes,
                summary=summary
            )
            
        except Exception as e:
            # Handle errors gracefully
            print(f"Error analyzing videos: {str(e)}")
            # Fall back to the template-based approach if GPT fails
            hook_patterns = self._analyze_hooks(videos)
            format_trends = self._analyze_format(videos)
            engagement_tactics = self._analyze_engagement(videos)
            content_themes = self._analyze_themes(videos)
            summary = self._generate_summary(videos, hook_patterns, format_trends, engagement_tactics, content_themes)
            
            return ContentAnalysisResult(
                hook_patterns=hook_patterns,
                format_trends=format_trends,
                engagement_tactics=engagement_tactics,
                content_themes=content_themes,
                summary=summary
            )
    
    async def _generate_with_gpt(self, prompt: str, max_tokens: int = 300) -> str:
        """Generate content using GPT"""
        try:
            response = await asyncio.to_thread(
                openai.ChatCompletion.create,
                model=self.model_name,
                messages=[{"role": "system", "content": "You are an expert content strategist specializing in viral short-form video analysis."},
                          {"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=0.7
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Error generating content with GPT: {str(e)}")
            return None
    
    async def _analyze_hooks_with_gpt(self, videos: List[VideoData]) -> List[Dict[str, str]]:
        """Analyze hook patterns in the videos using GPT"""
        # Format the videos for the prompt
        video_data = []
        for v in videos:
            video_data.append(f"Title: {v.title}\nDescription: {v.description or 'N/A'}\nViews: {v.views:,}\nChannel: {v.channel or 'Unknown'}")
        
        video_text = "\n\n".join(video_data)
        
        prompt = f"""Analyze these viral short-form videos and identify common hook patterns:

{video_text}

Identify 3-5 specific hook patterns used in these videos.
For each pattern:
1. Provide a descriptive name (e.g., "question-based", "shock-based", "number-based")
2. Include a concrete example from the videos

Output in JSON format like this:
[
  {{"type": "hook_type", "example": "example from data"}},
  ...
]"""

        # Try to generate with GPT
        try:
            result = await self._generate_with_gpt(prompt, max_tokens=300)
            if result:
                # Parse the JSON response
                hook_patterns = json.loads(result)
                return hook_patterns
        except Exception as e:
            print(f"Error parsing GPT hook patterns: {str(e)}")
        
        # Fall back to template approach if GPT fails
        return self._analyze_hooks(videos)
    
    async def _analyze_format_with_gpt(self, videos: List[VideoData]) -> List[str]:
        """Analyze format trends in the videos using GPT"""
        # Format the videos for the prompt
        video_data = []
        for v in videos:
            video_data.append(f"Title: {v.title}\nDescription: {v.description or 'N/A'}\nViews: {v.views:,}\nChannel: {v.channel or 'Unknown'}")
        
        video_text = "\n\n".join(video_data)
        
        prompt = f"""Analyze these viral short-form videos and identify format trends:

{video_text}

Identify 4-6 format trends based on these videos. Format trends include:
- Structure patterns (like "Hook → Problem → Solution → CTA")
- Editing styles
- Visual techniques
- Pacing patterns

Focus on actionable insights that could be used to create similar content.
Output as a JSON array of strings:
["Trend 1", "Trend 2", ...]"""

        # Try to generate with GPT
        try:
            result = await self._generate_with_gpt(prompt, max_tokens=300)
            if result:
                # Parse the JSON response
                format_trends = json.loads(result)
                return format_trends
        except Exception as e:
            print(f"Error parsing GPT format trends: {str(e)}")
        
        # Fall back to template approach if GPT fails
        return self._analyze_format(videos)
    
    async def _analyze_engagement_with_gpt(self, videos: List[VideoData]) -> List[str]:
        """Analyze engagement tactics in the videos using GPT"""
        # Format the videos for the prompt
        video_data = []
        for v in videos:
            video_data.append(f"Title: {v.title}\nDescription: {v.description or 'N/A'}\nViews: {v.views:,}\nChannel: {v.channel or 'Unknown'}")
        
        video_text = "\n\n".join(video_data)
        
        prompt = f"""Analyze these viral short-form videos and identify engagement tactics:

{video_text}

Identify 4-6 specific engagement tactics used in these videos. Engagement tactics include:
- Call-to-action techniques
- Audience interaction methods
- Psychological tactics (e.g., curiosity gaps, open loops)
- Community building approaches

Focus on actionable insights that could be used to create similar content.
Output as a JSON array of strings:
["Tactic 1", "Tactic 2", ...]"""

        # Try to generate with GPT
        try:
            result = await self._generate_with_gpt(prompt, max_tokens=300)
            if result:
                # Parse the JSON response
                engagement_tactics = json.loads(result)
                return engagement_tactics
        except Exception as e:
            print(f"Error parsing GPT engagement tactics: {str(e)}")
        
        # Fall back to template approach if GPT fails
        return self._analyze_engagement(videos)
    
    async def _analyze_themes_with_gpt(self, videos: List[VideoData]) -> List[str]:
        """Analyze content themes in the videos using GPT"""
        # Format the videos for the prompt
        video_data = []
        for v in videos:
            video_data.append(f"Title: {v.title}\nDescription: {v.description or 'N/A'}\nViews: {v.views:,}\nChannel: {v.channel or 'Unknown'}")
        
        video_text = "\n\n".join(video_data)
        
        prompt = f"""Analyze these viral short-form videos and identify content themes:

{video_text}

Identify 4-6 content themes from these videos. Look for:
- Subject matter patterns
- Value proposition types (e.g., time-saving, problem-solving)
- Common topics or categories
- Emotional appeals

Focus on themes that could guide new content creation.
Output as a JSON array of strings:
["Theme 1", "Theme 2", ...]"""

        # Try to generate with GPT
        try:
            result = await self._generate_with_gpt(prompt, max_tokens=300)
            if result:
                # Parse the JSON response
                content_themes = json.loads(result)
                return content_themes
        except Exception as e:
            print(f"Error parsing GPT content themes: {str(e)}")
        
        # Fall back to template approach if GPT fails
        return self._analyze_themes(videos)
    
    async def _generate_summary_with_gpt(self, videos: List[VideoData], hook_patterns: List[Dict[str, str]], 
                                  format_trends: List[str], engagement_tactics: List[str], 
                                  content_themes: List[str]) -> str:
        """Generate a summary of the analysis using GPT"""
        # Calculate average views
        avg_views = sum(v.views for v in videos) / len(videos) if videos else 0
        
        # Format the analysis components
        hook_types = [h['type'] for h in hook_patterns] if hook_patterns else []
        
        prompt = f"""Create a concise summary of viral short-form video trends based on this analysis:

Average Views: {avg_views:,.0f}

Hook Patterns: {', '.join(hook_types) if hook_types else 'N/A'}

Format Trends: {', '.join(format_trends) if format_trends else 'N/A'}

Engagement Tactics: {', '.join(engagement_tactics) if engagement_tactics else 'N/A'}

Content Themes: {', '.join(content_themes) if content_themes else 'N/A'}

Write a concise, action-oriented summary (3-5 sentences) that synthesizes these insights into practical guidance for creating viral short-form videos.
Focus on what makes these videos successful and how to replicate their success.
"""

        # Try to generate with GPT
        try:
            summary = await self._generate_with_gpt(prompt, max_tokens=200)
            if summary:
                return summary
        except Exception as e:
            print(f"Error generating GPT summary: {str(e)}")
        
        # Fall back to template approach if GPT fails
        return self._generate_summary(videos, hook_patterns, format_trends, engagement_tactics, content_themes)
    
    # Keep the original template-based methods as fallbacks
    def _analyze_hooks(self, videos: List[VideoData]) -> List[Dict[str, str]]:
        """Analyze hook patterns in the videos"""
        hook_patterns = []
        
        # Look for question-based hooks
        question_hooks = [v for v in videos if v.title.endswith('?') or 
                         (v.description and '?' in v.description.split('.')[0])]
        if question_hooks:
            sample = question_hooks[0].title
            hook_patterns.append({"type": "question-based", "example": sample})
        
        # Look for shock/surprise hooks
        shock_words = ["wrong", "mistake", "shocking", "never", "secret"]
        shock_hooks = [v for v in videos if any(word in v.title.lower() for word in shock_words)]
        if shock_hooks:
            sample = shock_hooks[0].title
            hook_patterns.append({"type": "shock-based", "example": sample})
        
        # Look for number-based hooks
        number_hooks = [v for v in videos if any(str(i) in v.title for i in range(1, 11))]
        if number_hooks:
            sample = number_hooks[0].title
            hook_patterns.append({"type": "number-based", "example": sample})
        
        # Look for personal story hooks
        story_hooks = [v for v in videos if "I" in v.title.split() or 
                      (v.description and "I" in v.description.split()[:5])]
        if story_hooks:
            sample = story_hooks[0].title
            hook_patterns.append({"type": "personal-story", "example": sample})
        
        return hook_patterns
    
    def _analyze_format(self, videos: List[VideoData]) -> List[str]:
        """Analyze format trends in the videos"""
        format_trends = []
        
        # Analyze titles for format clues
        has_numbers = any(any(c.isdigit() for c in v.title) for v in videos)
        if has_numbers:
            format_trends.append("List-based format (e.g., '5 tips', '3 mistakes')")
        
        # Look for how-to content
        how_to = any("how to" in v.title.lower() or 
                   (v.description and "how to" in v.description.lower()) 
                   for v in videos)
        if how_to:
            format_trends.append("Tutorial/How-to format with step-by-step instructions")
        
        # Look for before/after or transformation content
        transformation = any("before" in v.title.lower() and "after" in v.title.lower() or
                           (v.description and "before" in v.description.lower() and "after" in v.description.lower())
                           for v in videos)
        if transformation:
            format_trends.append("Before/After transformation format")
        
        # Common structure based on popular short-form videos
        format_trends.append("Hook (0-3s) → Problem/Pain Point (3-8s) → Solution/Value (8-20s) → CTA (last 5s)")
        format_trends.append("Fast-paced editing with text overlays and background music")
        
        return format_trends
    
    def _analyze_engagement(self, videos: List[VideoData]) -> List[str]:
        """Analyze engagement tactics in the videos"""
        engagement_tactics = []
        
        # Look for direct questions to viewers
        questions = any("?" in v.title or (v.description and "?" in v.description) for v in videos)
        if questions:
            engagement_tactics.append("Direct questions to viewers to encourage comments")
        
        # Look for calls to action
        cta_words = ["follow", "subscribe", "like", "comment", "share"]
        cta = any(any(word in v.description.lower() if v.description else False for word in cta_words) for v in videos)
        if cta:
            engagement_tactics.append("Explicit calls-to-action (follow, like, comment)")
        
        # Common engagement tactics in viral videos
        engagement_tactics.append("Open loops (creating curiosity gaps that keep viewers watching)")
        engagement_tactics.append("Relatable scenarios that prompt viewers to tag friends")
        engagement_tactics.append("Controversial or counterintuitive statements to drive discussion")
        
        return engagement_tactics
    
    def _analyze_themes(self, videos: List[VideoData]) -> List[str]:
        """Analyze content themes in the videos"""
        content_themes = []
        
        # Look for productivity/self-improvement content
        productivity = any("habit" in v.title.lower() or "productivity" in v.title.lower() or
                         (v.description and ("habit" in v.description.lower() or "productivity" in v.description.lower()))
                         for v in videos)
        if productivity:
            content_themes.append("Personal productivity and habit formation")
        
        # Look for tech/gadget content
        tech = any("tech" in v.title.lower() or "phone" in v.title.lower() or
                 (v.description and ("tech" in v.description.lower() or "phone" in v.description.lower()))
                 for v in videos)
        if tech:
            content_themes.append("Technology tips and gadget hacks")
        
        # Look for health/wellness content
        health = any("health" in v.title.lower() or "diet" in v.title.lower() or
                   (v.description and ("health" in v.description.lower() or "diet" in v.description.lower()))
                   for v in videos)
        if health:
            content_themes.append("Health, nutrition, and wellness advice")
        
        # Common themes in viral short-form content
        content_themes.append("Life hacks and everyday problem-solving")
        content_themes.append("Behind-the-scenes or 'day in the life' content")
        
        return content_themes
    
    def _generate_summary(self, videos: List[VideoData], hook_patterns: List[Dict[str, str]], 
                         format_trends: List[str], engagement_tactics: List[str], 
                         content_themes: List[str]) -> str:
        """Generate a summary of the analysis"""
        # Calculate average views
        avg_views = sum(v.views for v in videos) / len(videos) if videos else 0
        
        # Generate summary based on the analysis
        summary = f"The analyzed videos (averaging {avg_views:,.0f} views) typically use "
        
        # Add hook patterns to summary
        if hook_patterns:
            hook_types = [h['type'] for h in hook_patterns]
            summary += f"{', '.join(hook_types[:-1]) + ' and ' + hook_types[-1] if len(hook_types) > 1 else hook_types[0]} hooks, "
        
        # Add format trends to summary
        if format_trends:
            summary += f"with a structure that typically follows {format_trends[0].lower()}. "
        
        # Add engagement tactics to summary
        if engagement_tactics:
            summary += f"Successful videos employ {engagement_tactics[0].lower()} and "
            summary += f"{engagement_tactics[1].lower() if len(engagement_tactics) > 1 else ''} to drive viewer interaction. "
        
        # Add content themes to summary
        if content_themes:
            summary += f"The most popular content focuses on {content_themes[0].lower()}"
            summary += f" and {content_themes[1].lower()}." if len(content_themes) > 1 else "."
        
        return summary

# Example usage
if __name__ == "__main__":
    # Sample data
    sample_videos = [
        VideoData(
            title="5 Morning Habits That Changed My Life",
            description="I tried these 5 morning habits for 30 days and here's what happened...",
            views=1500000,
            publishedAt="2023-05-15",
            channel="ProductivityGuru"
        ),
        VideoData(
            title="You've Been Charging Your Phone Wrong",
            description="This simple trick will make your battery last twice as long!",
            views=2300000,
            publishedAt="2023-06-02",
            channel="TechHacks"
        ),
        VideoData(
            title="What I Eat in a Day as a Nutritionist",
            description="Healthy meal ideas that take less than 10 minutes to prepare",
            views=950000,
            publishedAt="2023-05-28",
            channel="HealthyEating"
        )
    ]
    
    # Create request
    request = ContentAnalysisRequest(videos=sample_videos)
    
    # Process request
    agent = ContentStrategyAgent()
    result = asyncio.run(agent.process_request(request))
    
    print(json.dumps(result, indent=2))
