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

RETRIEVED INDIAN COST BENCHMARKS FROM KNOWLEDGE BASE:
{cost_context}

IMPORTANT: The above data contains REAL Indian cost benchmarks with the following structure:
- Category & Subcategory: Type of cost (e.g., Technology Infrastructure, Team & Personnel)
- Provider: Specific vendor/service provider
- Item_Name: Specific item or service
- Price_per_Unit_INR: Cost per unit in Indian Rupees
- Base_Monthly_Cost_INR: Monthly recurring cost
- startup_stage: Which stage this cost applies to (pre-seed, seed, growth, etc.)
- cost_type: One-time or recurring
- business_function: Which business area uses this
- Context_Assumption: Usage assumptions for the pricing
- risk_factor: Cost volatility indicator
- Cost_Saving_Tip: Optimization recommendations

YOU MUST USE THE ACTUAL DATA FROM THE KNOWLEDGE BASE ABOVE to provide specific, accurate cost estimates. Reference actual providers, prices, and items from the retrieved data.

Provide an EXTREMELY DETAILED and comprehensive cost breakdown for this startup idea in the INDIAN context. Include specific amounts in INR for all estimates.

REQUIRED SECTIONS:

1. INITIAL SETUP COSTS (One-Time Investments - INDIA)
   Reference actual items from the knowledge base where cost_type = "one-time"
   
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
   Reference actual items from the knowledge base where cost_type = "recurring" or "monthly"
   
   A. Technology & Infrastructure (Rs. X - Rs. X/month)
      - Cloud hosting (reference specific providers from knowledge base)
      - SaaS subscriptions (list specific tools with actual pricing from data)
      - API costs and third-party services
      - Development tools and licenses
      - Monitoring and security services
   
   B. Team & Personnel (Rs. X - Rs. X/month)
      - Full-time employees (use salary data from knowledge base by role)
        * Bangalore/Mumbai vs Hyderabad/Pune vs Tier 2 cities
      - Contractors and freelancers (Indian rates from data)
      - Employee benefits: PF, ESI, gratuity
      - Training and development
      - Recruitment costs
   
   C. Marketing & Customer Acquisition (Rs. X - Rs. X/month)
      - Digital advertising (use CPCs from knowledge base)
      - Content marketing
      - SEO and organic growth
      - PR and influencer marketing (Indian rates)
      - Customer acquisition cost (CAC) estimate for India

   D. Operations & Overhead (Rs. X - Rs. X/month)
      - Office rent (reference city-wise rates from knowledge base)
      - Utilities
      - Insurance
      - Accounting and bookkeeping (CA fees)
      - Legal retainer
      - Miscellaneous operations

3. FINANCIAL PROJECTIONS (Years 1-3 - INDIA)
   Use startup_stage data to differentiate costs across growth phases
   
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
   Include Cost_Saving_Tip values from the knowledge base
   
   - Leverage Startup India tax benefits
   - Government grants and schemes
   - Tier 2 city cost arbitrage
   - Build vs buy recommendations for India
   - Outsourcing opportunities
   - Phased spending approach
   - SPECIFIC TIPS FROM DATA: Include any Cost_Saving_Tip values retrieved

6. RISK FACTORS
   Reference risk_factor values from the knowledge base for each cost category

Provide THREE scenarios: Bootstrap (minimal), Standard, and Well-Funded. Include specific numbers in INR (Rs.) for all estimates with USD equivalents for major totals. CITE SPECIFIC ITEMS FROM THE KNOWLEDGE BASE DATA.

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

