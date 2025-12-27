# Startup Analyzer - Django + LangGraph Backend

This is the Django/LangGraph backend for the Startup Analyzer application.

## Project Structure

```
python-backend/
├── manage.py                      # Django CLI
├── requirements.txt               # Dependencies
├── startup_analyzer/              # Django project settings
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
└── analyzer/                      # Main app
    ├── __init__.py
    ├── models.py                  # Project model
    ├── views.py                   # API views
    ├── urls.py                    # URL routing
    ├── serializers.py             # DRF serializers
    └── langgraph_workflow.py      # LangGraph multi-agent workflow
```

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
# Create .env file
echo "OPENAI_API_KEY=your_openai_key" > .env
echo "DJANGO_SECRET_KEY=your-secret-key-here" >> .env

# Or export directly
export OPENAI_API_KEY=your_openai_key
export DJANGO_SECRET_KEY=your-secret-key-here
```

4. **Run migrations**
```bash
python manage.py migrate
```

5. **Run the development server**
```bash
python manage.py runserver 0.0.0.0:8000
```

## API Endpoints

### `GET /`
API information and available endpoints.

### `GET /health`
Health check endpoint.

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

### `GET /projects`
List all projects.

### `POST /projects`
Create a new project.

### `GET /projects/{id}`
Get project details.

### `DELETE /projects/{id}`
Delete a project.

## Deployment

### Railway
1. Create new project on railway.app
2. Connect your GitHub repo
3. Set environment variables:
   - `OPENAI_API_KEY`
   - `DJANGO_SECRET_KEY`
4. Start command: `gunicorn startup_analyzer.wsgi:application --bind 0.0.0.0:$PORT`

### Render
1. Create new Web Service on render.com
2. Connect GitHub repo
3. Build command: `pip install -r requirements.txt && python manage.py migrate`
4. Start command: `gunicorn startup_analyzer.wsgi:application`

### Docker
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
RUN python manage.py migrate

EXPOSE 8000
CMD ["gunicorn", "startup_analyzer.wsgi:application", "--bind", "0.0.0.0:8000"]
```

### Heroku
```bash
# Create Procfile
echo "web: gunicorn startup_analyzer.wsgi:application" > Procfile

# Deploy
heroku create
heroku config:set OPENAI_API_KEY=your_key
heroku config:set DJANGO_SECRET_KEY=your_secret
git push heroku main
```

## LangGraph Workflow Architecture

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

## Using with Lovable Frontend

Once deployed, update your Lovable frontend to call your Django backend:

1. Get your deployed API URL (e.g., `https://your-app.railway.app`)
2. Update the frontend API calls to use this URL
