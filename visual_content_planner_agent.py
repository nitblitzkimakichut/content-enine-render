from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field
import json
import random
import os
import openai

class SceneData(BaseModel):
    """Data structure for a scene in the visual plan"""
    timestamp: str
    script_segment: str
    stock_footage: List[str] = Field(default_factory=list)
    text_overlay: Optional[str] = None
    visual_effects: List[str] = Field(default_factory=list)
    transition: str = "Cut"

class VisualPlanRequest(BaseModel):
    """Request structure for visual plan generation"""
    script: str
    hook: Optional[str] = None
    cta: Optional[str] = None
    niche: Optional[str] = None
    tone: str = "engaging"
    platform: str = "TikTok"  # Options: "TikTok", "Instagram", "YouTube"

class VisualPlanResponse(BaseModel):
    """Response structure for visual plan"""
    title: str
    scenes: List[SceneData]
    total_duration: str
    music_recommendation: str
    voiceover_style: str
    stock_footage_platforms: List[str] = Field(default_factory=list)
    editing_tips: List[str] = Field(default_factory=list)

class VisualContentPlannerAgent:
    """AI Agent for creating detailed visual production plans for short-form videos"""
    
    def __init__(self, model_name: str = "gpt-4"):
        # Set up OpenAI with the API key
        openai.api_key = os.environ.get("OPENAI_API_KEY")
        if not openai.api_key:
            print("Warning: OPENAI_API_KEY not found in environment variables. GPT generation will fail.")
        
        self.model_name = model_name
        
        # Fallback transition options
        self.transitions = [
            "Cut", 
            "Fade", 
            "Dissolve", 
            "Wipe", 
            "Zoom In", 
            "Zoom Out", 
            "Slide Left", 
            "Slide Right", 
            "Whip Pan", 
            "Split Screen"
        ]
        
        # Fallback visual effects options
        self.visual_effects = {
            "TikTok": [
                "Slow Motion", 
                "Text Animation", 
                "Green Screen", 
                "Duet Effect", 
                "Background Blur", 
                "Color Filter", 
                "Time Warp Scan", 
                "Sticker Overlay",
                "Glitch Effect",
                "Tracking Text"
            ],
            "Instagram": [
                "Boomerang", 
                "Superzoom", 
                "Face Filters", 
                "GIF Stickers", 
                "Color Filter", 
                "Drawing Tools", 
                "3D Text", 
                "AR Effects",
                "Depth Effect",
                "Slow Motion"
            ],
            "YouTube": [
                "Lower Thirds", 
                "Closed Captions", 
                "End Screen Elements", 
                "Pop-up Cards", 
                "Split Screen", 
                "Screen-in-Screen", 
                "Zoom Emphasis", 
                "Motion Graphics",
                "Cross Fade",
                "Color Grading"
            ]
        }
        
        # Fallback stock footage platforms
        self.stock_footage_platforms = [
            "Pexels", 
            "Pixabay", 
            "Unsplash", 
            "Storyblocks", 
            "Mixkit", 
            "Videvo", 
            "Coverr"
        ]
    
    def _generate_with_gpt(self, prompt: str, max_tokens: int = 1000) -> str:
        """Generate content using GPT"""
        try:
            response = openai.ChatCompletion.create(
                model=self.model_name,
                messages=[{"role": "system", "content": "You are an expert video producer specializing in short-form video content creation."},
                          {"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=0.7
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Error generating content with GPT: {str(e)}")
            return None
    
    def create_visual_plan(self, request: VisualPlanRequest) -> VisualPlanResponse:
        """Create a detailed visual production plan from a script"""
        try:
            # Try generating the complete visual plan with GPT
            gpt_plan = self._generate_visual_plan_with_gpt(request)
            if gpt_plan:
                return gpt_plan
            
            # If GPT fails, fall back to template-based approach
            return self._create_visual_plan_template(request)
        except Exception as e:
            print(f"Error creating visual plan: {str(e)}")
            # Return a basic fallback plan
            return self._create_fallback_plan(request)
    
    def _generate_visual_plan_with_gpt(self, request: VisualPlanRequest) -> Optional[VisualPlanResponse]:
        """Generate a visual plan using GPT"""
        # Format the request for the prompt
        script = request.script or ""
        hook = request.hook or (script.split("\n\n")[0] if "\n\n" in script else script.split(".")[0])
        cta = request.cta or "Follow for more content like this!"
        niche = request.niche or "lifestyle"
        
        prompt = f"""Create a detailed visual production plan for a {request.platform} short-form video.

SCRIPT:
{script}

HOOK: {hook}
CTA: {cta}
NICHE: {niche}
TONE: {request.tone}
PLATFORM: {request.platform}

Create a comprehensive visual production plan that includes:
1. A catchy title for the video
2. 4-8 scene breakdowns with:
   - Timestamp (e.g., "0:00-0:05")
   - Script segment for that scene
   - 2-3 stock footage suggestions
   - Text overlay recommendations (if appropriate)
   - 1-2 visual effects to apply
   - Transition to the next scene
3. Total estimated duration
4. Music style recommendation
5. Voiceover style guidance
6. 3-5 recommended stock footage platforms
7. 3-5 editing tips specific to {request.platform}

Format your response as valid JSON that matches this structure:
{{
  "title": "Catchy Title",
  "scenes": [
    {{
      "timestamp": "0:00-0:05",
      "script_segment": "Script for this scene",
      "stock_footage": ["Footage 1", "Footage 2"],
      "text_overlay": "Text to display (if any)",
      "visual_effects": ["Effect 1", "Effect 2"],
      "transition": "Transition type"
    }}
  ],
  "total_duration": "00:45",
  "music_recommendation": "Music style",
  "voiceover_style": "Voice guidance",
  "stock_footage_platforms": ["Platform 1", "Platform 2"],
  "editing_tips": ["Tip 1", "Tip 2"]
}}

Make the plan practical, detailed, and optimized for maximum engagement on {request.platform}.
"""

        try:
            # Generate with GPT
            result = self._generate_with_gpt(prompt, max_tokens=1200)
            if result:
                # Parse the JSON response
                plan_data = json.loads(result)
                
                # Convert to our response model
                scenes = []
                for scene in plan_data.get("scenes", []):
                    scenes.append(SceneData(
                        timestamp=scene.get("timestamp", "0:00-0:00"),
                        script_segment=scene.get("script_segment", ""),
                        stock_footage=scene.get("stock_footage", []),
                        text_overlay=scene.get("text_overlay", None),
                        visual_effects=scene.get("visual_effects", []),
                        transition=scene.get("transition", "Cut")
                    ))
                
                return VisualPlanResponse(
                    title=plan_data.get("title", hook),
                    scenes=scenes,
                    total_duration=plan_data.get("total_duration", "00:00"),
                    music_recommendation=plan_data.get("music_recommendation", "Upbeat background music"),
                    voiceover_style=plan_data.get("voiceover_style", "Energetic and clear"),
                    stock_footage_platforms=plan_data.get("stock_footage_platforms", self.stock_footage_platforms[:3]),
                    editing_tips=plan_data.get("editing_tips", [])
                )
        except Exception as e:
            print(f"Error parsing GPT visual plan: {str(e)}")
            return None
    
    def _create_visual_plan_template(self, request: VisualPlanRequest) -> VisualPlanResponse:
        """Create a visual plan using template-based approach (fallback)"""
        # Extract information from the request
        script = request.script or ""
        hook = request.hook or (script.split("\n\n")[0] if "\n\n" in script else script.split(".")[0])
        cta = request.cta or "Follow for more content like this!"
        niche = request.niche or "lifestyle"
        platform = request.platform
        
        # Generate a title
        title = hook if len(hook) < 60 else hook[:57] + "..."
        
        # Set up default durations based on platform
        if platform == "TikTok":
            default_duration = "0:40"
        elif platform == "Instagram":
            default_duration = "0:55"
        else:  # YouTube Shorts
            default_duration = "0:58"
        
        # Split the script into segments
        segments = script.split("\n\n") if "\n\n" in script else script.split(". ")
        
        # Create scenes
        scenes = []
        total_seconds = 0
        
        # Hook scene (0:00-0:05)
        hook_scene = SceneData(
            timestamp="0:00-0:05",
            script_segment=hook,
            stock_footage=self._suggest_stock_footage(hook, niche),
            text_overlay=hook if len(hook) < 40 else None,
            visual_effects=self._suggest_visual_effects(platform, "hook"),
            transition=random.choice(self.transitions)
        )
        scenes.append(hook_scene)
        total_seconds += 5
        
        # Content scenes
        segment_duration = max(3, min(10, 30 // max(1, len(segments) - 2)))  # Between 3-10 seconds per segment
        
        for i, segment in enumerate(segments[1:-1] if len(segments) > 2 else segments):
            start_time = total_seconds
            end_time = total_seconds + segment_duration
            
            scene = SceneData(
                timestamp=f"{start_time//60}:{start_time%60:02d}-{end_time//60}:{end_time%60:02d}",
                script_segment=segment,
                stock_footage=self._suggest_stock_footage(segment, niche),
                text_overlay=self._suggest_text_overlay(segment),
                visual_effects=self._suggest_visual_effects(platform, "content"),
                transition=random.choice(self.transitions)
            )
            scenes.append(scene)
            total_seconds += segment_duration
        
        # CTA scene
        if cta:
            start_time = total_seconds
            end_time = total_seconds + 5
            
            cta_scene = SceneData(
                timestamp=f"{start_time//60}:{start_time%60:02d}-{end_time//60}:{end_time%60:02d}",
                script_segment=cta,
                stock_footage=self._suggest_stock_footage("creator speaking directly to camera", niche),
                text_overlay=cta if len(cta) < 40 else None,
                visual_effects=self._suggest_visual_effects(platform, "cta"),
                transition="Fade"
            )
            scenes.append(cta_scene)
            total_seconds += 5
        
        # Format the total duration
        total_duration = f"{total_seconds//60}:{total_seconds%60:02d}"
        
        # Generate recommendations based on niche and platform
        music_recommendation = self._suggest_music(niche, request.tone)
        voiceover_style = self._suggest_voiceover(niche, request.tone)
        stock_footage_platforms = random.sample(self.stock_footage_platforms, min(4, len(self.stock_footage_platforms)))
        editing_tips = self._suggest_editing_tips(platform)
        
        return VisualPlanResponse(
            title=title,
            scenes=scenes,
            total_duration=total_duration,
            music_recommendation=music_recommendation,
            voiceover_style=voiceover_style,
            stock_footage_platforms=stock_footage_platforms,
            editing_tips=editing_tips
        )
    
    def _suggest_stock_footage(self, segment: str, niche: str) -> List[str]:
        """Suggest stock footage based on segment text and niche"""
        # Extract keywords from the segment
        keywords = [word.lower() for word in segment.split() if len(word) > 3]
        
        # Niche-specific suggestions
        niche_footage = {
            "productivity": ["person working at desk", "calendar planning", "time management app"],
            "tech": ["smartphone usage", "app interface", "tech gadget closeup"],
            "health": ["healthy meal prep", "workout sequence", "meditation scene"],
            "finance": ["money saving visualization", "investment chart", "budgeting app"],
            "home": ["home organization", "cleaning transformation", "interior design"],
            "beauty": ["skincare routine", "makeup application", "before/after transition"],
            "fashion": ["outfit styling", "fabric closeup", "accessory details"],
            "travel": ["destination views", "packing process", "travel hacks"],
            "cooking": ["ingredient preparation", "cooking technique", "final dish reveal"],
            "fitness": ["workout demonstration", "before/after body transformation", "gym equipment"]
        }
        
        # Default suggestions based on common short-form video elements
        default_footage = [
            "person speaking to camera",
            "relevant B-roll footage",
            "text animation on solid background"
        ]
        
        # Get niche-specific suggestions if available
        for n, suggestions in niche_footage.items():
            if n in niche.lower():
                specific_suggestions = suggestions.copy()
                # Add one keyword-based suggestion if possible
                if keywords:
                    specific_suggestions.append(f"{random.choice(keywords)} visual")
                return specific_suggestions[:3]
        
        # If no niche match, use keywords to generate suggestions
        if keywords:
            keyword_suggestions = [f"{kw} visual" for kw in random.sample(keywords, min(3, len(keywords)))]
            return keyword_suggestions + default_footage[:3-len(keyword_suggestions)]
        
        return default_footage
    
    def _suggest_text_overlay(self, segment: str) -> Optional[str]:
        """Suggest text overlay for a segment"""
        # If segment is short enough, use it directly
        if len(segment) < 40:
            return segment
        
        # Extract key phrases
        if "." in segment:
            key_phrase = segment.split(".")[0]
            if len(key_phrase) < 40:
                return key_phrase
        
        # Extract first sentence or important keywords
        words = segment.split()
        if len(words) > 5:
            return " ".join(words[:5]) + "..."
        
        return None
    
    def _suggest_visual_effects(self, platform: str, scene_type: str) -> List[str]:
        """Suggest visual effects based on platform and scene type"""
        platform_effects = self.visual_effects.get(platform, self.visual_effects["TikTok"])
        
        if scene_type == "hook":
            # Hook scenes need attention-grabbing effects
            hook_effects = ["Text Animation", "Zoom In", "Color Filter", "Motion Graphics"]
            available_effects = [e for e in hook_effects if e in platform_effects]
            if not available_effects:
                available_effects = platform_effects
            
            return random.sample(available_effects, min(2, len(available_effects)))
        
        elif scene_type == "cta":
            # CTA scenes need clear, engaging effects
            cta_effects = ["Text Animation", "Sticker Overlay", "3D Text", "GIF Stickers"]
            available_effects = [e for e in cta_effects if e in platform_effects]
            if not available_effects:
                available_effects = platform_effects
            
            return random.sample(available_effects, min(2, len(available_effects)))
        
        else:  # Content scenes
            return random.sample(platform_effects, min(2, len(platform_effects)))
    
    def _suggest_music(self, niche: str, tone: str) -> str:
        """Suggest background music based on niche and tone"""
        niche_music = {
            "productivity": "Upbeat lo-fi with light percussion",
            "tech": "Modern electronic with tech sounds",
            "health": "Calm ambient with nature elements",
            "finance": "Professional corporate with positive progression",
            "home": "Cozy acoustic with warm tones",
            "beauty": "Stylish pop with fashionable beats",
            "fashion": "Trendy electronic with runway vibes",
            "travel": "Exotic instrumental with cultural elements",
            "cooking": "Light jazz with kitchen-friendly rhythm",
            "fitness": "High-energy EDM with strong beat"
        }
        
        tone_adjectives = {
            "energetic": "high-energy",
            "calm": "soothing",
            "professional": "polished",
            "fun": "playful",
            "emotional": "moving",
            "informative": "neutral",
            "inspiring": "uplifting",
            "humorous": "quirky"
        }
        
        # Find matching niche
        music_base = "Trendy background music"
        for n, suggestion in niche_music.items():
            if n in niche.lower():
                music_base = suggestion
                break
        
        # Add tone modifier
        tone_modifier = ""
        for t, adjective in tone_adjectives.items():
            if t in tone.lower():
                tone_modifier = adjective
                break
        
        if tone_modifier:
            return f"{tone_modifier.capitalize()} {music_base.lower()}"
        
        return music_base
    
    def _suggest_voiceover(self, niche: str, tone: str) -> str:
        """Suggest voiceover style based on niche and tone"""
        niche_voice = {
            "productivity": "Clear and motivational",
            "tech": "Knowledgeable and straightforward",
            "health": "Calming and authoritative",
            "finance": "Professional and trustworthy",
            "home": "Friendly and approachable",
            "beauty": "Enthusiastic and detailed",
            "fashion": "Stylish and confident",
            "travel": "Adventurous and descriptive",
            "cooking": "Warm and instructional",
            "fitness": "Energetic and encouraging"
        }
        
        tone_modifiers = {
            "energetic": "with high energy",
            "calm": "with a soothing tone",
            "professional": "with expert delivery",
            "fun": "with playful inflection",
            "emotional": "with authentic feeling",
            "informative": "with clear articulation",
            "inspiring": "with motivational emphasis",
            "humorous": "with comedic timing"
        }
        
        # Find matching niche
        voice_base = "Engaging and conversational"
        for n, suggestion in niche_voice.items():
            if n in niche.lower():
                voice_base = suggestion
                break
        
        # Add tone modifier
        tone_modifier = ""
        for t, modifier in tone_modifiers.items():
            if t in tone.lower():
                tone_modifier = modifier
                break
        
        if tone_modifier:
            return f"{voice_base} {tone_modifier}"
        
        return voice_base
    
    def _suggest_editing_tips(self, platform: str) -> List[str]:
        """Suggest editing tips based on platform"""
        platform_tips = {
            "TikTok": [
                "Keep transitions snappy - no longer than 0.3 seconds",
                "Use trending sounds/music to increase discoverability",
                "Add closed captions for better engagement (80% watch with sound off)",
                "Maintain high-energy pacing throughout",
                "Include text overlays for key points",
                "Use trending effects when they match your content",
                "Front-load the hook in the first 1-2 seconds",
                "End with a strong call-to-action"
            ],
            "Instagram": [
                "Maintain 9:16 aspect ratio for optimal display",
                "Use Instagram's built-in effects for better algorithmic performance",
                "Include a mix of on-screen text and voiceover",
                "Tag relevant accounts/products in the video",
                "Use Instagram's music library for better reach",
                "Create shareable moments for Stories reshares",
                "Design colorful and vibrant visuals",
                "End with a question to encourage comments"
            ],
            "YouTube": [
                "Include a clear hook within the first 3 seconds",
                "Add a branded subscribe animation at the end",
                "Use YouTube's end screen elements for the last 5-10 seconds",
                "Optimize brightness and contrast for mobile viewing",
                "Include closed captions for accessibility",
                "Use chapters/timestamps in video description",
                "Create a consistent color grade throughout",
                "Include subtle background music at 10-15% volume under narration"
            ]
        }
        
        default_tips = [
            "Keep editing pace fast with cuts every 1-2 seconds",
            "Add text overlays for all key points",
            "Use subtle zoom effects to maintain visual interest",
            "Include motion graphics for statistics or numbers",
            "Ensure clear audio quality for voiceover"
        ]
        
        tips = platform_tips.get(platform, default_tips)
        return random.sample(tips, min(5, len(tips)))
    
    def _create_fallback_plan(self, request: VisualPlanRequest) -> VisualPlanResponse:
        """Create an absolute minimal fallback plan in case of errors"""
        script = request.script or ""
        hook = request.hook or "Attention-grabbing hook"
        
        # Very simple single-scene plan
        scenes = [SceneData(
            timestamp="0:00-0:30",
            script_segment=script,
            stock_footage=["Person talking to camera", "Relevant B-roll"],
            text_overlay="Key message",
            visual_effects=["Text Animation"],
            transition="Cut"
        )]
        
        return VisualPlanResponse(
            title=hook,
            scenes=scenes,
            total_duration="0:30",
            music_recommendation="Upbeat background music",
            voiceover_style="Clear and engaging",
            stock_footage_platforms=["Pexels", "Pixabay"],
            editing_tips=["Keep it simple", "Focus on clear audio"]
        )

# Example usage
if __name__ == "__main__":
    # Sample request
    sample_request = VisualPlanRequest(
        script="They said this kitchen was a lost cause. But $3,000 and 6 weekends later? It's now our favorite room.",
        hook="You won't believe this transformation.",
        cta="Follow for more budget renovation ideas.",
        niche="home renovation",
        tone="inspiring and upbeat",
        platform="TikTok"
    )
    
    # Generate visual plan
    agent = VisualContentPlannerAgent()
    result = agent.create_visual_plan(sample_request)
    
    # Print the result
    print("===== VISUAL CONTENT PLAN =====\n")
    print(f"TITLE: {result.title}\n")
    print(f"TOTAL DURATION: {result.total_duration}\n")
    print(f"VOICEOVER: {result.voiceover_style}\n")
    print(f"MUSIC: {result.music_recommendation}\n")
    
    print("SCENES:")
    for i, scene in enumerate(result.scenes):
        print(f"\nSCENE {i+1}: {scene.timestamp}")
        print(f"TEXT: {scene.script_segment}")
        print(f"STOCK FOOTAGE: {', '.join(scene.stock_footage)}")
        if scene.text_overlay:
            print(f"TEXT OVERLAY: {scene.text_overlay}")
        print(f"VISUAL EFFECTS: {', '.join(scene.visual_effects)}")
        print(f"TRANSITION: {scene.transition}")
    
    print("\nSTOCK FOOTAGE SOURCES:")
    for source in result.stock_footage_platforms:
        print(f"- {source}")
    
    print("\nEDITING TIPS:")
    for tip in result.editing_tips:
        print(f"- {tip}")
