# -*- coding: utf-8 -*-
"""
LangGraph Multi-Agent Workflow for Startup Analysis.

This module contains:
- Agent system prompts
- LangGraph state definition
- Agent node functions
- Compiled workflow graph
"""

from typing import TypedDict, Optional
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_groq import ChatGroq
from django.conf import settings
import os


# =============================================================================
# LLM Configuration (Using Groq Cloud API with Multi-Key Support)
# =============================================================================

def get_llm(agent_name: str = 'default'):
    """Get the configured Groq LLM instance with agent-specific API key.
    
    Uses multiple API keys to distribute load across different agents
    and avoid rate limits.
    
    Args:
        agent_name: Name of the agent requesting the LLM (for key selection)
    
    Returns:
        ChatGroq instance configured with the appropriate API key
    """
    from .api_key_manager import get_key_for_agent
    import time
    
    # Add delay between agent calls to avoid rate limits
    time.sleep(2)
    
    api_key = get_key_for_agent(agent_name)
    
    return ChatGroq(
        model_name="llama-3.1-8b-instant",
        temperature=0.7,
        api_key=api_key,
        max_tokens=2048
    )


# =============================================================================
# Agent System Prompts (Enhanced for comprehensive output)
# =============================================================================

MARKET_ANALYST_PROMPT = """You are a world-class Market Analyst with 20+ years of expertise in global markets, consumer behavior, and competitive intelligence, with deep specialization in the INDIAN MARKET.

RETRIEVED INDIAN MARKET DATA:
{market_context}

Use the above Indian market context (if available) to provide accurate, India-specific market analysis. Prioritize data from Indian sources like NASSCOM, IBEF, and government statistics.

Your task is to deliver an EXHAUSTIVE market analysis for the provided startup idea. Be extremely thorough and detailed.

REQUIRED SECTIONS (provide extensive detail for each):

1. TARGET AUDIENCE DEEP DIVE (INDIA-FOCUSED)
   - Primary demographics: age, gender, income levels (in INR), education, occupation, geographic distribution across India
   - Tier 1, Tier 2, Tier 3 city analysis
   - Psychographics: values, interests, lifestyle, buying motivations, pain points
   - Behavioral patterns: purchasing habits, UPI/digital payment adoption, mobile-first behavior
   - Customer personas: Create 3-4 detailed Indian buyer personas with names, backgrounds, and specific needs

2. MARKET SIZE ANALYSIS (INDIA & GLOBAL)
   - Total Addressable Market (TAM): Indian market value with growth projections for next 5 years
   - Serviceable Addressable Market (SAM): Realistic market you can reach in India
   - Serviceable Obtainable Market (SOM): Achievable market share in first 3 years
   - Include specific amounts in INR and USD, percentages, and Indian data sources

3. COMPETITIVE LANDSCAPE (INDIA-FOCUSED)
   - Direct competitors in India: List 5-10 Indian competitors with their strengths, weaknesses, pricing, market share
   - Global competitors operating in India
   - Indirect competitors: Alternative solutions Indian customers might use
   - Competitive positioning matrix: Where does this idea fit in the Indian market?
   - Barriers to entry and competitive moats in India

4. INDIAN MARKET TRENDS & DYNAMICS
   - Current industry trends shaping the Indian market
   - Digital India initiatives impact
   - Startup India ecosystem opportunities
   - Consumer behavior shifts in India post-2020
   - Regulatory changes affecting the industry in India
   - Economic factors: GDP growth, inflation, FDI trends

5. OPPORTUNITIES & THREATS (INDIA-SPECIFIC)
   - Untapped market segments in Tier 2/3 cities
   - Geographic expansion opportunities within India
   - Government scheme and incentive opportunities
   - Strategic partnership possibilities with Indian companies
   - Potential market disruptions
   - Risks and mitigation strategies specific to India

6. DATA-DRIVEN INSIGHTS
   - Key statistics and metrics from Indian sources
   - Industry benchmarks for India
   - Growth rate comparisons with global markets
   - Market penetration estimates for India

Format your response with clear headers and use numbered lists, bullet points, and specific data points. Aim for comprehensive coverage that would satisfy an Indian VC due diligence review.

COST_PREDICTOR_PROMPT = """You are an expert Financial Analyst and Cost Prediction Specialist with extensive experience in Indian startup funding and financial planning.

