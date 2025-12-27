-- Create projects table for storing startup analysis history
CREATE TABLE public.projects (
  id UUID NOT NULL DEFAULT gen_random_uuid() PRIMARY KEY,
  startup_idea TEXT NOT NULL,
  target_market TEXT,
  market_analysis TEXT,
  cost_prediction TEXT,
  business_strategy TEXT,
  monetization TEXT,
  legal_considerations TEXT,
  tech_stack TEXT,
  strategist_critique TEXT,
  status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'analyzing', 'completed', 'failed')),
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
  updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
);

-- Enable Row Level Security
ALTER TABLE public.projects ENABLE ROW LEVEL SECURITY;

-- Create policy for public read/write access (no auth required for MVP)
CREATE POLICY "Allow public read access" 
ON public.projects 
FOR SELECT 
USING (true);

CREATE POLICY "Allow public insert access" 
ON public.projects 
FOR INSERT 
WITH CHECK (true);

CREATE POLICY "Allow public update access" 
ON public.projects 
FOR UPDATE 
USING (true);

CREATE POLICY "Allow public delete access" 
ON public.projects 
FOR DELETE 
USING (true);

-- Create function to update timestamps
CREATE OR REPLACE FUNCTION public.update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = now();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql SET search_path = public;

-- Create trigger for automatic timestamp updates
CREATE TRIGGER update_projects_updated_at
BEFORE UPDATE ON public.projects
FOR EACH ROW
EXECUTE FUNCTION public.update_updated_at_column();