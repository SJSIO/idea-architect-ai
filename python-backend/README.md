# Startup Analyzer - LangGraph Python Backend

This is the Python/LangGraph backend for the Startup Analyzer application.

## Setup

1. **Create virtual environment**
```bash
cd python-backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Set environment variables**
```bash
# Option 1: OpenAI
export OPENAI_API_KEY=your_openai_key

# Option 2: Groq (uncomment groq lines in main.py)
export GROQ_API_KEY=your_groq_key
```

4. **Run the server**
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

## API Endpoints

### `POST /analyze`
Analyzes a startup idea using 6 AI agents + strategist/critic debate.

**Request:**
```json
{
  "startupIdea": "A platform that connects local farmers with consumers...",
  "targetMarket": "Urban consumers in tier-1 cities",
  "projectId": "optional-uuid"
}
```

**Response:**
```json
{
  "success": true,
  "projectId": "...",
  "analysis": {
    "marketAnalysis": "...",
    "costPrediction": "...",
    "businessStrategy": "...",
    "monetization": "...",
    "legalConsiderations": "...",
    "techStack": "...",
    "strategistCritique": "..."
  }
}
```

## Deployment Options

### Railway
1. Create new project on railway.app
2. Connect your GitHub repo
3. Set environment variables
4. Deploy automatically

### Render
1. Create new Web Service on render.com
2. Connect GitHub repo
3. Build command: `pip install -r requirements.txt`
4. Start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`

### Google Cloud Run
```bash
gcloud run deploy startup-analyzer \
  --source . \
  --region us-central1 \
  --allow-unauthenticated
```

### Docker
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    LangGraph Workflow                        │
├─────────────────────────────────────────────────────────────┤
│  Phase 1: 6 Specialist Agents (Sequential)                  │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐                    │
│  │ Market   │→│ Cost     │→│ Business │                    │
│  │ Analyst  │ │ Predictor│ │ Strategy │                    │
│  └──────────┘ └──────────┘ └──────────┘                    │
│       ↓                                                      │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐                    │
│  │Monetize  │→│ Legal    │→│ Tech     │                    │
│  │ Expert   │ │ Advisor  │ │ Architect│                    │
│  └──────────┘ └──────────┘ └──────────┘                    │
│       ↓                                                      │
│  Phase 2: Strategist Synthesis                              │
│  ┌──────────────────────────────────────┐                  │
│  │ Strategist synthesizes all insights  │                  │
│  └──────────────────────────────────────┘                  │
│       ↓                                                      │
│  Phase 3: Critic Review                                      │
│  ┌──────────────────────────────────────┐                  │
│  │ Critic challenges the plan           │                  │
│  └──────────────────────────────────────┘                  │
│       ↓                                                      │
│  Phase 4: Final Refinement                                   │
│  ┌──────────────────────────────────────┐                  │
│  │ Strategist refines based on critique │                  │
│  └──────────────────────────────────────┘                  │
└─────────────────────────────────────────────────────────────┘
```

## Connecting to Lovable Frontend

Once deployed, update your Lovable frontend to call your Python backend:

1. Get your deployed API URL (e.g., `https://your-app.railway.app`)
2. Update the frontend to call this URL instead of the edge function