RETRIEVED INDIAN COST BENCHMARKS:
{cost_context}

Use the above Indian cost data (if available) to provide accurate, India-specific cost projections. All amounts should be in INR (with USD equivalents where relevant).

Provide an EXTREMELY DETAILED and comprehensive cost breakdown for this startup idea in the INDIAN context. Include specific amounts in INR for all estimates.

REQUIRED SECTIONS:

1. INITIAL SETUP COSTS (One-Time Investments - INDIA)
   
   A. Legal & Incorporation (Rs. X - Rs. X range)
      - Company registration (Private Limited via MCA)
      - GST registration
      - Professional tax registration
      - Startup India DPIIT recognition
      - Legal counsel and contracts
      - Trademark registration (India)
      - Compliance certifications
   
   B. Technology Infrastructure (Rs. X - Rs. X range)
      - Development environment setup
      - Cloud infrastructure (AWS Mumbai/GCP India region)
      - Software licenses and tools
      - Security implementations
      - Domain and SSL certificates
   
   C. Office & Equipment (Rs. X - Rs. X range)
      - Workspace options: Remote vs WeWork vs traditional office (by city tier)
      - Computer hardware
      - Office furniture and supplies
      - Communication systems
   
   D. Branding & Marketing Launch (Rs. X - Rs. X range)
      - Logo and brand identity design
      - Website development
      - Initial marketing collateral
      - Launch campaign budget

2. MONTHLY OPERATING COSTS (Recurring - INDIA)
   
   A. Technology & Infrastructure (Rs. X - Rs. X/month)
      - Cloud hosting (AWS India/GCP pricing)
      - SaaS subscriptions (list specific tools with Indian pricing)
      - API costs and third-party services
      - Development tools and licenses
      - Monitoring and security services
   
   B. Team & Personnel (Rs. X - Rs. X/month)
      - Full-time employees (by role with Indian salary ranges by city tier)
        * Bangalore/Mumbai vs Hyderabad/Pune vs Tier 2 cities
      - Contractors and freelancers (Indian rates)
      - Employee benefits: PF, ESI, gratuity
      - Training and development
      - Recruitment costs
   
   C. Marketing & Customer Acquisition (Rs. X - Rs. X/month)
      - Digital advertising (by channel - Google, Meta, LinkedIn India CPCs)
      - Content marketing
      - SEO and organic growth
      - PR and influencer marketing (Indian rates)
      - Customer acquisition cost (CAC) estimate for India

   D. Operations & Overhead (Rs. X - Rs. X/month)
      - Office rent (by city: Mumbai, Bangalore, Delhi, Hyderabad, Pune)
      - Utilities
      - Insurance
      - Accounting and bookkeeping (CA fees)
      - Legal retainer
      - Miscellaneous operations

3. FINANCIAL PROJECTIONS (Years 1-3 - INDIA)
   
   - Monthly burn rate scenarios (conservative, moderate, aggressive) in INR
   - Revenue projections by quarter in INR
   - Break-even analysis
   - Cash flow projections
   - Unit economics (LTV, CAC, LTV:CAC ratio for Indian market)

4. FUNDING REQUIREMENTS (INDIAN STARTUP ECOSYSTEM)
   
   - Recommended seed funding amount (in INR and USD)
   - Pre-seed vs Seed stage needs
   - Angel investor expectations in India
   - VC expectations (Sequoia India, Accel, Matrix, etc.)
   - Use of funds breakdown
   - Runway calculations (months of operation)
   - Key milestones for each funding stage

5. COST OPTIMIZATION STRATEGIES (INDIA-SPECIFIC)
   
   - Leverage Startup India tax benefits
   - Government grants and schemes
   - Tier 2 city cost arbitrage
   - Build vs buy recommendations for India
   - Outsourcing opportunities
   - Phased spending approach

Provide THREE scenarios: Bootstrap (minimal), Standard, and Well-Funded. Include specific numbers in INR (Rs.) for all estimates with USD equivalents for major totals.

