from fastapi import FastAPI, HTTPException, Body
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import uvicorn
import json
import asyncio
import os
import sys
import logging
import datetime

# Add a more robust mechanism to find agent modules
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)  # Add current directory first in path

# Add parent directory to path as well
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Try alternative common directories where agents might be
possible_paths = [
    os.path.join(current_dir, 'agents'),
    os.path.join(parent_dir, 'agents'),
    os.path.join(os.getcwd(), 'agents')
]

for path in possible_paths:
    if os.path.exists(path) and path not in sys.path:
        sys.path.insert(0, path)

# Import our agents
try:
    from agents.content_strategy_agent import ContentStrategyAgent, VideoData, ContentAnalysisRequest
    from agents.content_scriptwriter_agent import ContentScriptwriterAgent, ScriptRequest
    from agents.visual_content_planner_agent import VisualContentPlannerAgent, VisualPlanRequest
    print("Successfully imported agent modules")
except ImportError as e:
    print(f"Error importing agents: {e}")
    print("Attempting to fix import...")
    
    # List all directories and their contents to help debug
    all_dirs = []
    for p in sys.path:
        if os.path.exists(p):
            all_dirs.append(f"Directory {p} exists, contains: {os.listdir(p) if os.path.isdir(p) else 'Not a directory'}")
    print("\n".join(all_dirs))
    
    try:
        # Last resort - create direct imports with exec
        # This is not ideal but won't modify agent files
        import importlib.util
        
        agent_files = {
            'content_strategy_agent': os.path.join(current_dir, 'agents', 'content_strategy_agent.py'),
            'content_scriptwriter_agent': os.path.join(current_dir, 'agents', 'content_scriptwriter_agent.py'),
            'visual_content_planner_agent': os.path.join(current_dir, 'agents', 'visual_content_planner_agent.py')
        }
        
        modules = {}
        for name, path in agent_files.items():
            if os.path.exists(path):
                print(f"Loading {name} from {path}")
                spec = importlib.util.spec_from_file_location(name, path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                modules[name] = module
                # Add to global namespace
                globals()[name] = module
        
        # Extract needed classes
        if 'content_strategy_agent' in modules:
            ContentStrategyAgent = modules['content_strategy_agent'].ContentStrategyAgent
            VideoData = modules['content_strategy_agent'].VideoData
            ContentAnalysisRequest = modules['content_strategy_agent'].ContentAnalysisRequest
        
        if 'content_scriptwriter_agent' in modules:
            ContentScriptwriterAgent = modules['content_scriptwriter_agent'].ContentScriptwriterAgent
            ScriptRequest = modules['content_scriptwriter_agent'].ScriptRequest
        
        if 'visual_content_planner_agent' in modules:
            VisualContentPlannerAgent = modules['visual_content_planner_agent'].VisualContentPlannerAgent
            VisualPlanRequest = modules['visual_content_planner_agent'].VisualPlanRequest
        
        print("Successfully loaded modules directly")
    except Exception as e3:
        print(f"Failed all import methods: {e3}")
        raise

# Enhanced VideoData model with niche-specific fields
class EnhancedVideoData(VideoData):
    problem: Optional[str] = None
    audience: Optional[str] = None
    solution: Optional[str] = None
    emotional_triggers: Optional[str] = None
    niche: Optional[str] = None
    sub_niche: Optional[str] = None
    pain_points: Optional[str] = None
    value_proposition: Optional[str] = None

# Enhanced request model
class EnhancedContentAnalysisRequest(ContentAnalysisRequest):
    videos: List[EnhancedVideoData]
    target_niche: Optional[str] = None
    target_problem: Optional[str] = None
    target_audience: Optional[str] = None

app = FastAPI(
    title="TitanFlow Content Strategy AI",
    description="API for creating viral short-form video content from analysis to visual production plans",
    version="1.0.0"
)

# Initialize our agents
try:
    content_agent = ContentStrategyAgent()
    scriptwriter_agent = ContentScriptwriterAgent()
    visual_planner_agent = VisualContentPlannerAgent()
    print("Successfully initialized all agents")
except Exception as e:
    print(f"Error initializing agents: {e}")
    # We'll raise the error later when an endpoint is actually called
    # This allows the server to start even if there are initialization issues
    content_agent = None
    scriptwriter_agent = None
    visual_planner_agent = None

@app.get("/")
async def root():
    return {"message": "Welcome to TitanFlow Content Strategy AI", 
            "endpoints": ["/analyze", "/generate-script", "/create-visual-plan", "/full-pipeline", "/niche-analysis"]}

@app.post("/analyze", response_model=Dict[str, Any])
async def analyze_videos(request: ContentAnalysisRequest = Body(...)):
    """
    Analyze a list of viral videos and extract structured insights.
    
    The analysis includes:
    - Hook patterns (types and examples)
    - Format trends
    - Engagement tactics
    - Content themes
    - Overall summary
    """
    if content_agent is None:
        raise HTTPException(status_code=500, detail="Content analysis agent failed to initialize")
    
    try:
        result = await content_agent.process_request(request)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.post("/niche-analysis", response_model=Dict[str, Any])
async def analyze_niche_videos(request: EnhancedContentAnalysisRequest = Body(...)):
    """
    Analyze videos with enhanced niche-specific data.
    
    This endpoint accepts additional fields like problem, audience, solution, etc.
    and can filter analysis based on target niche, problem, or audience.
    """
    if content_agent is None:
        raise HTTPException(status_code=500, detail="Content analysis agent failed to initialize")
    
    try:
        # Filter videos by target parameters if provided
        filtered_videos = request.videos
        
        if request.target_niche:
            filtered_videos = [v for v in filtered_videos if v.niche and request.target_niche.lower() in v.niche.lower()]
        
        if request.target_problem:
            filtered_videos = [v for v in filtered_videos if v.problem and request.target_problem.lower() in v.problem.lower()]
            
        if request.target_audience:
            filtered_videos = [v for v in filtered_videos if v.audience and request.target_audience.lower() in v.audience.lower()]
        
        # Create standard request with filtered videos
        standard_request = ContentAnalysisRequest(
            videos=[VideoData(
                title=v.title,
                description=v.description,
                views=v.views,
                publishedAt=v.publishedAt,
                channel=v.channel
            ) for v in filtered_videos],
            analysis_type=request.analysis_type
        )
        
        # Process with standard agent
        result = await content_agent.process_request(standard_request)
        
        # Add niche-specific insights
        result["niche_insights"] = {
            "problems": list(set([v.problem for v in filtered_videos if v.problem])),
            "audiences": list(set([v.audience for v in filtered_videos if v.audience])),
            "solutions": list(set([v.solution for v in filtered_videos if v.solution])),
            "emotional_triggers": list(set([v.emotional_triggers for v in filtered_videos if v.emotional_triggers])),
            "niches": list(set([v.niche for v in filtered_videos if v.niche])),
            "sub_niches": list(set([v.sub_niche for v in filtered_videos if v.sub_niche])),
            "pain_points": list(set([v.pain_points for v in filtered_videos if v.pain_points])),
            "value_propositions": list(set([v.value_proposition for v in filtered_videos if v.value_proposition]))
        }
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Niche analysis failed: {str(e)}")

@app.post("/generate-script", response_model=Dict[str, Any])
async def generate_script(request: ScriptRequest = Body(...)):
    """
    Generate an optimized short-form video script based on content analysis data.
    
    The script includes:
    - Hook
    - Main content
    - Call to action
    - Metadata (estimated duration, hook type, theme)
    """
    if scriptwriter_agent is None:
        raise HTTPException(status_code=500, detail="Script writer agent failed to initialize")
    
    try:
        result = scriptwriter_agent.generate_script(request)
        return result.dict()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Script generation failed: {str(e)}")

@app.post("/create-visual-plan", response_model=Dict[str, Any])
async def create_visual_plan(request: VisualPlanRequest = Body(...)):
    """
    Create a detailed visual production plan from a short-form video script.
    
    The plan includes:
    - Scene breakdowns with timestamps
    - Stock footage suggestions
    - Text overlay recommendations
    - Visual effects and transitions
    - Voiceover and music guidance
    - Platform-specific editing tips
    """
    if visual_planner_agent is None:
        raise HTTPException(status_code=500, detail="Visual planner agent failed to initialize")
    
    try:
        result = visual_planner_agent.create_visual_plan(request)
        return result.dict()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Visual plan creation failed: {str(e)}")

@app.post("/full-pipeline", response_model=Dict[str, Any])
async def full_pipeline(videos: List[Dict[str, Any]] = Body(...), platform: str = Body("TikTok"), target_niche: Optional[str] = Body(None), target_problem: Optional[str] = Body(None), target_duration: int = Body(50)):
    """
    Run the complete content creation pipeline:
    1. Analyze viral videos
    2. Generate an optimized script
    3. Create a detailed visual production plan
    
    Returns the results from all three stages.
    """
    if content_agent is None or scriptwriter_agent is None or visual_planner_agent is None:
        raise HTTPException(status_code=500, detail="One or more required agents failed to initialize")
    
    try:
        # Step 1: Analyze videos
        video_data = []
        for video in videos:
            # Create VideoData or EnhancedVideoData based on available fields
            if any(key in video for key in ["problem", "audience", "solution", "niche"]):
                video_data.append(EnhancedVideoData(**video))
            else:
                video_data.append(VideoData(**video))
        
        # Use niche-specific analysis if enhanced data is available
        if any(isinstance(v, EnhancedVideoData) for v in video_data):
            analysis_request = EnhancedContentAnalysisRequest(
                videos=video_data, 
                analysis_type="full",
                target_niche=target_niche,
                target_problem=target_problem
            )
            analysis_result = await analyze_niche_videos(analysis_request)
        else:
            analysis_request = ContentAnalysisRequest(videos=video_data, analysis_type="full")
            analysis_result = await content_agent.process_request(analysis_request)
        
        # Step 2: Generate script
        script_request = ScriptRequest(
            hook_patterns=analysis_result.get("hook_patterns", []),
            format_trends=analysis_result.get("format_trends", []),
            engagement_tactics=analysis_result.get("engagement_tactics", []),
            content_themes=analysis_result.get("content_themes", []),
            summary=analysis_result.get("summary", ""),
            target_length=target_duration,
            platform=platform
        )
        
        # Add niche insights if available
        if "niche_insights" in analysis_result:
            script_request.niche_insights = analysis_result["niche_insights"]
        
        script_result = scriptwriter_agent.generate_script(script_request)
        
        # Step 3: Create visual plan
        visual_request = VisualPlanRequest(
            script=script_result.script,
            hook=script_result.title,
            cta=script_result.cta,
            niche=script_result.theme,
            tone="engaging and informative",
            platform=platform
        )
        visual_result = visual_planner_agent.create_visual_plan(visual_request)
        
        # Return all results
        return {
            "analysis": analysis_result,
            "script": script_result.dict(),
            "visual_plan": visual_result.dict()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pipeline execution failed: {str(e)}")

@app.get("/sample")
async def get_sample_request():
    """
    Returns sample request formats for all endpoints
    """
    sample_videos = [
        {
            "title": "5 Morning Habits That Changed My Life",
            "description": "I tried these 5 morning habits for 30 days and here's what happened...",
            "views": 1500000,
            "publishedAt": "2023-05-15",
            "channel": "ProductivityGuru"
        },
        {
            "title": "You've Been Charging Your Phone Wrong",
            "description": "This simple trick will make your battery last twice as long!",
            "views": 2300000,
            "publishedAt": "2023-06-02",
            "channel": "TechHacks"
        },
        {
            "title": "What I Eat in a Day as a Nutritionist",
            "description": "Healthy meal ideas that take less than 10 minutes to prepare",
            "views": 950000,
            "publishedAt": "2023-05-28",
            "channel": "HealthyEating"
        },
        {
            "title": "3 Exercises You're Doing Wrong",
            "description": "Fix these common mistakes to prevent injury and get better results",
            "views": 1800000,
            "publishedAt": "2023-06-10",
            "channel": "FitnessExpert"
        }
    ]
    
    # Enhanced sample videos with niche information
    enhanced_sample_videos = [
        {
            "title": "5 Morning Habits That Changed My Life",
            "description": "I tried these 5 morning habits for 30 days and here's what happened...",
            "views": 1500000,
            "publishedAt": "2023-05-15",
            "channel": "ProductivityGuru",
            "problem": "Lack of productivity and energy in the morning",
            "audience": "Young professionals and students",
            "solution": "Simple morning routine habits that increase productivity",
            "niche": "Productivity",
            "sub_niche": "Morning routines",
            "pain_points": "Feeling tired, unproductive, and overwhelmed",
            "value_proposition": "Boost energy and productivity with simple morning habits"
        },
        {
            "title": "You've Been Charging Your Phone Wrong",
            "description": "This simple trick will make your battery last twice as long!",
            "views": 2300000,
            "publishedAt": "2023-06-02",
            "channel": "TechHacks",
            "problem": "Phone battery dies too quickly",
            "audience": "Smartphone users of all ages",
            "solution": "Proper charging techniques to extend battery life",
            "niche": "Technology",
            "sub_niche": "Smartphone tips",
            "pain_points": "Frustration with short battery life, always needing a charger",
            "value_proposition": "Double your battery life with this simple change"
        }
    ]
    
    sample_analysis = {
        "hook_patterns": [
            {"type": "shock-based", "example": "You're doing this wrong — here's why."},
            {"type": "question-based", "example": "What if I told you this one habit could change your life?"}
        ],
        "format_trends": [
            "Hook → Insight → Visual Demo → CTA",
            "Fast-paced cuts with meme overlays and subtitles"
        ],
        "engagement_tactics": [
            "Open loops (e.g., 'Wait for it...')",
            "Direct CTAs ('Follow me for more')"
        ],
        "content_themes": [
            "Time management hacks",
            "Exposing common myths"
        ],
        "summary": "The most effective viral videos use fast-paced editing with captions and B-roll, lead with a curiosity or pain-point hook, and close with direct CTAs."
    }
    
    sample_script = {
        "script": "I can't believe I didn't know this behind-the-scenes secret sooner.\n\nWe all struggle with having too much to do and too little time. [show overwhelmed person]\n\nHere's a simple system that changed everything for me: [cut to notebook] The 1-3-5 Rule. Each day, commit to accomplishing: 1 big thing, 3 medium things, and 5 small things. [show list] That's it. This prevents overwhelm while still ensuring progress on what matters. [show completed list]\n\nStitch this with your results!",
        "hook": "I can't believe I didn't know this behind-the-scenes secret sooner.",
        "cta": "Stitch this with your results!",
        "niche": "productivity",
        "tone": "informative",
        "platform": "TikTok"
    }
    
    return {
        "analyze_endpoint": {
            "videos": sample_videos,
            "analysis_type": "full"
        },
        "niche_analysis_endpoint": {
            "videos": enhanced_sample_videos,
            "analysis_type": "full",
            "target_niche": "Productivity"
        },
        "generate_script_endpoint": sample_analysis,
        "create_visual_plan_endpoint": sample_script,
        "full_pipeline_endpoint": {
            "videos": enhanced_sample_videos,
            "platform": "TikTok",
            "target_duration": 50,
            "target_niche": "Productivity"
        }
    }

@app.get("/health")
async def health_check():
    """
    Health check endpoint for monitoring.
    Returns the status of all components.
    """
    agent_status = {
        "content_agent": content_agent is not None,
        "scriptwriter_agent": scriptwriter_agent is not None,
        "visual_planner_agent": visual_planner_agent is not None
    }
    
    # Check OpenAI API key
    openai_key_available = bool(os.environ.get("OPENAI_API_KEY"))
    
    return {
        "status": "healthy",
        "timestamp": datetime.datetime.now().isoformat(),
        "agent_status": agent_status,
        "openai_key_available": openai_key_available,
        "version": "1.0.0"
    }

if __name__ == "__main__":
    # Configure basic logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger("titanflow-api")
    
    # Check if OpenAI API key is set
    if not os.environ.get("OPENAI_API_KEY"):
        try:
            # Try to load from .env file
            from dotenv import load_dotenv
            load_dotenv()
            if not os.environ.get("OPENAI_API_KEY"):
                logger.warning("OPENAI_API_KEY not found in environment variables.")
                logger.warning("The API will run but AI generation will fall back to template-based methods.")
                print("\033[93mWARNING: OPENAI_API_KEY not found in environment variables.")
                print("The API will run but AI generation will fall back to template-based methods.")
                print("Please set your OpenAI API key in the .env file or as an environment variable.\033[0m")
        except ImportError:
            logger.warning("python-dotenv not installed or OPENAI_API_KEY not found.")
            print("\033[93mWARNING: python-dotenv not installed or OPENAI_API_KEY not found.")
            print("The API will run but AI generation will fall back to template-based methods.\033[0m")
    else:
        logger.info("OPENAI_API_KEY found in environment variables.")
    
    # Get port from environment variable for Render compatibility
    port = int(os.environ.get("PORT", 8000))
    logger.info(f"Starting server on port {port}")
    
    print("\033[92m")
    print("Starting TitanFlow AI API server...")
    print(f"The API will be available at http://localhost:{port}")
    print(f"Visit http://localhost:{port}/docs for interactive API documentation")
    print("\033[0m")
    
    try:
        uvicorn.run("content_strategy_api:app", host="0.0.0.0", port=port, reload=True)
    except Exception as e:
        logger.error(f"Failed to start server: {str(e)}")
        print(f"\033[91mERROR: Failed to start server: {str(e)}\033[0m")