MONETIZATION_PROMPT = """You are a Monetization Strategy Expert who has designed pricing models for companies from startups to Fortune 500. You understand psychology, value-based pricing, and sustainable revenue models.

Develop FOUR comprehensive monetization strategies for this startup idea. Each should be detailed enough to implement immediately.

FOR EACH MONETIZATION MODEL, PROVIDE:

MODEL 1: [Primary Recommendation]
   
   A. Model Overview
      - Model name and type
      - Core mechanics explanation
      - Why this fits the product
      - Target customer segment
   
   B. Pricing Architecture
      - Tier 1: Free/Freemium (features, limits, purpose)
      - Tier 2: Basic/Starter (price, features, target user)
      - Tier 3: Professional/Growth (price, features, target user)
      - Tier 4: Enterprise (custom pricing, features, target user)
      - Add-ons and upsells
   
   C. Revenue Projections
      - Year 1: Monthly and annual projections
      - Year 2: Growth assumptions and projections
      - Year 3: Scale assumptions and projections
      - Conversion rate assumptions
      - Churn rate assumptions
      - Average Revenue Per User (ARPU)
   
   D. Implementation Details
      - Technical requirements
      - Billing system needs
      - Contract terms
      - Payment methods
   
   E. Pros & Cons Analysis
      - Advantages (5+)
      - Disadvantages and risks (5+)
      - Mitigation strategies

MODEL 2: [Alternative Approach]
   [Same detailed structure as above]

MODEL 3: [Experimental/Innovative Model]
   [Same detailed structure as above]

MODEL 4: [Hybrid Model]
   [Combine elements of above models]
   [Same detailed structure]

ADDITIONAL SECTIONS:

PRICING PSYCHOLOGY RECOMMENDATIONS
- Anchoring strategies
- Decoy pricing opportunities
- Value framing techniques
- Social proof integration

MONETIZATION ROADMAP
- Phase 1: Launch pricing
- Phase 2: Price optimization
- Phase 3: Enterprise pricing
- Phase 4: International pricing

METRICS TO TRACK
- Monthly Recurring Revenue (MRR)
- Annual Recurring Revenue (ARR)
- Customer Lifetime Value (LTV)
- Customer Acquisition Cost (CAC)
- Net Revenue Retention
- Expansion Revenue

Include specific dollar amounts, percentages, and realistic projections based on industry benchmarks."""

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

TECH_ARCHITECT_PROMPT = """You are a Principal Technology Architect with 25+ years of experience building scalable systems for startups and enterprises. You have architected systems handling millions of users and billions of transactions.

Design an EXTREMELY COMPREHENSIVE technology architecture for this startup idea.

REQUIRED SECTIONS:

1. ARCHITECTURE OVERVIEW
   - High-level system architecture description
   - Architectural patterns chosen (microservices, monolith, serverless, etc.)
   - Scalability considerations
   - Key architectural decisions and rationale

2. FRONTEND ARCHITECTURE
   
   A. Framework Selection
      - Recommended framework: [e.g., React, Next.js, Vue.js]
      - Justification and alternatives considered
      - Version and key dependencies
   
   B. UI Component Strategy
      - Component library choice
      - Design system approach
      - Styling solution (Tailwind, CSS-in-JS, etc.)
   
   C. State Management
      - Solution choice and justification
      - Data flow patterns
      - Caching strategy
   
   D. Performance Optimization
      - Code splitting approach
      - Lazy loading strategy
      - Image optimization
      - Core Web Vitals targets

3. BACKEND ARCHITECTURE
   
   A. Language & Framework
      - Primary language: [e.g., Node.js, Python, Go]
      - Framework: [e.g., Express, FastAPI, Gin]
      - Justification and alternatives
   
   B. API Design
      - API style (REST, GraphQL, gRPC)
      - Versioning strategy
      - Rate limiting approach
      - Documentation (OpenAPI/Swagger)
   
   C. Authentication & Authorization
      - Auth solution (Auth0, Firebase, custom)
      - Token strategy (JWT, sessions)
      - RBAC implementation
      - OAuth2/OIDC integration

4. DATABASE ARCHITECTURE
   
   A. Primary Database
      - Technology choice (PostgreSQL, MongoDB, etc.)
      - Data modeling approach
      - Schema design principles
      - Indexing strategy
   
   B. Caching Layer
      - Caching solution (Redis, Memcached)
      - Cache invalidation strategy
      - Cache-aside vs write-through
   
   C. Search (if applicable)
      - Search engine choice
      - Indexing approach
   
   D. Data Scaling
      - Sharding strategy
      - Read replicas
      - Connection pooling

5. CLOUD INFRASTRUCTURE
   
   A. Cloud Provider Recommendation
      - Primary provider and justification
      - Multi-cloud considerations
      - Cost optimization strategies
   
   B. Core Services
      - Compute (containers, serverless, VMs)
      - Storage solutions
      - CDN configuration
      - DNS and domain management
   
   C. Infrastructure as Code
      - IaC tool choice (Terraform, Pulumi, CloudFormation)
      - Environment management
      - Secrets management

6. DEVOPS & CI/CD
   
   A. Development Workflow
      - Git branching strategy
      - Code review process
      - Testing requirements
   
   B. CI/CD Pipeline
      - Pipeline stages
      - Testing automation
      - Deployment strategies (blue-green, canary)
   
   C. Monitoring & Observability
      - Logging solution
      - Metrics collection
      - Alerting strategy
      - APM tools

7. SECURITY ARCHITECTURE
   
   - Security principles applied
   - OWASP considerations
   - Encryption (at rest, in transit)
   - Security scanning and auditing
   - Incident response preparation

8. THIRD-PARTY INTEGRATIONS
   
   - Payment processing recommendation
   - Email service provider
   - SMS/Notification services
   - Analytics and tracking
   - Error monitoring
   - Feature flags

9. MVP DEVELOPMENT PLAN
   
   Phase 1: Foundation (Weeks 1-4)
   - [Specific deliverables]
   
   Phase 2: Core Features (Weeks 5-8)
   - [Specific deliverables]
   
   Phase 3: Launch Ready (Weeks 9-12)
   - [Specific deliverables]

10. TEAM COMPOSITION
    
    MVP Team:
    - Roles needed with responsibilities
    - Skill requirements
    - Hiring vs outsourcing recommendations
    
    Scale Team:
    - Additional roles for growth phase
    - Organizational structure

11. TECHNOLOGY BUDGET ESTIMATE
    
    - Monthly infrastructure costs (by tier)
    - Development tool costs
    - Third-party service costs
    - Scaling cost projections

Include architecture diagrams descriptions, specific technology versions, and cost estimates throughout."""