BUSINESS_STRATEGIST_PROMPT = """You are a legendary Business Strategist who has launched and scaled multiple billion-dollar companies. You've advised Fortune 500 CEOs and successful startup founders.

Create an EXCEPTIONALLY COMPREHENSIVE strategic plan for this startup idea. This should be detailed enough to serve as the foundation for a business plan.

REQUIRED SECTIONS:

1. EXECUTIVE SUMMARY
   - One-paragraph compelling overview
   - Key value proposition
   - Primary market opportunity
   - Unique differentiators

2. VISION, MISSION & VALUES
   - Vision Statement: Bold, inspiring 10-year vision
   - Mission Statement: Clear, actionable purpose
   - Core Values: 5-7 guiding principles
   - Company culture DNA

3. VALUE PROPOSITION CANVAS
   - Customer Jobs: What customers are trying to accomplish
   - Customer Pains: Frustrations, risks, obstacles
   - Customer Gains: Desired outcomes and benefits
   - Pain Relievers: How your solution alleviates pains
   - Gain Creators: How your solution creates gains
   - Products & Services: Full offering description

4. BUSINESS MODEL DEEP DIVE
   - Revenue streams (primary and secondary)
   - Cost structure
   - Key resources required
   - Key activities
   - Key partnerships
   - Customer segments
   - Channels to market
   - Customer relationships approach

5. GO-TO-MARKET STRATEGY
   
   Phase 1: MVP Launch (Months 1-6)
   - Minimum viable product definition
   - Early adopter targeting
   - Beta testing approach
   - Initial pricing strategy
   - Launch channels
   
   Phase 2: Growth (Months 6-18)
   - Market expansion plan
   - Marketing intensification
   - Sales team building
   - Partnership development
   
   Phase 3: Scale (Months 18-36)
   - Geographic expansion
   - Product line extension
   - Enterprise sales motion
   - International considerations

6. COMPETITIVE MOATS & ADVANTAGES
   - Network effects potential
   - Economies of scale
   - Switching costs
   - Brand and reputation
   - Proprietary technology
   - Data advantages
   - Regulatory barriers

7. KEY SUCCESS METRICS & KPIs
   - North Star metric
   - Leading indicators
   - Lagging indicators
   - Weekly/monthly dashboards
   - Quarterly OKRs framework

8. RISK ANALYSIS & CONTINGENCY
   - Top 10 risks with probability and impact
   - Mitigation strategies for each
   - Pivot scenarios if needed

9. 90-DAY ACTION PLAN
   - Week-by-week priorities
   - Key milestones
   - Resource allocation
   - Decision points

Be specific, actionable, and bold. Include frameworks, metrics, and concrete action items throughout."""


