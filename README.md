# TitanFlow AI

TitanFlow AI is a comprehensive content creation system for viral short-form videos, providing AI-powered tools from content strategy development to visual production planning.

## Features

- **Content Strategy Analysis**: Analyze viral videos to extract hook patterns, format trends, engagement tactics, and content themes.
- **Script Generation**: Create optimized short-form video scripts based on content analysis data.
- **Visual Production Planning**: Generate detailed visual plans from scripts, including scene breakdowns, stock footage suggestions, and editing tips.

## Installation

1. Clone this repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Set up your OpenAI API key in `.env` file:
   ```
   OPENAI_API_KEY=your_api_key_here
   ```

## Usage

### API Server

Start the API server:
```
python content_strategy_api.py
```

The server will be available at http://localhost:8000 with the following endpoints:
- `/analyze` - Analyze viral videos
- `/generate-script` - Generate video scripts
- `/create-visual-plan` - Create visual production plans
- `/full-pipeline` - Run the complete content creation pipeline
- `/niche-analysis` - Analyze videos with niche-specific data

### Command Line Tools

Analyze viral videos:
```
python analyze_viral_videos.py --file videos.json --output analysis.json
```

Create a visual plan:
```
python create_visual_plan.py --script script.json --platform TikTok --output plan.json
```

## Deployment to Render

### 1. Prepare your repository

1. Push your code to a GitHub repository:
   ```
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/yourusername/titanflow-ai.git
   git push -u origin main
   ```

### 2. Deploy on Render

1. Sign up for a [Render account](https://render.com/)
2. From the Render dashboard, click "New" and select "Web Service"
3. Connect your GitHub repository
4. Configure the service:
   - **Name**: titanflow-ai (or your preferred name)
   - **Environment**: Python
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn content_strategy_api:app -k uvicorn.workers.UvicornWorker`
5. Add environment variable:
   - Add `OPENAI_API_KEY` with your OpenAI API key
6. Click "Create Web Service"

Render will automatically deploy your app and provide a URL for access.

### Using Render Blueprint

If you want to use the Render Blueprint for automatic deployment:

1. Commit and push the `render.yaml` file to your GitHub repository
2. In your Render dashboard, click "New" and select "Blueprint"
3. Connect your GitHub repository
4. Render will automatically configure the service based on the `render.yaml` file
5. Make sure to set the `OPENAI_API_KEY` environment variable in the Render dashboard

## API Input Format

### Full Pipeline Endpoint

POST to `/full-pipeline` with this JSON format:

```json
{
  "videos": [
    {
      "title": "Video Title",
      "description": "Video description",
      "views": 1000000,
      "publishedAt": "2023-05-15",
      "channel": "ChannelName",
      "problem": "Problem description", // optional
      "audience": "Target audience", // optional
      "solution": "Solution offered", // optional
      "niche": "Primary category", // optional
      "sub_niche": "Specific category", // optional
      "pain_points": "Audience frustrations", // optional
      "value_proposition": "Core value offered" // optional
    }
  ],
  "platform": "TikTok", // optional, default is "TikTok"
  "target_duration": 50, // optional, default is 50 seconds
  "target_niche": "YourNiche" // optional, filters the analysis
}
```

## System Architecture

The system consists of three core AI agents:

1. **ContentStrategyAgent**: Analyzes viral video content and extracts patterns and insights.
2. **ContentScriptwriterAgent**: Generates optimized scripts based on content analysis.
3. **VisualContentPlannerAgent**: Creates detailed visual production plans for video scripts.

Each agent uses GPT for generating creative and analytical content, with fallback mechanisms for reliability.

## License

MIT 