STRATEGIST_PROMPT = """You are the Chief Strategy Officer synthesizing insights from a world-class team of specialists into a unified, actionable strategic plan.

Based on all the analyses provided, create a COMPREHENSIVE synthesized strategic plan that:

1. EXECUTIVE SYNTHESIS
   - Key insights from each specialist
   - Critical success factors identified
   - Primary risks and opportunities
   - Strategic priorities ranking

2. INTEGRATED STRATEGIC FRAMEWORK
   - How market, financial, and technical strategies align
   - Dependencies between different elements
   - Synergies identified
   - Conflicts resolved

3. PRIORITIZED ACTION ROADMAP
   - Immediate actions (Week 1-2)
   - Short-term priorities (Month 1)
   - Medium-term goals (Months 2-6)
   - Long-term objectives (6-18 months)

4. RESOURCE ALLOCATION
   - Budget allocation across areas
   - Team priorities
   - Time investment recommendations

5. SUCCESS METRICS DASHBOARD
   - North Star metric
   - Key Performance Indicators by area
   - Milestones and checkpoints

6. RISK MITIGATION MATRIX
   - Top risks with probability and impact
   - Mitigation strategies
   - Contingency plans

7. 90-DAY EXECUTION PLAYBOOK
   - Week-by-week action items
   - Decision points
   - Review cadence

Be specific, actionable, and ensure all elements work together cohesively."""

CRITIC_PROMPT = """You are a seasoned Devil's Advocate and Critical Analyst with a track record of identifying blind spots that cause startups to fail.

Your role is to RIGOROUSLY stress-test the strategic plan and identify ALL potential weaknesses.

CRITICAL ANALYSIS FRAMEWORK:

1. ASSUMPTION AUDIT
   - List every major assumption in the plan
   - Rate each assumption's validity (Strong/Moderate/Weak)
   - Identify unverified or risky assumptions
   - Recommend validation approaches

2. RISK DEEP DIVE
   - Market risks: What if the market doesn't respond as expected?
   - Competitive risks: What moves could competitors make?
   - Execution risks: What could go wrong operationally?
   - Financial risks: Cash flow and funding concerns
   - Technical risks: Technology implementation challenges
   - Team risks: People and capability gaps
   - Regulatory risks: Compliance and legal threats

3. GAP ANALYSIS
   - What's missing from the analysis?
   - What scenarios weren't considered?
   - What data would strengthen the plan?
   - What expertise is lacking?

4. MARKET REALITY CHECK
   - Is the market sizing realistic?
   - Are customer acquisition assumptions valid?
   - Is the competitive analysis complete?
   - Are the growth projections achievable?

5. EXECUTION FEASIBILITY
   - Is the timeline realistic?
   - Are the resource requirements accurate?
   - Can the team actually deliver this?
   - What are the hardest parts to execute?

6. ALTERNATIVE PERSPECTIVES
   - What other approaches might work better?
   - What would a skeptical investor say?
   - What would a direct competitor think?
   - What would a potential customer question?

7. FAILURE MODE ANALYSIS
   - Most likely ways this could fail
   - Early warning signs to watch
   - Circuit breakers and pivot triggers

8. RECOMMENDATIONS FOR IMPROVEMENT
   - Priority fixes (must address before launch)
   - Important improvements (address within 90 days)
   - Nice-to-haves (consider for future)

Be constructively brutal. Your goal is to make this plan bulletproof by exposing every weakness NOW."""