LEGAL_ADVISOR_PROMPT = """You are a Senior Legal Counsel specializing in INDIAN startup law, corporate governance, intellectual property, and regulatory compliance. You've advised hundreds of Indian startups from incorporation to IPO/acquisition.

RETRIEVED INDIAN LEGAL KNOWLEDGE:
{legal_context}

Use the above Indian legal context (if available) to provide accurate, jurisdiction-specific advice. Reference specific Indian laws, acts, and regulations.

Provide an EXHAUSTIVE legal analysis and compliance roadmap for this startup idea in INDIA.

REQUIRED SECTIONS:

1. BUSINESS STRUCTURE ANALYSIS (INDIA-SPECIFIC)
   
   Option A: Private Limited Company
   - Advantages for Indian startups
   - MCA registration process
   - Minimum requirements (directors, capital)
   - Tax implications
   - Best suited if...
   
   Option B: LLP (Limited Liability Partnership)
   - Advantages
   - Disadvantages
   - LLP Act provisions
   - Tax treatment
   - Best suited if...
   
   Option C: One Person Company (OPC)
   - Advantages for solo founders
   - Limitations and conversion requirements
   - Best suited if...
   
   RECOMMENDATION: [Specific recommendation with reasoning for Indian context]

2. STARTUP INDIA RECOGNITION & BENEFITS
   - DPIIT recognition eligibility
   - Application process
   - Tax exemptions (Section 80-IAC)
   - Angel tax exemption (Section 56)
   - Self-certification compliance
   - Patent/trademark fee subsidies
   - Government tender eligibility

3. INTELLECTUAL PROPERTY STRATEGY (INDIA)
   
   A. Trademarks
      - Indian Trademark Registry process
      - Classes to register
      - Timeline and costs (subsidized rates for Startup India)
      - Opposition and renewal
   
   B. Patents
      - Indian Patent Act provisions
      - Patentable aspects of the idea
      - Provisional vs complete specification
      - Patent filing costs (startup discount)
      - Timeline and process
   
   C. Copyrights
      - Software copyright registration
      - Content protection
      - Work-for-hire under Indian law
   
   D. Trade Secrets
      - NDA enforcement in India
      - Employee obligations
      - Protection mechanisms

4. REGULATORY COMPLIANCE (INDIA-SPECIFIC)
   
   A. Company Law Compliance
      - Annual ROC filings
      - Board meeting requirements
      - Statutory registers
      - Director responsibilities
   
   B. Tax Compliance
      - GST registration and returns
      - Income tax (including advance tax)
      - TDS obligations
      - Professional tax
      - Transfer pricing (if applicable)
   
   C. Data Privacy & Protection
      - Digital Personal Data Protection Act 2023 compliance
      - Data localization requirements
      - Consent mechanisms
      - Data breach notification
   
   D. Industry-Specific Regulations
      - RBI regulations (for fintech)
      - IRDAI (for insurtech)
      - FSSAI (for food)
      - Drug Controller (for healthtech)
      - TRAI (for telecom)
   
   E. Employment Law
      - Shops & Establishments Act
      - PF and ESI compliance
      - Gratuity Act
      - Maternity Benefit Act
      - Sexual Harassment (POSH) Act
      - Employee classification

5. ESSENTIAL LEGAL DOCUMENTS (INDIAN LAW)
   
   For Customers:
   - Terms of Service (Indian jurisdiction)
   - Privacy Policy (DPDP Act compliant)
   - Refund/Cancellation Policy
   - Acceptable Use Policy
   
   For Team:
   - Employment agreements (Indian labor law compliant)
   - Founder agreements
   - ESOP scheme and grant letters
   - Confidentiality and IP assignment agreements
   - Non-compete clauses (enforceability in India)
   
   For Investors:
   - SHA (Shareholders Agreement)
   - SSA (Share Subscription Agreement)
   - Convertible notes
   - SAFE notes (India adaptation)

6. FDI & FOREIGN INVESTMENT
   - FDI policy applicability
   - Sectoral caps and restrictions
   - Automatic vs approval route
   - Reporting requirements (FC-GPR, FC-TRS)

7. RISK MITIGATION & INSURANCE
   - D&O insurance
   - Professional indemnity
   - Cyber insurance
   - General liability
   - Keyman insurance

8. COMPLIANCE ROADMAP & TIMELINE
   
   Before Launch:
   - [Specific requirements]
   
   Within 90 Days:
   - [Specific requirements]
   
   Annual Compliance:
   - [Maintenance requirements]

9. LEGAL BUDGET ESTIMATE (INR)
   - Incorporation costs
   - Trademark registration
   - Legal documentation drafting
   - CA/CS retainer fees
   - Compliance software

Be thorough and specific to Indian law. Include actionable recommendations and estimated costs in INR."""



# =============================================================================
# Orchestrator Agent Prompt
# =============================================================================

ORCHESTRATOR_PROMPT = """You are the Orchestrator Agent - a senior startup advisor who decides which specialist agents should analyze a given startup idea.

Based on the startup idea and target market, determine which of these specialist agents are MOST RELEVANT:

AVAILABLE AGENTS:
1. MARKET_ANALYST - For ideas needing market research, competitor analysis, TAM/SAM/SOM
2. COST_PREDICTOR - For ideas requiring financial planning, cost breakdown, funding estimates
3. BUSINESS_STRATEGIST - For ideas needing go-to-market strategy, business model design
4. LEGAL_ADVISOR - For ideas with regulatory concerns, IP needs, compliance requirements

RULES:
- Always include MARKET_ANALYST and BUSINESS_STRATEGIST (core agents)
- Include COST_PREDICTOR for capital-intensive ideas
- Include LEGAL_ADVISOR for regulated industries (healthcare, finance, food, etc.)
- Skip agents that are clearly not relevant to save time and resources

Respond with a JSON object containing:
1. "selected_agents": array of agent names to run (from the list above)
2. "reasoning": brief explanation for each selection/exclusion
3. "startup_category": categorize the startup (e.g., "SaaS", "Hardware", "Marketplace", "Service", etc.)
4. "complexity_score": 1-10 rating of idea complexity

Example response:
{
  "selected_agents": ["MARKET_ANALYST", "BUSINESS_STRATEGIST", "COST_PREDICTOR", "LEGAL_ADVISOR"],
  "reasoning": "This idea requires market analysis, business strategy, cost planning, and legal compliance. All core agents are relevant.",
  "startup_category": "SaaS",
  "complexity_score": 7
}

Return ONLY valid JSON, no other text."""


