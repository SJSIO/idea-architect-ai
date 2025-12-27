import { serve } from "https://deno.land/std@0.168.0/http/server.ts";

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
};

const LOVABLE_API_KEY = Deno.env.get('LOVABLE_API_KEY');
const AI_GATEWAY_URL = 'https://ai.gateway.lovable.dev/v1/chat/completions';

interface AgentResult {
  agent: string;
  content: string;
}

async function callAgent(systemPrompt: string, userMessage: string, model = 'google/gemini-2.5-flash'): Promise<string> {
  console.log(`Calling agent with model: ${model}`);
  
  const response = await fetch(AI_GATEWAY_URL, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${LOVABLE_API_KEY}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      model,
      messages: [
        { role: 'system', content: systemPrompt },
        { role: 'user', content: userMessage },
      ],
    }),
  });

  if (!response.ok) {
    const errorText = await response.text();
    console.error(`AI Gateway error: ${response.status} - ${errorText}`);
    throw new Error(`AI Gateway error: ${response.status}`);
  }

  const data = await response.json();
  return data.choices?.[0]?.message?.content || 'No response generated';
}

// Agent System Prompts
const MARKET_ANALYST_PROMPT = `You are a world-class Market Analyst with expertise in global markets.
Your task is to analyze the provided startup idea.
Focus on:
- Target audience demographics and psychographics
- Total Addressable Market (TAM), Serviceable Addressable Market (SAM), and Serviceable Obtainable Market (SOM)
- Key competitors and their market positioning
- Market trends and growth projections
- Potential market gaps and opportunities

Provide specific data points, percentages, and market size estimates where possible.
Format your response with clear headers and bullet points for easy reading.`;

const COST_PREDICTOR_PROMPT = `You are an expert Cost Prediction Specialist for startups.
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

Provide all estimates in USD with ranges (low/medium/high scenarios).`;

const BUSINESS_STRATEGIST_PROMPT = `You are a seasoned Business Strategist who has launched multiple successful companies.
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

Be specific and actionable in your recommendations.`;

const MONETIZATION_PROMPT = `You are a Monetization Strategy expert with experience in various business models.
Propose three distinct monetization models for this startup idea.

For each model, provide:
1. **Model Name & Description**
2. **Pricing Strategy** - Specific price points and tiers
3. **Revenue Projections** - Year 1, Year 2, Year 3 estimates
4. **Pros & Cons** - Benefits and challenges
5. **Implementation Complexity** - Easy, Medium, Hard
6. **Best Suited For** - Which customer segments

Consider: subscriptions, freemium, marketplace fees, licensing, advertising, and hybrid models.`;

const LEGAL_ADVISOR_PROMPT = `You are an expert Legal Counsel specializing in startup law and compliance.
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

Provide actionable steps for legal compliance.`;

const TECH_ARCHITECT_PROMPT = `You are a senior Technology Architect specializing in building scalable MVPs.
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

Justify each choice based on scalability, cost, and speed of development.`;

const STRATEGIST_PROMPT = `You are a Senior Business Strategist synthesizing insights from multiple expert analyses.
Based on all the analyses provided, create a refined and actionable strategic plan.

Your synthesis should:
1. Identify the most critical insights from each analysis
2. Find synergies and connections between different recommendations
3. Prioritize actions based on impact and feasibility
4. Create a phased implementation roadmap
5. Highlight key risks and mitigation strategies
6. Provide specific, measurable goals for the first 90 days

Be bold but practical in your recommendations.`;

const CRITIC_PROMPT = `You are a Devil's Advocate and Critical Analyst.
Your role is to stress-test the strategic plan and identify weaknesses.

Critically analyze:
1. **Assumptions** - What unverified assumptions is this plan based on?
2. **Risks** - What could go wrong? What are the biggest threats?
3. **Gaps** - What's missing from the analysis?
4. **Market Reality Check** - Is this truly viable in the current market?
5. **Execution Challenges** - What will be hardest to actually do?
6. **Alternative Perspectives** - What other approaches might work better?

Be constructively critical - identify problems AND suggest solutions.
Your goal is to make the final plan stronger by exposing weaknesses now.`;