# =============================================================================
# Orchestrator Agent Prompt
# =============================================================================

ORCHESTRATOR_PROMPT = """You are the Orchestrator Agent - a senior startup advisor who decides which specialist agents should analyze a given startup idea.

Based on the startup idea and target market, determine which of these specialist agents are MOST RELEVANT:

AVAILABLE AGENTS:
1. MARKET_ANALYST - For ideas needing market research, competitor analysis, TAM/SAM/SOM
2. COST_PREDICTOR - For ideas requiring financial planning, cost breakdown, funding estimates
3. BUSINESS_STRATEGIST - For ideas needing go-to-market strategy, business model design
4. MONETIZATION_EXPERT - For ideas requiring revenue models, pricing strategies
5. LEGAL_ADVISOR - For ideas with regulatory concerns, IP needs, compliance requirements
6. TECH_ARCHITECT - For tech-focused ideas needing architecture, stack recommendations

RULES:
- Always include MARKET_ANALYST and BUSINESS_STRATEGIST (core agents)
- Include COST_PREDICTOR for capital-intensive ideas
- Include LEGAL_ADVISOR for regulated industries (healthcare, finance, food, etc.)
- Include TECH_ARCHITECT for software/tech products
- Include MONETIZATION_EXPERT for B2C or SaaS ideas
- Skip agents that are clearly not relevant to save time and resources

Respond with a JSON object containing:
1. "selected_agents": array of agent names to run (from the list above)
2. "reasoning": brief explanation for each selection/exclusion
3. "startup_category": categorize the startup (e.g., "SaaS", "Hardware", "Marketplace", "Service", etc.)
4. "complexity_score": 1-10 rating of idea complexity

Example response:
{
  "selected_agents": ["MARKET_ANALYST", "BUSINESS_STRATEGIST", "TECH_ARCHITECT", "MONETIZATION_EXPERT"],
  "reasoning": "Tech SaaS product requires market analysis, business strategy, technical architecture, and monetization planning. Legal and cost analysis less critical at ideation stage.",
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
    monetization: str
    legal_considerations: str
    tech_stack: str
    strategist_synthesis: str
    critic_review: str
    final_strategy: str


# =============================================================================
# Agent Node Functions
# =============================================================================

# Valid agent names and common typo aliases
ALLOWED_AGENTS = {
    "MARKET_ANALYST", "COST_PREDICTOR", "BUSINESS_STRATEGIST",
    "MONETIZATION_EXPERT", "LEGAL_ADVISOR", "TECH_ARCHITECT"
}

AGENT_ALIASES = {
    # Common typos and variations
    "MARKET_ANALYSIST": "MARKET_ANALYST",
    "MARKET_ANALYSIS": "MARKET_ANALYST",
    "MARKETANALYST": "MARKET_ANALYST",
    "COST_PREDICTION": "COST_PREDICTOR",
    "COSTPREDICTOR": "COST_PREDICTOR",
    "BUSINESS_STRATEGY": "BUSINESS_STRATEGIST",
    "BUSINESSSTRATEGIST": "BUSINESS_STRATEGIST",
    "MONETIZATION": "MONETIZATION_EXPERT",
    "MONETISATION_EXPERT": "MONETIZATION_EXPERT",
    "LEGAL": "LEGAL_ADVISOR",
    "LEGALADVISOR": "LEGAL_ADVISOR",
    "TECH": "TECH_ARCHITECT",
    "TECHARCHITECT": "TECH_ARCHITECT",
    "TECHNOLOGY_ARCHITECT": "TECH_ARCHITECT",
}

# Core agents that should always run
CORE_AGENTS = {"MARKET_ANALYST", "BUSINESS_STRATEGIST"}


def normalize_agent_names(agents: list) -> list:
    """Normalize agent names to fix typos and ensure core agents are included."""
    normalized = set()
    
    for agent in agents:
        name = agent.strip().upper().replace(" ", "_")
        # Apply alias mapping if exists
        if name in AGENT_ALIASES:
            name = AGENT_ALIASES[name]
        # Only include valid agents
        if name in ALLOWED_AGENTS:
            normalized.add(name)
    
    # Always include core agents
    normalized.update(CORE_AGENTS)
    
    return list(normalized)


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
        raw_selected = result.get("selected_agents", ["MARKET_ANALYST", "BUSINESS_STRATEGIST"])
        reasoning = result.get("reasoning", "Default analysis")
        category = result.get("startup_category", "General")
        complexity = result.get("complexity_score", 5)
    except json.JSONDecodeError:
        # Fallback to all agents if parsing fails
        raw_selected = ["MARKET_ANALYST", "COST_PREDICTOR", "BUSINESS_STRATEGIST", 
                       "MONETIZATION_EXPERT", "LEGAL_ADVISOR", "TECH_ARCHITECT"]
        reasoning = "Full analysis (parsing fallback)"
        category = "General"
        complexity = 5
    
    # Normalize agent names to fix typos and ensure core agents
    selected = normalize_agent_names(raw_selected)
    
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
    
    # Query RAG for Indian cost benchmarks with multiple relevant queries
    cost_context = "No additional cost data available."
    try:
        from .rag_system import query_cost_knowledge
        
        startup_idea = state['startup_idea']
        target_market = state.get('target_market', 'India')
        
        # Build comprehensive queries to retrieve relevant cost data
        queries = [
            f"{startup_idea} technology infrastructure cloud hosting SaaS costs",
            f"{startup_idea} team salaries personnel hiring costs India",
            f"{startup_idea} marketing customer acquisition costs India",
            f"startup setup costs legal incorporation office equipment India",
            f"{startup_idea} {target_market} operational overhead monthly expenses"
        ]
        
        # Retrieve from multiple query angles and combine
        all_contexts = []
        for query in queries:
            try:
                result = query_cost_knowledge(query, k=3)
                if result and "No relevant information" not in result and "Error" not in result:
                    all_contexts.append(result)
            except Exception as query_error:
                print(f"⚠️ Query failed for '{query[:50]}...': {query_error}")
                continue
        
        if all_contexts:
            cost_context = "\n\n--- ADDITIONAL COST DATA ---\n\n".join(all_contexts)
            print(f"💵 Retrieved Indian cost benchmarks from {len(all_contexts)} queries")
        else:
            print("⚠️ No cost data retrieved from knowledge base")
            
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


def monetization_node(state: AnalysisState) -> dict:
    """Monetization Expert agent."""
    if "MONETIZATION_EXPERT" not in state.get("selected_agents", []):
        print("⏭️ Skipping Monetization Expert (not selected)")
        return {"monetization": ""}
    
    print("💳 Monetization Expert working...")
    llm = get_llm('monetization')
    context = create_user_context(state)
    response = llm.invoke([
        SystemMessage(content=MONETIZATION_PROMPT),
        HumanMessage(content=context)
    ])
    return {"monetization": response.content}


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


def tech_architect_node(state: AnalysisState) -> dict:
    """Tech Architect agent."""
    if "TECH_ARCHITECT" not in state.get("selected_agents", []):
        print("⏭️ Skipping Tech Architect (not selected)")
        return {"tech_stack": ""}
    
    print("💻 Tech Architect working...")
    llm = get_llm('tech_architect')
    context = create_user_context(state)
    response = llm.invoke([
        SystemMessage(content=TECH_ARCHITECT_PROMPT),
        HumanMessage(content=context)
    ])
    return {"tech_stack": response.content}


def truncate_with_context(text: str, max_chars: int = 2500, preserve_headers: bool = True) -> str:
    """
    Truncate text while preserving structure and key information.
    Keeps headers and first paragraph under each header.
    """
    if not text or len(text) <= max_chars:
        return text
    
    if preserve_headers:
        lines = text.split('\n')
        result = []
        current_length = 0
        
        for line in lines:
            # Always keep headers (lines starting with # or all caps)
            is_header = line.strip().startswith('#') or (line.strip().isupper() and len(line.strip()) > 3)
            
            if current_length + len(line) > max_chars and not is_header:
                break
            
            result.append(line)
            current_length += len(line) + 1
        
        return '\n'.join(result) + "\n[... truncated for brevity ...]"
    
    return text[:max_chars] + "\n[... truncated for brevity ...]"


def strategist_synthesis_node(state: AnalysisState) -> dict:
    """Strategist synthesizes all agent outputs."""
    print("🔮 Strategist synthesizing insights...")
    llm = get_llm('strategist_synthesis')
    
    # Truncate each agent output to reduce token usage
    synthesis_context = f"""