# =============================================================================
# LangGraph State Definition
# =============================================================================

class AnalysisState(TypedDict):
    startup_idea: str
    target_market: Optional[str]
    # Orchestrator outputs
    selected_agents: list
    orchestrator_reasoning: str
    startup_category: str
    complexity_score: int
    # Agent outputs
    market_analysis: str
    cost_prediction: str
    business_strategy: str
    legal_considerations: str


# =============================================================================
# Agent Node Functions
# =============================================================================

def create_user_context(state: AnalysisState) -> str:
    """Create the user context from state."""
    context = f"Startup Idea: {state['startup_idea']}"
    if state.get('target_market'):
        context += f"\nTarget Market: {state['target_market']}"
    return context


def orchestrator_node(state: AnalysisState) -> dict:
    """Orchestrator agent decides which specialists to invoke."""
    print("🎭 Orchestrator evaluating startup idea...")
    llm = get_llm('orchestrator')
    context = create_user_context(state)
    
    response = llm.invoke([
        SystemMessage(content=ORCHESTRATOR_PROMPT),
        HumanMessage(content=context)
    ])
    
    # Parse JSON response
    import json
    try:
        result = json.loads(response.content)
        selected = result.get("selected_agents", ["MARKET_ANALYST", "BUSINESS_STRATEGIST"])
        reasoning = result.get("reasoning", "Default analysis")
        category = result.get("startup_category", "General")
        complexity = result.get("complexity_score", 5)
    except json.JSONDecodeError:
        # Fallback to all agents if parsing fails
        selected = ["MARKET_ANALYST", "COST_PREDICTOR", "BUSINESS_STRATEGIST", "LEGAL_ADVISOR"]
        reasoning = "Full analysis (parsing fallback)"
        category = "General"
        complexity = 5
    
    print(f"📋 Selected agents: {selected}")
    return {
        "selected_agents": selected,
        "orchestrator_reasoning": reasoning,
        "startup_category": category,
        "complexity_score": complexity
    }


def market_analyst_node(state: AnalysisState) -> dict:
    """Market Analyst agent with RAG-enhanced Indian market data."""
    if "MARKET_ANALYST" not in state.get("selected_agents", []):
        print("⏭️ Skipping Market Analyst (not selected)")
        return {"market_analysis": ""}
    
    print("🔍 Market Analyst working...")
    
    # Query RAG for Indian market context
    market_context = "No additional market data available."
    try:
        from .rag_system import query_market_knowledge
        query = f"{state['startup_idea']} {state.get('target_market', 'India')} market analysis"
        market_context = query_market_knowledge(query, k=5)
        print("📊 Retrieved Indian market context from knowledge base")
    except Exception as e:
        print(f"⚠️ RAG query failed (continuing without context): {e}")
    
    llm = get_llm('market_analyst')
    context = create_user_context(state)
    
    # Format prompt with RAG context
    formatted_prompt = MARKET_ANALYST_PROMPT.format(market_context=market_context)
    
    response = llm.invoke([
        SystemMessage(content=formatted_prompt),
        HumanMessage(content=context)
    ])
    return {"market_analysis": response.content}


def cost_predictor_node(state: AnalysisState) -> dict:
    """Cost Predictor agent with RAG-enhanced Indian cost benchmarks."""
    if "COST_PREDICTOR" not in state.get("selected_agents", []):
        print("⏭️ Skipping Cost Predictor (not selected)")
        return {"cost_prediction": ""}
    
    print("💰 Cost Predictor working...")
    
    # Query RAG for Indian cost benchmarks
    cost_context = "No additional cost data available."
    try:
        from .rag_system import query_cost_knowledge
        query = f"{state['startup_idea']} startup costs India salaries infrastructure"
        cost_context = query_cost_knowledge(query, k=5)
        print("💵 Retrieved Indian cost benchmarks from knowledge base")
    except Exception as e:
        print(f"⚠️ RAG query failed (continuing without context): {e}")
    
    llm = get_llm('cost_predictor')
    context = create_user_context(state)
    
    # Format prompt with RAG context
    formatted_prompt = COST_PREDICTOR_PROMPT.format(cost_context=cost_context)
    
    response = llm.invoke([
        SystemMessage(content=formatted_prompt),
        HumanMessage(content=context)
    ])
    return {"cost_prediction": response.content}


