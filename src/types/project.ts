export interface Project {
  id: string;
  startup_idea: string;
  target_market: string | null;
  market_analysis: string | null;
  cost_prediction: string | null;
  business_strategy: string | null;
  legal_considerations: string | null;
  status: 'pending' | 'analyzing' | 'completed' | 'failed';
  created_at: string;
  updated_at: string;
}

export interface AnalysisResult {
  marketAnalysis: string;
  costPrediction: string;
  businessStrategy: string;
  legalConsiderations: string;
}

export interface AgentCard {
  id: keyof AnalysisResult;
  title: string;
  icon: string;
  description: string;
  color: string;
}

export const AGENT_CARDS: AgentCard[] = [
  {
    id: 'marketAnalysis',
    title: 'Market Analysis',
    icon: '📈',
    description: 'Market size, competition, and opportunity assessment',
    color: 'from-teal-500/20 to-teal-600/10',
  },
  {
    id: 'costPrediction',
    title: 'Cost Prediction',
    icon: '💰',
    description: 'Startup costs, burn rate, and financial planning',
    color: 'from-amber-500/20 to-amber-600/10',
  },
  {
    id: 'businessStrategy',
    title: 'Business Strategy',
    icon: '🎯',
    description: 'Go-to-market strategy and competitive positioning',
    color: 'from-blue-500/20 to-blue-600/10',
  },
  {
    id: 'legalConsiderations',
    title: 'Legal Considerations',
    icon: '⚖️',
    description: 'Compliance, IP protection, and legal structure',
    color: 'from-rose-500/20 to-rose-600/10',
  },
];