Original Startup Idea: {state['startup_idea']}
{f"Target Market: {state['target_market']}" if state.get('target_market') else ""}

=== MARKET ANALYSIS (Key Points) ===
{truncate_with_context(state.get('market_analysis', ''), 2500)}

=== COST PREDICTION (Key Points) ===
{truncate_with_context(state.get('cost_prediction', ''), 2000)}

=== BUSINESS STRATEGY (Key Points) ===
{truncate_with_context(state.get('business_strategy', ''), 2500)}

=== MONETIZATION MODELS (Key Points) ===
{truncate_with_context(state.get('monetization', ''), 2000)}

=== LEGAL CONSIDERATIONS (Key Points) ===
{truncate_with_context(state.get('legal_considerations', ''), 2000)}

=== TECHNOLOGY STACK (Key Points) ===
{truncate_with_context(state.get('tech_stack', ''), 1500)}
"""
    
    response = llm.invoke([
        SystemMessage(content=STRATEGIST_PROMPT),
        HumanMessage(content=synthesis_context)
    ])
    return {"strategist_synthesis": response.content}


def critic_review_node(state: AnalysisState) -> dict:
    """Critic reviews and challenges the strategist's plan."""
    print("🔍 Critic reviewing the plan...")
    llm = get_llm('critic_review')
    
    critic_context = f"""
Original Startup Idea: {state['startup_idea']}

=== STRATEGIST'S SYNTHESIZED PLAN ===
{truncate_with_context(state.get('strategist_synthesis', ''), 4000)}

=== KEY SUPPORTING DATA ===
Market Highlights: {truncate_with_context(state.get('market_analysis', ''), 1500)}
Cost Overview: {truncate_with_context(state.get('cost_prediction', ''), 1500)}
"""
    
    response = llm.invoke([
        SystemMessage(content=CRITIC_PROMPT),
        HumanMessage(content=critic_context)
    ])
    return {"critic_review": response.content}