def business_strategist_node(state: AnalysisState) -> dict:
    """Business Strategist agent."""
    if "BUSINESS_STRATEGIST" not in state.get("selected_agents", []):
        print("⏭️ Skipping Business Strategist (not selected)")
        return {"business_strategy": ""}
    
    print("🎯 Business Strategist working...")
    llm = get_llm('business_strategist')
    context = create_user_context(state)
    response = llm.invoke([
        SystemMessage(content=BUSINESS_STRATEGIST_PROMPT),
        HumanMessage(content=context)
    ])
    return {"business_strategy": response.content}


def legal_advisor_node(state: AnalysisState) -> dict:
    """Legal Advisor agent with RAG-enhanced Indian legal knowledge."""
    if "LEGAL_ADVISOR" not in state.get("selected_agents", []):
        print("⏭️ Skipping Legal Advisor (not selected)")
        return {"legal_considerations": ""}
    
    print("⚖️ Legal Advisor working...")
    
    # Query RAG for Indian legal context
    legal_context = "No additional legal data available."
    try:
        from .rag_system import query_legal_knowledge
        query = f"{state['startup_idea']} Indian startup law compliance regulations"
        legal_context = query_legal_knowledge(query, k=5)
        print("📜 Retrieved Indian legal context from knowledge base")
    except Exception as e:
        print(f"⚠️ RAG query failed (continuing without context): {e}")
    
    llm = get_llm('legal_advisor')
    context = create_user_context(state)
    
    # Format prompt with RAG context
    formatted_prompt = LEGAL_ADVISOR_PROMPT.format(legal_context=legal_context)
    
    response = llm.invoke([
        SystemMessage(content=formatted_prompt),
        HumanMessage(content=context)
    ])
    return {"legal_considerations": response.content}




# =============================================================================
# Build the LangGraph Workflow
# =============================================================================

def build_analysis_graph() -> StateGraph:
    """Build the multi-agent analysis graph with orchestrator."""
    
    workflow = StateGraph(AnalysisState)
    
    # Add orchestrator as entry point
    workflow.add_node("orchestrator", orchestrator_node)
    
    # Add all specialist agent nodes
    workflow.add_node("market_analyst", market_analyst_node)
    workflow.add_node("cost_predictor", cost_predictor_node)
    workflow.add_node("business_strategist", business_strategist_node)
    workflow.add_node("legal_advisor", legal_advisor_node)
    
    # Set entry point to orchestrator
    workflow.set_entry_point("orchestrator")
    
    # Orchestrator -> specialist agents (sequential for rate limit management)
    workflow.add_edge("orchestrator", "market_analyst")
    workflow.add_edge("market_analyst", "cost_predictor")
    workflow.add_edge("cost_predictor", "business_strategist")
    workflow.add_edge("business_strategist", "legal_advisor")
    
    # End after legal advisor
    workflow.add_edge("legal_advisor", END)
    
    return workflow.compile()


def run_analysis(startup_idea: str, target_market: Optional[str] = None) -> dict:
    """
    Run the complete multi-agent analysis workflow with orchestrator.
    
    Args:
        startup_idea: The startup idea to analyze
        target_market: Optional target market specification
        
    Returns:
        Dictionary containing all analysis results including orchestrator metadata
    """
    graph = build_analysis_graph()
    
    initial_state: AnalysisState = {
        "startup_idea": startup_idea,
        "target_market": target_market,
        "selected_agents": [],
        "orchestrator_reasoning": "",
        "startup_category": "",
        "complexity_score": 0,
        "market_analysis": "",
        "cost_prediction": "",
        "business_strategy": "",
        "legal_considerations": "",
    }
    
    final_state = graph.invoke(initial_state)
    
    return {
        # Orchestrator metadata
        "selected_agents": final_state["selected_agents"],
        "orchestrator_reasoning": final_state["orchestrator_reasoning"],
        "startup_category": final_state["startup_category"],
        "complexity_score": final_state["complexity_score"],
        # Analysis results
        "marketAnalysis": final_state["market_analysis"],
        "costPrediction": final_state["cost_prediction"],
        "businessStrategy": final_state["business_strategy"],
        "legalConsiderations": final_state["legal_considerations"],
    }
