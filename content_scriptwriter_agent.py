from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field
import json
import random
from datetime import datetime
import openai
import os

class ScriptRequest(BaseModel):
    """Request structure for script generation"""
    hook_patterns: List[Dict[str, str]]
    format_trends: List[str]
    engagement_tactics: List[str]
    content_themes: List[str]
    summary: str
    target_length: int = 60  # Target length in seconds
    platform: str = "all"  # Options: "tiktok", "youtube_shorts", "instagram_reels", "all"
    niche_insights: Dict[str, List[str]] = Field(default_factory=dict)

class ScriptResponse(BaseModel):
    """Response structure for generated script"""
    title: str
    script: str
    hook_type: str
    estimated_duration: int  # in seconds
    theme: str
    cta: str
    notes: List[str] = Field(default_factory=list)

class ContentScriptwriterAgent:
    """AI Agent for generating optimized short-form video scripts"""
    
    def __init__(self, model_name: str = "gpt-4"):
        # Set up OpenAI with the API key
        openai.api_key = os.environ.get("OPENAI_API_KEY")
        if not openai.api_key:
            print("Warning: OPENAI_API_KEY not found in environment variables. GPT generation will fail.")
        
        self.model_name = model_name
        
        # Keep these templates as fallbacks in case the API call fails
        self.hook_templates = {
            "shock-based": [
                "You've been [action] wrong this whole time.",
                "This is the biggest mistake people make when [action].",
                "I can't believe I didn't know this [topic] secret sooner.",
                "Stop [action] immediately if you're doing this."
            ],
            "question-based": [
                "What if I told you [surprising claim]?",
                "Ever wondered why [intriguing question]?",
                "Do you make this common [topic] mistake?",
                "Want to know the real reason [curious situation]?"
            ],
            "number-based": [
                "3 [topic] hacks that changed my life.",
                "The #1 reason your [topic] isn't working.",
                "5 seconds that will change how you [action].",
                "These 3 [topic] tips saved me hours every day."
            ],
            "personal-story": [
                "I tried [action] for 30 days and here's what happened.",
                "My [topic] routine was completely wrong until I discovered this.",
                "I was shocked when I learned this [topic] secret.",
                "Let me show you how I [action] to get these results."
            ]
        }
        
        self.cta_templates = {
            "tiktok": [
                "Hit that follow button if you want more [topic] tips like this.",
                "Comment '[phrase]' if you're going to try this.",
                "Stitch this with your results!",
                "Save this for later when you need it!"
            ],
            "youtube_shorts": [
                "Subscribe for more [topic] hacks that actually work.",
                "Let me know in the comments if this helped you.",
                "Check the link in my bio for the full tutorial.",
                "Hit the bell so you don't miss part 2!"
            ],
            "instagram_reels": [
                "Save this to your collection for when you need it.",
                "Tag someone who needs to see this [topic] hack.",
                "DM me your before and after if you try this!",
                "Share this with someone who's been struggling with [topic]."
            ],
            "all": [
                "Follow for more [topic] tips that nobody talks about.",
                "Comment if you're going to try this today.",
                "Like and save this for later!",
                "Let me know your results in the comments!"
            ]
        }

    def _generate_with_gpt(self, prompt: str, max_tokens: int = 300) -> str:
        """Generate content using GPT"""
        try:
            response = openai.ChatCompletion.create(
                model=self.model_name,
                messages=[{"role": "system", "content": "You are an expert social media content creator specializing in viral short-form videos."},
                          {"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=0.7
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Error generating content with GPT: {str(e)}")
            return None
    
    def _select_hook(self, hook_patterns: List[Dict[str, str]], content_theme: str) -> Dict[str, str]:
        """Select an appropriate hook based on the patterns and theme using GPT"""
        # Format the hook patterns for the prompt
        hook_patterns_str = "\n".join([f"- {h['type']}: {h.get('example', '')}" for h in hook_patterns])
        
        prompt = f"""Create a compelling hook for a short-form video about {content_theme}.
        
The hook should grab attention in the first 3 seconds and be in one of these formats:
{hook_patterns_str}

Generate an original, engaging hook (1-2 sentences maximum) that will make viewers stop scrolling.
Only return the hook text itself, nothing else."""

        # Try to generate with GPT
        gpt_hook = self._generate_with_gpt(prompt, max_tokens=50)
        
        if gpt_hook:
            # Try to determine the hook type
            hook_type = "shock-based"  # Default
            for pattern in hook_patterns:
                if pattern.get("example") and any(keyword in gpt_hook.lower() for keyword in pattern.get("example", "").lower().split()):
                    hook_type = pattern["type"]
                    break
            
            return {"type": hook_type, "hook": gpt_hook}
        
        # Fall back to template-based approach if GPT fails
        if hook_patterns and len(hook_patterns) > 0:
            selected_hook_type = random.choice(hook_patterns)["type"]
            templates = self.hook_templates.get(selected_hook_type, self.hook_templates["shock-based"])
            template = random.choice(templates)
            
            hook = template.replace("[topic]", content_theme.split()[0].lower())
            hook = hook.replace("[action]", self._get_action_from_theme(content_theme))
            hook = hook.replace("[surprising claim]", f"one simple {content_theme.split()[0].lower()} hack could save you hours")
            hook = hook.replace("[intriguing question]", f"most people get {content_theme.split()[0].lower()} completely wrong")
            hook = hook.replace("[curious situation]", f"your {content_theme.split()[0].lower()} isn't improving")
            hook = hook.replace("[phrase]", "I'll try this")
            
            return {"type": selected_hook_type, "hook": hook}
        
        # Fallback to a generic hook
        return {"type": "shock-based", "hook": f"You've been approaching {content_theme.split()[0].lower()} all wrong."}
    
    def _get_action_from_theme(self, theme: str) -> str:
        """Extract an action verb from the theme"""
        theme_lower = theme.lower()
        
        if "productivity" in theme_lower or "habit" in theme_lower or "time management" in theme_lower:
            return random.choice(["planning your day", "setting priorities", "managing your time"])
        elif "tech" in theme_lower or "phone" in theme_lower:
            return random.choice(["charging your phone", "using your apps", "backing up your data"])
        elif "health" in theme_lower or "diet" in theme_lower or "nutrition" in theme_lower:
            return random.choice(["meal prepping", "counting calories", "planning your diet"])
        elif "life hack" in theme_lower or "problem-solving" in theme_lower:
            return random.choice(["organizing your space", "saving money", "simplifying your life"])
        else:
            return "doing this"
    
    def _select_cta(self, engagement_tactics: List[str], platform: str, theme: str) -> str:
        """Select an appropriate call to action using GPT"""
        tactics_str = "\n".join([f"- {tactic}" for tactic in engagement_tactics])
        
        prompt = f"""Create a compelling call-to-action (CTA) for a {platform} video about {theme}.

The video engages viewers using these tactics:
{tactics_str}

Generate an original, engaging CTA (1 sentence) that will drive engagement and follows {platform}'s best practices.
Only return the CTA text itself, nothing else."""

        # Try to generate with GPT
        gpt_cta = self._generate_with_gpt(prompt, max_tokens=50)
        
        if gpt_cta:
            return gpt_cta
        
        # Fall back to template-based approach if GPT fails
        templates = self.cta_templates.get(platform.lower(), self.cta_templates["all"])
        template = random.choice(templates)
        cta = template.replace("[topic]", theme.split()[0].lower())
        cta = cta.replace("[phrase]", "I'll try this")
        
        return cta
    
    def _generate_script_body(self, hook: str, theme: str, format_trends: List[str]) -> str:
        """Generate the main body of the script based on the hook and theme using GPT"""
        # Format the format trends for the prompt
        format_trends_str = "\n".join([f"- {trend}" for trend in format_trends])
        
        prompt = f"""Write the main body of a viral short-form video script about {theme}. 
        
The script should start with this hook: "{hook}"

The script should follow these structural patterns:
{format_trends_str}

The main body should:
1. Identify a relatable problem or pain point
2. Present a solution, insight, or value
3. Include visual cues in [brackets] to guide production
4. Be optimized for 30-60 seconds total duration
5. Use conversational, engaging language
6. NOT include the CTA (that will be added separately)

Format the response as:
[Problem section with visual cues]
[Solution section with visual cues]

Keep the entire script body under 150 words for a fast-paced delivery."""

        # Try to generate with GPT
        gpt_body = self._generate_with_gpt(prompt, max_tokens=250)
        
        if gpt_body:
            return f"{hook}\n\n{gpt_body}"
        
        # Fall back to template-based approach if GPT fails
        if "productivity" in theme.lower() or "habit" in theme.lower() or "time management" in theme.lower():
            problem = "Most people waste hours every day on tasks that don't move the needle. [show frustrated person]"
            solution = "Instead, try time blocking: [cut to phone calendar] First, identify your top 3 priorities for tomorrow. [show list] Then, schedule specific time blocks for each one. [show calendar] The key is to work in 25-minute focused sessions with 5-minute breaks. [show timer]"
        
        elif "tech" in theme.lower() or "phone" in theme.lower():
            problem = "Your phone battery dying mid-day is not just annoying—it's preventable. [show phone at 1%]"
            solution = "Here's what actually kills your battery: [cut to settings] Background apps constantly refreshing. [show settings menu] Go to Settings → General → Background App Refresh and turn it off for apps you don't need instant updates from. [show toggling off] This one change can give you 2-3 extra hours of battery life. [show battery percentage increasing]"
        
        elif "health" in theme.lower() or "diet" in theme.lower() or "nutrition" in theme.lower():
            problem = "That afternoon energy crash isn't normal, and it's probably because of what you're eating for lunch. [show tired person at desk]"
            solution = "Try this instead: [cut to meal prep] Combine protein, healthy fats, and complex carbs in every meal. [show food items] For example: grilled chicken, avocado, and sweet potato. [show meal] This balanced combo prevents blood sugar spikes and keeps your energy stable all day. [show energetic person working]"
        
        else:  # Generic life hack
            problem = "We all struggle with having too much to do and too little time. [show overwhelmed person]"
            solution = "Here's a simple system that changed everything for me: [cut to notebook] The 1-3-5 Rule. Each day, commit to accomplishing: 1 big thing, 3 medium things, and 5 small things. [show list] That's it. This prevents overwhelm while still ensuring progress on what matters. [show completed list]"
        
        return f"{hook}\n\n{problem}\n\n{solution}"
    
    def generate_script(self, request: ScriptRequest) -> ScriptResponse:
        """Generate an optimized short-form video script based on viral content analysis"""
        # Select a content theme
        selected_theme = random.choice(request.content_themes) if request.content_themes else "productivity hacks"
        
        # Select a hook based on the patterns
        hook_selection = self._select_hook(request.hook_patterns, selected_theme)
        
        # Generate the script body
        script_body = self._generate_script_body(hook_selection["hook"], selected_theme, request.format_trends)
        
        # Select a CTA
        cta = self._select_cta(request.engagement_tactics, request.platform, selected_theme)
        
        # Combine everything into a complete script
        full_script = f"{script_body}\n\n{cta}"
        
        # Generate a title
        title = f"{hook_selection['hook']}"
        if len(title) > 60:
            title = title[:57] + "..."
        
        # Estimate duration (rough approximation: ~2.5 words per second for fast-paced delivery)
        word_count = len(full_script.split())
        estimated_duration = max(min(int(word_count / 2.5), 60), 15)  # Between 15-60 seconds
        
        # Create notes about the script
        notes = [
            f"Estimated duration: {estimated_duration} seconds",
            f"Hook type: {hook_selection['type']}",
            f"Primary theme: {selected_theme}",
            f"Target platform: {request.platform}"
        ]
        
        # Include platform-specific notes
        if request.platform.lower() == "tiktok":
            notes.append("Optimize for mobile vertical format (9:16)")
        elif request.platform.lower() == "youtube_shorts":
            notes.append("Include subscribe reminder overlay in final seconds")
        elif request.platform.lower() == "instagram_reels":
            notes.append("Consider adding trending sound/music for additional reach")
        
        return ScriptResponse(
            title=title,
            script=full_script,
            hook_type=hook_selection["type"],
            estimated_duration=estimated_duration,
            theme=selected_theme,
            cta=cta,
            notes=notes
        )

# Example usage
if __name__ == "__main__":
    # Sample data based on viral video analysis
    sample_request = ScriptRequest(
        hook_patterns=[
            {"type": "shock-based", "example": "You're doing this wrong — here's why."},
            {"type": "question-based", "example": "What if I told you this one habit could change your life?"}
        ],
        format_trends=[
            "Hook → Insight → Visual Demo → CTA",
            "Fast-paced cuts with meme overlays and subtitles"
        ],
        engagement_tactics=[
            "Open loops (e.g., 'Wait for it...')",
            "Direct CTAs ('Follow me for more')"
        ],
        content_themes=[
            "Time management hacks",
            "Exposing common myths"
        ],
        summary="The most effective viral videos use fast-paced editing with captions and B-roll, lead with a curiosity or pain-point hook, and close with direct CTAs.",
        platform="tiktok"
    )
    
    # Generate script
    agent = ContentScriptwriterAgent()
    result = agent.generate_script(sample_request)
    
    # Print the result
    print("===== GENERATED SCRIPT =====\n")
    print(f"TITLE: {result.title}\n")
    print(f"HOOK TYPE: {result.hook_type}\n")
    print(f"THEME: {result.theme}\n")
    print(f"ESTIMATED DURATION: {result.estimated_duration} seconds\n")
    print("SCRIPT:")
    print("--------")
    print(result.script)
    print("--------\n")
    print(f"CTA: {result.cta}\n")
    print("NOTES:")
    for note in result.notes:
        print(f"- {note}")