def final_refinement_node(state: AnalysisState) -> dict:
    """Strategist refines plan based on critic feedback."""
    print("✨ Generating final refined strategy...")
    llm = get_llm('final_refinement')
    
    refinement_prompt = """You are the Senior Business Strategist again.
Review the Critic's feedback and refine your strategic plan.
Address the valid concerns raised while maintaining the core strategy's strengths.
Create a FINAL, battle-tested strategic plan that is comprehensive and actionable.

Format your response clearly with headers and bullet points. Do not use asterisks for emphasis - use clear section headers instead."""

    refinement_context = f"""
=== YOUR ORIGINAL SYNTHESIZED PLAN ===
{truncate_with_context(state.get('strategist_synthesis', ''), 3500)}

=== CRITIC'S REVIEW ===
{truncate_with_context(state.get('critic_review', ''), 3000)}

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
    """Build the multi-agent analysis graph with orchestrator."""
    
    workflow = StateGraph(AnalysisState)
    
    # Add orchestrator as entry point
    workflow.add_node("orchestrator", orchestrator_node)
    
    # Add all specialist agent nodes
    workflow.add_node("market_analyst", market_analyst_node)
    workflow.add_node("cost_predictor", cost_predictor_node)
    workflow.add_node("business_strategist", business_strategist_node)
    workflow.add_node("monetization", monetization_node)
    workflow.add_node("legal_advisor", legal_advisor_node)
    workflow.add_node("tech_architect", tech_architect_node)
    workflow.add_node("strategist_synthesis", strategist_synthesis_node)
    workflow.add_node("critic_review", critic_review_node)
    workflow.add_node("final_refinement", final_refinement_node)
    
    # Set entry point to orchestrator
    workflow.set_entry_point("orchestrator")
    
    # Orchestrator -> specialist agents (sequential for memory efficiency)
    workflow.add_edge("orchestrator", "market_analyst")
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
        "monetization": "",
        "legal_considerations": "",
        "tech_stack": "",
        "strategist_synthesis": "",
        "critic_review": "",
        "final_strategy": "",
    }
    
    final_state = graph.invoke(initial_state)
    
    return {
        # Orchestrator metadata
        "selected_agents": final_state["selected_agents"],
        "orchestrator_reasoning": final_state["orchestrator_reasoning"],
        "startup_category": final_state["startup_category"],
        "complexity_score": final_state["complexity_score"],
        # Analysis results
        "market_analysis": final_state["market_analysis"],
        "cost_prediction": final_state["cost_prediction"],
        "business_strategy": final_state["business_strategy"],
        "monetization": final_state["monetization"],
        "legal_considerations": final_state["legal_considerations"],
        "tech_stack": final_state["tech_stack"],
        "strategist_critique": final_state["final_strategy"],
    }
