from typing import Dict, Any, Optional
from supabase import create_client, Client
import os
import json
from datetime import datetime

class AgentConfigManager:
    def __init__(self):
        self.supabase: Client = create_client(
            os.getenv("SUPABASE_URL"),
            os.getenv("SUPABASE_ANON_KEY")
        )
        self._cache = {}
        self._cache_timestamp = None
        self._cache_ttl = 300  # 5 minutes
    
    async def get_agent_config(self) -> Dict[str, Any]:
        """Get agent configuration from Supabase with caching"""
        now = datetime.now()
        
        # Check cache first
        if (self._cache_timestamp and 
            (now - self._cache_timestamp).seconds < self._cache_ttl and 
            self._cache):
            return self._cache
        
        try:
            # Fetch from Supabase settings table
            response = self.supabase.table('settings').select('*').eq('key', 'agent_config').execute()
            
            if response.data:
                config = json.loads(response.data[0]['value'])
            else:
                # Default configuration if none exists
                config = self._get_default_config()
                await self._save_default_config(config)
            
            # Update cache
            self._cache = config
            self._cache_timestamp = now
            
            return config
            
        except Exception as e:
            print(f"Error fetching agent config: {e}")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Default agent configuration"""
        return {
            "personality": "Professional, friendly, and knowledgeable real estate assistant who helps clients find their perfect home",
            "system_prompt": """You are a helpful real estate assistant. Your role is to:
1. Help users find properties that match their needs
2. Qualify leads by understanding their budget, timeline, and preferences  
3. Schedule property viewings and appointments
4. Provide market information and neighborhood insights
5. Guide users through the home buying/selling process
6. Escalate complex issues to human agents when needed

Always be professional, empathetic, and solution-focused.""",
            "response_style": "conversational",
            "max_response_length": 250,
            "tools_enabled": [
                "property_search",
                "lead_qualification", 
                "schedule_viewing",
                "market_info",
                "escalate_human"
            ],
            "services": [
                "Property Search",
                "Market Analysis", 
                "Viewing Appointments",
                "Buyer/Seller Guidance",
                "Neighborhood Information"
            ],
            "greeting_message": "Hi! I'm your AI real estate assistant. I'm here to help you find your perfect home or answer any real estate questions you might have. How can I assist you today?",
            "escalation_triggers": [
                "complaint",
                "legal_question",
                "complex_negotiation",
                "technical_issue"
            ],
            "lead_qualification_fields": [
                "budget_range",
                "preferred_location",
                "property_type",
                "timeline",
                "contact_info"
            ]
        }
    
    async def _save_default_config(self, config: Dict[str, Any]) -> None:
        """Save default configuration to Supabase"""
        try:
            self.supabase.table('settings').upsert({
                'key': 'agent_config',
                'value': json.dumps(config),
                'updated_at': datetime.now().isoformat()
            }).execute()
        except Exception as e:
            print(f"Error saving default config: {e}")
    
    async def update_agent_config(self, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update agent configuration (called from admin panel)"""
        try:
            # Get current config
            current_config = await self.get_agent_config()
            
            # Merge updates
            updated_config = {**current_config, **updates}
            
            # Save to Supabase
            self.supabase.table('settings').upsert({
                'key': 'agent_config',
                'value': json.dumps(updated_config),
                'updated_at': datetime.now().isoformat()
            }).execute()
            
            # Clear cache
            self._cache = {}
            self._cache_timestamp = None
            
            return updated_config
            
        except Exception as e:
            print(f"Error updating agent config: {e}")
            raise
    
    async def get_personality_presets(self) -> Dict[str, Dict[str, Any]]:
        """Get predefined personality presets for admin panel"""
        return {
            "professional": {
                "personality": "Professional, formal, and detail-oriented real estate expert",
                "response_style": "formal",
                "greeting_message": "Good day! I am your professional real estate consultant. How may I assist you with your property needs today?"
            },
            "friendly": {
                "personality": "Warm, friendly, and approachable real estate helper who makes home buying fun",
                "response_style": "conversational", 
                "greeting_message": "Hey there! I'm excited to help you find your dream home! What kind of place are you looking for?"
            },
            "expert": {
                "personality": "Highly knowledgeable real estate expert with deep market insights and analytical approach",
                "response_style": "informative",
                "greeting_message": "Hello! I'm your real estate market expert. I can provide detailed analysis and insights to help you make informed decisions. What would you like to know?"
            },
            "luxury": {
                "personality": "Sophisticated luxury real estate specialist focused on high-end properties and white-glove service",
                "response_style": "elegant",
                "greeting_message": "Welcome! I specialize in luxury real estate and premium properties. I'm here to provide you with exceptional service. How may I assist you today?"
            }
        }
    
    async def apply_personality_preset(self, preset_name: str) -> Dict[str, Any]:
        """Apply a personality preset"""
        presets = await self.get_personality_presets()
        
        if preset_name not in presets:
            raise ValueError(f"Unknown personality preset: {preset_name}")
        
        preset_config = presets[preset_name]
        return await self.update_agent_config(preset_config)
    
    async def get_analytics_config(self) -> Dict[str, Any]:
        """Get configuration for conversation analytics"""
        try:
            response = self.supabase.table('settings').select('*').eq('key', 'analytics_config').execute()
            
            if response.data:
                return json.loads(response.data[0]['value'])
            else:
                return {
                    "track_conversations": True,
                    "track_lead_conversion": True,
                    "track_tool_usage": True,
                    "track_escalations": True,
                    "anonymize_data": False
                }
        except Exception as e:
            print(f"Error fetching analytics config: {e}")
            return {}
    
    def invalidate_cache(self):
        """Manually invalidate configuration cache"""
        self._cache = {}
        self._cache_timestamp = None 