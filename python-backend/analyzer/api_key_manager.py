"""
API Key Manager for Groq Multi-Key Support.

Distributes API requests across multiple Groq API keys to avoid rate limits.
"""

import os
from typing import Optional, List, Dict
from django.conf import settings


# Agent to API Key mapping for load distribution
# Group 1 - Key 1: Initial analysis agents
# Group 2 - Key 2: Strategy & planning agents
# Group 3 - Key 3: Architecture & synthesis agents
AGENT_KEY_MAPPING = {
    # Group 1 - Key 1 (Initial Analysis)
    'orchestrator': 'key_1',
    'market_analyst': 'key_1',
    'cost_predictor': 'key_1',
    
    # Group 2 - Key 2 (Strategy & Planning)
    'business_strategist': 'key_2',
    'monetization': 'key_2',
    'legal_advisor': 'key_2',
    
    # Group 3 - Key 3 (Architecture & Synthesis)
    'tech_architect': 'key_3',
    'strategist_synthesis': 'key_3',
    'critic_review': 'key_3',
    'final_refinement': 'key_3',
}


def get_configured_keys() -> Dict[str, Optional[str]]:
    """Get all configured API keys from settings/environment."""
    return {
        'key_1': getattr(settings, 'GROQ_API_KEY_1', None) or os.getenv('GROQ_API_KEY_1') or getattr(settings, 'GROQ_API_KEY', None) or os.getenv('GROQ_API_KEY'),
        'key_2': getattr(settings, 'GROQ_API_KEY_2', None) or os.getenv('GROQ_API_KEY_2'),
        'key_3': getattr(settings, 'GROQ_API_KEY_3', None) or os.getenv('GROQ_API_KEY_3'),
    }


def get_available_keys() -> List[str]:
    """Get list of all valid (non-None) API keys."""
    keys = get_configured_keys()
    return [key for key_id, key in keys.items() if key]


def get_key_for_agent(agent_name: str) -> str:
    """
    Get the appropriate API key for a specific agent.
    
    Falls back to available keys if the designated key isn't configured.
    
    Args:
        agent_name: Name of the agent (e.g., 'market_analyst', 'legal_advisor')
        
    Returns:
        API key string
        
    Raises:
        ValueError: If no API keys are configured
    """
    keys = get_configured_keys()
    
    # Get the designated key for this agent
    designated_key_id = AGENT_KEY_MAPPING.get(agent_name, 'key_1')
    designated_key = keys.get(designated_key_id)
    
    # If designated key is available, use it
    if designated_key:
        print(f"🔑 Agent '{agent_name}' using {designated_key_id}")
        return designated_key
    
    # Fallback: find any available key
    for key_id, key in keys.items():
        if key:
            print(f"🔑 Agent '{agent_name}' falling back to {key_id}")
            return key
    
    raise ValueError(
        "No Groq API keys configured. Please set GROQ_API_KEY_1 (or GROQ_API_KEY), "
        "GROQ_API_KEY_2, and/or GROQ_API_KEY_3 in your environment."
    )


def get_key_status() -> Dict[str, Dict]:
    """
    Get the configuration status of all API keys.
    
    Returns:
        Dictionary with key status information
    """
    keys = get_configured_keys()
    
    status = {}
    for key_id, key in keys.items():
        # Get agents assigned to this key
        assigned_agents = [
            agent for agent, assigned_key in AGENT_KEY_MAPPING.items() 
            if assigned_key == key_id
        ]
        
        status[key_id] = {
            'configured': bool(key),
            'masked_key': f"{key[:8]}...{key[-4:]}" if key else None,
            'assigned_agents': assigned_agents,
        }
    
    # Add summary
    configured_count = sum(1 for k in keys.values() if k)
    
    return {
        'keys': status,
        'summary': {
            'total_keys': 3,
            'configured_keys': configured_count,
            'fallback_active': configured_count < 3,
        }
    }


def get_fallback_key(exclude_key_id: str = None) -> Optional[str]:
    """
    Get a fallback key when the primary key is rate limited.
    
    Args:
        exclude_key_id: Key ID to exclude (the one that's rate limited)
        
    Returns:
        Alternative API key or None if no alternatives available
    """
    keys = get_configured_keys()
    
    for key_id, key in keys.items():
        if key and key_id != exclude_key_id:
            return key
    
    return None
