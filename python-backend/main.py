# =============================================================================
# STARTUP ANALYZER - LangGraph Backend
# =============================================================================
# Deploy this on Railway, Render, AWS Lambda, Google Cloud Run, or any Python host
# 
# Setup:
#   pip install -r requirements.txt
#   export OPENAI_API_KEY=your_key  (or GROQ_API_KEY for Groq)
#   uvicorn main:app --host 0.0.0.0 --port 8000
# =============================================================================

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, TypedDict, Annotated
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
# Alternatively use Groq:
# from langchain_groq import ChatGroq
import os

# =============================================================================
# FastAPI App Setup
# =============================================================================

app = FastAPI(title="Startup Analyzer API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for your frontend domain in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =============================================================================
# LLM Configuration
# =============================================================================

# Option 1: OpenAI
llm = ChatOpenAI(
    model="gpt-4o",
    temperature=0.7,
    api_key=os.getenv("OPENAI_API_KEY")
)

# Option 2: Groq (uncomment to use)
# from langchain_groq import ChatGroq
# llm = ChatGroq(
#     model_name="llama-3.1-70b-versatile",
#     temperature=0.7,
#     api_key=os.getenv("GROQ_API_KEY")
# )

# =============================================================================
# Agent System Prompts
# =============================================================================

MARKET_ANALYST_PROMPT = """You are a world-class Market Analyst with expertise in global markets.
Your task is to analyze the provided startup idea.
Focus on:
- Target audience demographics and psychographics
- Total Addressable Market (TAM), Serviceable Addressable Market (SAM), and Serviceable Obtainable Market (SOM)
- Key competitors and their market positioning
- Market trends and growth projections
- Potential market gaps and opportunities

Provide specific data points, percentages, and market size estimates where possible.
Format your response with clear headers and bullet points for easy reading."""

COST_PREDICTOR_PROMPT = """You are an expert Cost Prediction Specialist for startups.
Analyze the startup idea and provide a comprehensive breakdown of potential costs.

Include these categories:
1. **Initial Setup Costs** (one-time)
   - Legal & incorporation
   - Technology infrastructure
   - Office/workspace setup
   
2. **Monthly Operating Costs**
   - Technology (hosting, tools, subscriptions)
   - Team (salaries, contractors)
   - Marketing & customer acquisition
   - Operations & overhead

3. **Runway Planning**
   - Estimated monthly burn rate
   - Recommended initial funding
   - Time to breakeven estimate

Provide all estimates in USD with ranges (low/medium/high scenarios)."""

BUSINESS_STRATEGIST_PROMPT = """You are a seasoned Business Strategist who has launched multiple successful companies.
Based on the startup idea, outline a comprehensive strategic plan including:

1. **Mission & Vision Statement** - Clear, inspiring, and actionable
2. **Value Proposition Canvas** - What pain points you solve and gains you create
3. **Business Model** - How the business creates, delivers, and captures value
4. **Go-to-Market Strategy**
   - Launch phases (MVP, growth, scale)
   - Target market prioritization
   - Distribution channels
5. **Competitive Moats** - Sustainable competitive advantages
6. **Key Success Metrics** - KPIs to track progress

Be specific and actionable in your recommendations."""

MONETIZATION_PROMPT = """You are a Monetization Strategy expert with experience in various business models.
Propose three distinct monetization models for this startup idea.

For each model, provide:
1. **Model Name & Description**
2. **Pricing Strategy** - Specific price points and tiers
3. **Revenue Projections** - Year 1, Year 2, Year 3 estimates
4. **Pros & Cons** - Benefits and challenges
5. **Implementation Complexity** - Easy, Medium, Hard
6. **Best Suited For** - Which customer segments

Consider: subscriptions, freemium, marketplace fees, licensing, advertising, and hybrid models."""

LEGAL_ADVISOR_PROMPT = """You are an expert Legal Counsel specializing in startup law and compliance.
Analyze the startup idea from a legal and regulatory perspective.

Cover these areas:
1. **Business Structure Recommendation** (LLC, C-Corp, S-Corp, etc.) with pros/cons
2. **Intellectual Property Protection**
   - Trademarks, patents, copyrights needed
   - Trade secret protection strategies
3. **Regulatory Compliance**
   - Industry-specific regulations
   - Data privacy (GDPR, CCPA, etc.)
   - Consumer protection laws
4. **Key Legal Documents Needed**
   - Terms of Service
   - Privacy Policy
   - User agreements
   - Contractor/employee agreements
5. **Risk Mitigation** - Potential legal pitfalls to avoid

Provide actionable steps for legal compliance."""

TECH_ARCHITECT_PROMPT = """You are a senior Technology Architect specializing in building scalable MVPs.
Based on the startup idea, recommend a comprehensive technology stack.

Provide recommendations for:
1. **Frontend**
   - Framework/library choice with justification
   - UI component approach
   - State management

2. **Backend**
   - Language and framework
   - API architecture (REST, GraphQL, etc.)
   - Authentication/authorization approach

3. **Database**
   - Database type and specific technology
   - Data modeling considerations
   - Scaling strategy

4. **Infrastructure**
   - Cloud provider recommendation
   - Hosting architecture
   - CI/CD pipeline

5. **Third-party Services**
   - Payment processing
   - Email/notifications
   - Analytics

6. **MVP Timeline & Team**
   - Estimated development time
   - Recommended team composition

Justify each choice based on scalability, cost, and speed of development."""

STRATEGIST_PROMPT = """You are a Senior Business Strategist synthesizing insights from multiple expert analyses.
Based on all the analyses provided, create a refined and actionable strategic plan.

Your synthesis should:
1. Identify the most critical insights from each analysis
2. Find synergies and connections between different recommendations
3. Prioritize actions based on impact and feasibility
4. Create a phased implementation roadmap
5. Highlight key risks and mitigation strategies
6. Provide specific, measurable goals for the first 90 days

Be bold but practical in your recommendations."""

CRITIC_PROMPT = """You are a Devil's Advocate and Critical Analyst.
Your role is to stress-test the strategic plan and identify weaknesses.

Critically analyze:
1. **Assumptions** - What unverified assumptions is this plan based on?
2. **Risks** - What could go wrong? What are the biggest threats?
3. **Gaps** - What's missing from the analysis?
4. **Market Reality Check** - Is this truly viable in the current market?
5. **Execution Challenges** - What will be hardest to actually do?
6. **Alternative Perspectives** - What other approaches might work better?

Be constructively critical - identify problems AND suggest solutions.
Your goal is to make the final plan stronger by exposing weaknesses now."""

# =============================================================================
# LangGraph State Definition
# =============================================================================

class AnalysisState(TypedDict):
    startup_idea: str
    target_market: Optional[str]
    market_analysis: str
    cost_prediction: str
    business_strategy: str
    monetization: str
    legal_considerations: str
    tech_stack: str
    strategist_synthesis: str
    critic_review: str
    final_strategy: str

# =============================================================================
# Agent Node Functions
# =============================================================================

def create_user_context(state: AnalysisState) -> str:
    """Create the user context from state."""
    context = f"Startup Idea: {state['startup_idea']}"
    if state.get('target_market'):
        context += f"\nTarget Market: {state['target_market']}"
    return context

def market_analyst_node(state: AnalysisState) -> dict:
    """Market Analyst agent."""
    print("🔍 Market Analyst working...")
    context = create_user_context(state)
    response = llm.invoke([
        SystemMessage(content=MARKET_ANALYST_PROMPT),
        HumanMessage(content=context)
    ])
    return {"market_analysis": response.content}

def cost_predictor_node(state: AnalysisState) -> dict:
    """Cost Predictor agent."""
    print("💰 Cost Predictor working...")
    context = create_user_context(state)
    response = llm.invoke([
        SystemMessage(content=COST_PREDICTOR_PROMPT),
        HumanMessage(content=context)
    ])
    return {"cost_prediction": response.content}

def business_strategist_node(state: AnalysisState) -> dict:
    """Business Strategist agent."""
    print("🎯 Business Strategist working...")
    context = create_user_context(state)
    response = llm.invoke([
        SystemMessage(content=BUSINESS_STRATEGIST_PROMPT),
        HumanMessage(content=context)
    ])
    return {"business_strategy": response.content}

def monetization_node(state: AnalysisState) -> dict:
    """Monetization Expert agent."""
    print("💳 Monetization Expert working...")
    context = create_user_context(state)
    response = llm.invoke([
        SystemMessage(content=MONETIZATION_PROMPT),
        HumanMessage(content=context)
    ])
    return {"monetization": response.content}

def legal_advisor_node(state: AnalysisState) -> dict:
    """Legal Advisor agent."""
    print("⚖️ Legal Advisor working...")
    context = create_user_context(state)
    response = llm.invoke([
        SystemMessage(content=LEGAL_ADVISOR_PROMPT),
        HumanMessage(content=context)
    ])
    return {"legal_considerations": response.content}

def tech_architect_node(state: AnalysisState) -> dict:
    """Tech Architect agent."""
    print("💻 Tech Architect working...")
    context = create_user_context(state)
    response = llm.invoke([
        SystemMessage(content=TECH_ARCHITECT_PROMPT),
        HumanMessage(content=context)
    ])
    return {"tech_stack": response.content}

def strategist_synthesis_node(state: AnalysisState) -> dict:
    """Strategist synthesizes all agent outputs."""
    print("🔮 Strategist synthesizing insights...")
    
    synthesis_context = f"""
Original Startup Idea: {state['startup_idea']}
{f"Target Market: {state['target_market']}" if state.get('target_market') else ""}

=== MARKET ANALYSIS ===
{state['market_analysis']}

=== COST PREDICTION ===
{state['cost_prediction']}

=== BUSINESS STRATEGY ===
{state['business_strategy']}

=== MONETIZATION MODELS ===
{state['monetization']}

=== LEGAL CONSIDERATIONS ===
{state['legal_considerations']}

=== TECHNOLOGY STACK ===
{state['tech_stack']}
"""
    
    response = llm.invoke([
        SystemMessage(content=STRATEGIST_PROMPT),
        HumanMessage(content=synthesis_context)
    ])
    return {"strategist_synthesis": response.content}

def critic_review_node(state: AnalysisState) -> dict:
    """Critic reviews and challenges the strategist's plan."""
    print("🔍 Critic reviewing the plan...")
    
    critic_context = f"""
Original Startup Idea: {state['startup_idea']}

=== STRATEGIST'S SYNTHESIZED PLAN ===
{state['strategist_synthesis']}

=== KEY DATA FROM ANALYSES ===
Market Analysis Summary: {state['market_analysis'][:1000]}...
Cost Estimates: {state['cost_prediction'][:1000]}...
"""
    
    response = llm.invoke([
        SystemMessage(content=CRITIC_PROMPT),
        HumanMessage(content=critic_context)
    ])
    return {"critic_review": response.content}

def final_refinement_node(state: AnalysisState) -> dict:
    """Strategist refines plan based on critic feedback."""
    print("✨ Generating final refined strategy...")
    
    refinement_prompt = """You are the Senior Business Strategist again.
Review the Critic's feedback and refine your strategic plan.
Address the valid concerns raised while maintaining the core strategy's strengths.
Create a FINAL, battle-tested strategic plan."""

    refinement_context = f"""
=== YOUR ORIGINAL SYNTHESIZED PLAN ===
{state['strategist_synthesis']}

=== CRITIC'S REVIEW ===
{state['critic_review']}

Based on this feedback, provide a refined final strategy that addresses the valid concerns while maintaining strategic coherence.
"""
    
    response = llm.invoke([
        SystemMessage(content=refinement_prompt),
        HumanMessage(content=refinement_context)
    ])
    return {"final_strategy": response.content}

# =============================================================================
# Build the LangGraph Workflow
# =============================================================================

def build_analysis_graph() -> StateGraph:
    """Build the multi-agent analysis graph."""
    
    workflow = StateGraph(AnalysisState)
    
    # Add all agent nodes
    workflow.add_node("market_analyst", market_analyst_node)
    workflow.add_node("cost_predictor", cost_predictor_node)
    workflow.add_node("business_strategist", business_strategist_node)
    workflow.add_node("monetization", monetization_node)
    workflow.add_node("legal_advisor", legal_advisor_node)
    workflow.add_node("tech_architect", tech_architect_node)
    workflow.add_node("strategist_synthesis", strategist_synthesis_node)
    workflow.add_node("critic_review", critic_review_node)
    workflow.add_node("final_refinement", final_refinement_node)
    
    # Set entry point - all 6 agents run in parallel conceptually
    # (LangGraph will handle this based on the edges)
    workflow.set_entry_point("market_analyst")
    
    # Phase 1: Run 6 specialist agents (sequential for simplicity, can be parallelized)
    workflow.add_edge("market_analyst", "cost_predictor")
    workflow.add_edge("cost_predictor", "business_strategist")
    workflow.add_edge("business_strategist", "monetization")
    workflow.add_edge("monetization", "legal_advisor")
    workflow.add_edge("legal_advisor", "tech_architect")
    
    # Phase 2: Strategist synthesizes all outputs
    workflow.add_edge("tech_architect", "strategist_synthesis")
    
    # Phase 3: Critic reviews the synthesis
    workflow.add_edge("strategist_synthesis", "critic_review")
    
    # Phase 4: Final refinement based on criticism
    workflow.add_edge("critic_review", "final_refinement")
    
    # End the workflow
    workflow.add_edge("final_refinement", END)
    
    return workflow.compile()

# Create the compiled graph
analysis_graph = build_analysis_graph()

# =============================================================================
# API Request/Response Models
# =============================================================================

class AnalysisRequest(BaseModel):
    startupIdea: str
    targetMarket: Optional[str] = None
    projectId: Optional[str] = None

class AnalysisResponse(BaseModel):
    success: bool
    projectId: Optional[str]
    analysis: dict
    error: Optional[str] = None

# =============================================================================
# API Endpoints
# =============================================================================

@app.get("/")
async def root():
    return {"message": "Startup Analyzer API - LangGraph Backend", "version": "1.0.0"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.post("/analyze", response_model=AnalysisResponse)
async def analyze_startup(request: AnalysisRequest):
    """
    Analyze a startup idea using the multi-agent LangGraph workflow.
    """
    try:
        print(f"📊 Starting analysis for: {request.startupIdea[:100]}...")
        
        # Initialize state
        initial_state: AnalysisState = {
            "startup_idea": request.startupIdea,
            "target_market": request.targetMarket,
            "market_analysis": "",
            "cost_prediction": "",
            "business_strategy": "",
            "monetization": "",
            "legal_considerations": "",
            "tech_stack": "",
            "strategist_synthesis": "",
            "critic_review": "",
            "final_strategy": "",
        }
        
        # Run the graph
        final_state = analysis_graph.invoke(initial_state)
        
        print("✅ Analysis complete!")
        
        return AnalysisResponse(
            success=True,
            projectId=request.projectId,
            analysis={
                "marketAnalysis": final_state["market_analysis"],
                "costPrediction": final_state["cost_prediction"],
                "businessStrategy": final_state["business_strategy"],
                "monetization": final_state["monetization"],
                "legalConsiderations": final_state["legal_considerations"],
                "techStack": final_state["tech_stack"],
                "strategistCritique": final_state["final_strategy"],
            }
        )
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# =============================================================================
# Run the server (for local development)
# =============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