serve(async (req) => {
  if (req.method === 'OPTIONS') {
    return new Response(null, { headers: corsHeaders });
  }

  try {
    const { startupIdea, targetMarket, projectId } = await req.json();

    if (!startupIdea) {
      return new Response(
        JSON.stringify({ error: 'Startup idea is required' }),
        { status: 400, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
      );
    }

    if (!LOVABLE_API_KEY) {
      console.error('LOVABLE_API_KEY not configured');
      return new Response(
        JSON.stringify({ error: 'AI service not configured' }),
        { status: 500, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
      );
    }

    const userContext = `
Startup Idea: ${startupIdea}
${targetMarket ? `Target Market: ${targetMarket}` : ''}
    `.trim();

    console.log('Starting multi-agent analysis for:', startupIdea.substring(0, 100));

    // Phase 1: Run all 6 agents in parallel
    console.log('Phase 1: Running 6 specialized agents in parallel...');
    
    const [
      marketAnalysis,
      costPrediction,
      businessStrategy,
      monetization,
      legalConsiderations,
      techStack
    ] = await Promise.all([
      callAgent(MARKET_ANALYST_PROMPT, userContext),
      callAgent(COST_PREDICTOR_PROMPT, userContext),
      callAgent(BUSINESS_STRATEGIST_PROMPT, userContext),
      callAgent(MONETIZATION_PROMPT, userContext),
      callAgent(LEGAL_ADVISOR_PROMPT, userContext),
      callAgent(TECH_ARCHITECT_PROMPT, userContext),
    ]);

    console.log('Phase 1 complete. All 6 agents have responded.');

    // Phase 2: Strategist synthesizes all insights
    console.log('Phase 2: Strategist synthesizing insights...');
    
    const strategistContext = `
Original Startup Idea: ${startupIdea}
${targetMarket ? `Target Market: ${targetMarket}` : ''}

=== MARKET ANALYSIS ===
${marketAnalysis}

=== COST PREDICTION ===
${costPrediction}

=== BUSINESS STRATEGY ===
${businessStrategy}

=== MONETIZATION MODELS ===
${monetization}

=== LEGAL CONSIDERATIONS ===
${legalConsiderations}

=== TECHNOLOGY STACK ===
${techStack}
    `.trim();

    const strategistPlan = await callAgent(STRATEGIST_PROMPT, strategistContext);
    console.log('Strategist synthesis complete.');

    // Phase 3: Critic reviews and challenges
    console.log('Phase 3: Critic reviewing the plan...');
    
    const criticContext = `
Original Startup Idea: ${startupIdea}

=== STRATEGIST'S SYNTHESIZED PLAN ===
${strategistPlan}

=== KEY DATA FROM ANALYSES ===
Market Analysis Summary: ${marketAnalysis.substring(0, 500)}...
Cost Estimates: ${costPrediction.substring(0, 500)}...
    `.trim();

    const criticReview = await callAgent(CRITIC_PROMPT, criticContext);
    console.log('Critic review complete.');

    // Phase 4: Final refined strategy incorporating criticism
    console.log('Phase 4: Generating final refined strategy...');
    
    const finalRefinementPrompt = `You are the Senior Business Strategist again.
Review the Critic's feedback and refine your strategic plan.
Address the valid concerns raised while maintaining the core strategy's strengths.
Create a FINAL, battle-tested strategic plan.`;

    const finalStrategyContext = `
=== YOUR ORIGINAL SYNTHESIZED PLAN ===
${strategistPlan}

=== CRITIC'S REVIEW ===
${criticReview}

Based on this feedback, provide a refined final strategy that addresses the valid concerns while maintaining strategic coherence.
    `.trim();

    const strategistCritique = await callAgent(finalRefinementPrompt, finalStrategyContext);
    console.log('Final strategy generation complete.');

    const result = {
      success: true,
      projectId,
      analysis: {
        marketAnalysis,
        costPrediction,
        businessStrategy,
        monetization,
        legalConsiderations,
        techStack,
        strategistCritique,
      },
    };

    console.log('Analysis complete. Returning results.');

    return new Response(
      JSON.stringify(result),
      { headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
    );

  } catch (error) {
    console.error('Error in analyze-startup function:', error);
    
    if (error instanceof Error && error.message.includes('429')) {
      return new Response(
        JSON.stringify({ error: 'Rate limit exceeded. Please try again in a moment.' }),
        { status: 429, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
      );
    }
    
    if (error instanceof Error && error.message.includes('402')) {
      return new Response(
        JSON.stringify({ error: 'AI credits exhausted. Please add credits to continue.' }),
        { status: 402, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
      );
    }

    return new Response(
      JSON.stringify({ error: error instanceof Error ? error.message : 'Analysis failed' }),
      { status: 500, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
    );
  }
});
