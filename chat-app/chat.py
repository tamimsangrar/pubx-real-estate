from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import os
from dotenv import load_dotenv
from agents.real_estate_agent import RealEstateAgent
from agents.config_manager import AgentConfigManager
from supabase import create_client, Client

load_dotenv()

app = FastAPI(title="Real Estate Chat API")

# CORS configuration
cors_origin = os.getenv("CORS_ORIGIN", "http://localhost:3000")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[cors_origin, "https://pubx-real-estate.netlify.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Supabase client
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
supabase: Client = None

if supabase_url and supabase_key and supabase_url != "https://placeholder.supabase.co":
    supabase = create_client(supabase_url, supabase_key)
else:
    print("Warning: Supabase credentials not configured. Using mock data for leads.")

# Initialize the LangGraph agent
agent = RealEstateAgent()
config_manager = AgentConfigManager()

class ChatMessage(BaseModel):
    message: str
    conversation_history: List[Dict[str, Any]] = []

class ChatResponse(BaseModel):
    response: str
    conversation_history: List[Dict[str, Any]]
    lead_info: Dict[str, Any] = {}
    tools_used: List[str] = []
    current_step: str = ""

class AgentConfig(BaseModel):
    personality: str
    system_prompt: str
    temperature: float
    model: str
    max_tokens: int
    services: List[str]
    tools_enabled: bool

class Lead(BaseModel):
    id: Optional[str] = None
    name: str
    email: str
    phone: str
    source: str
    score: Optional[int] = None
    status: str = "new"
    created_at: Optional[str] = None
    last_contact: Optional[str] = None
    notes: Optional[str] = None

class LeadFilters(BaseModel):
    search: Optional[str] = None
    status: Optional[str] = None
    score_min: Optional[int] = None
    score_max: Optional[int] = None
    limit: int = 50
    offset: int = 0

@app.get("/")
async def root():
    return {"message": "Real Estate Chat API with LangGraph is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "chat-api", "agent": "langgraph"}

@app.post("/api/chat", response_model=ChatResponse)
async def chat(chat_message: ChatMessage):
    """
    Handle chat messages using LangGraph real estate agent
    """
    try:
        # Use the LangGraph agent to process the message
        result = await agent.chat(
            message=chat_message.message,
            conversation_history=chat_message.conversation_history
        )
        
        return ChatResponse(
            response=result["response"],
            conversation_history=result["conversation_history"],
            lead_info=result.get("lead_info", {}),
            tools_used=result.get("tools_used", []),
            current_step=result.get("current_step", "")
        )
        
    except Exception as e:
        print(f"Chat error: {e}")
        # Fallback response
        return ChatResponse(
            response="I'm sorry, I'm having trouble processing your request right now. Please try again.",
            conversation_history=chat_message.conversation_history + [
                {"role": "user", "content": chat_message.message},
                {"role": "assistant", "content": "I'm sorry, I'm having trouble processing your request right now. Please try again."}
            ]
        )

# Agent Configuration Endpoints
@app.get("/api/config")
async def get_agent_config():
    """Get current agent configuration for admin panel"""
    try:
        config = await config_manager.get_agent_config()
        return config
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/config")
async def update_agent_config(config_update: AgentConfig):
    """Update agent configuration from admin panel"""
    try:
        updates = config_update.dict()
        updated_config = await config_manager.update_agent_config(updates)
        return {"message": "Configuration updated successfully", "config": updated_config}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/agent/config")
async def get_agent_config_legacy():
    """Legacy endpoint - redirects to /api/config"""
    return await get_agent_config()

@app.post("/api/agent/config")
async def update_agent_config_legacy(config_update: Dict[str, Any]):
    """Legacy endpoint - redirects to /api/config"""
    try:
        updated_config = await config_manager.update_agent_config(config_update)
        return {"message": "Configuration updated successfully", "config": updated_config}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/agent/presets")
async def get_personality_presets():
    """Get available personality presets"""
    try:
        presets = await config_manager.get_personality_presets()
        return {"presets": presets}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/agent/preset/{preset_name}")
async def apply_personality_preset(preset_name: str):
    """Apply a personality preset"""
    try:
        updated_config = await config_manager.apply_personality_preset(preset_name)
        return {"message": f"Applied {preset_name} preset", "config": updated_config}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Leads Management Endpoints
@app.get("/api/leads/stats")
async def get_lead_stats():
    """Get lead statistics for dashboard"""
    from datetime import datetime, timedelta
    try:
        if not supabase:
            print("Supabase not configured, returning mock data")
            return {
                "total_leads": 156,
                "high_score_leads": 23,
                "this_week_leads": 12,
                "qualified_leads": 8
            }
        
        print("Fetching total leads...")
        # Get total leads
        total_response = supabase.table('leads').select('id').execute()
        print(f"Total leads response: {total_response}")
        total_leads = len(total_response.data) if total_response.data else 0
        print(f"Total leads count: {total_leads}")

        print("Fetching this week leads...")
        # Get leads created this week
        week_ago = (datetime.now() - timedelta(days=7)).isoformat()
        this_week_response = supabase.table('leads').select('id').gte('created_at', week_ago).execute()
        print(f"This week response: {this_week_response}")
        this_week_leads = len(this_week_response.data) if this_week_response.data else 0
        print(f"This week count: {this_week_leads}")

        print("Fetching lead scores...")
        # Get latest score per lead
        scores_response = supabase.table('lead_scores').select('lead_id,score,created_at').order('created_at', desc=True).execute()
        print(f"Scores response: {scores_response}")
        
        latest_scores = {}
        if scores_response.data:
            for row in scores_response.data:
                lead_id = row['lead_id']
                if lead_id not in latest_scores:
                    latest_scores[lead_id] = row['score']
        
        print(f"Latest scores: {latest_scores}")
        
        # Compute high score and qualified counts
        high_score_leads = sum(1 for score in latest_scores.values() if score >= 80)
        qualified_leads = sum(1 for score in latest_scores.values() if score >= 70)
        
        print(f"High score leads: {high_score_leads}, Qualified leads: {qualified_leads}")

        result = {
            "total_leads": total_leads,
            "high_score_leads": high_score_leads,
            "this_week_leads": this_week_leads,
            "qualified_leads": qualified_leads
        }
        print(f"Final result: {result}")
        return result
        
    except Exception as e:
        print(f"Error fetching lead stats: {e}")
        import traceback
        traceback.print_exc()
        # Return mock data on error
        return {
            "total_leads": 156,
            "high_score_leads": 23,
            "this_week_leads": 12,
            "qualified_leads": 8
        }

@app.get("/api/leads")
async def get_leads(
    search: Optional[str] = None,
    status: Optional[str] = None,
    score_min: Optional[int] = None,
    score_max: Optional[int] = None,
    limit: int = 50,
    offset: int = 0
):
    """Get leads with filtering and pagination"""
    try:
        if not supabase:
            # Return mock data when Supabase is not configured
            mock_leads = [
                {
                    "id": "1",
                    "name": "John Doe",
                    "email": "john@example.com",
                    "phone": "+1-555-0123",
                    "source": "Website Chat",
                    "score": 85,
                    "status": "qualified",
                    "created_at": "2024-01-15T10:30:00Z",
                    "last_contact": "2024-01-16T14:20:00Z",
                    "notes": "Interested in 3BR properties downtown. Budget $500k-750k."
                },
                {
                    "id": "2",
                    "name": "Jane Smith",
                    "email": "jane.smith@gmail.com",
                    "phone": "+1-555-0456",
                    "source": "Phone Call",
                    "score": 92,
                    "status": "contacted",
                    "created_at": "2024-01-14T09:15:00Z",
                    "last_contact": "2024-01-15T16:45:00Z",
                    "notes": "Looking for investment properties. Has experience in real estate."
                },
                {
                    "id": "3",
                    "name": "Mike Johnson",
                    "email": "mike@temp-mail.org",
                    "phone": "+1-555-0789",
                    "source": "Website Chat",
                    "score": 45,
                    "status": "new",
                    "created_at": "2024-01-16T11:20:00Z",
                    "last_contact": "2024-01-16T11:20:00Z",
                    "notes": "General inquiry about market conditions."
                },
                {
                    "id": "4",
                    "name": "Sarah Wilson",
                    "email": "sarah.wilson@outlook.com",
                    "phone": "+1-555-0321",
                    "source": "Website Chat",
                    "score": 78,
                    "status": "contacted",
                    "created_at": "2024-01-13T15:45:00Z",
                    "last_contact": "2024-01-14T10:30:00Z",
                    "notes": "First-time buyer. Looking for 2BR condo under $400k."
                },
                {
                    "id": "5",
                    "name": "David Brown",
                    "email": "david.brown@yahoo.com",
                    "phone": "+1-555-0654",
                    "source": "Phone Call",
                    "score": 95,
                    "status": "qualified",
                    "created_at": "2024-01-12T08:20:00Z",
                    "last_contact": "2024-01-13T14:15:00Z",
                    "notes": "Experienced investor. Looking for multi-family properties."
                }
            ]
            
            # Apply filters to mock data
            filtered_leads = mock_leads
            
            if search:
                filtered_leads = [lead for lead in filtered_leads if 
                    search.lower() in lead["name"].lower() or 
                    search.lower() in lead["email"].lower() or 
                    search in lead["phone"]
                ]
            
            if status and status != 'all':
                filtered_leads = [lead for lead in filtered_leads if lead["status"] == status]
            
            if score_min is not None:
                filtered_leads = [lead for lead in filtered_leads if lead["score"] >= score_min]
            
            if score_max is not None:
                filtered_leads = [lead for lead in filtered_leads if lead["score"] <= score_max]
            
            # Apply pagination
            total_count = len(filtered_leads)
            paginated_leads = filtered_leads[offset:offset + limit]
            
            return {
                "leads": paginated_leads,
                "total": total_count,
                "limit": limit,
                "offset": offset
            }
        
        # Build query
        query = supabase.table('leads').select('*')
        
        # Apply filters
        if search:
            query = query.or_(f"name.ilike.%{search}%,email.ilike.%{search}%,phone.ilike.%{search}%")
        
        if status and status != 'all':
            query = query.eq('status', status)
        
        if score_min is not None:
            query = query.gte('score', score_min)
        
        if score_max is not None:
            query = query.lte('score', score_max)
        
        # Apply pagination
        query = query.range(offset, offset + limit - 1)
        
        # Execute query
        response = query.execute()
        leads = response.data
        
        # Get total count for pagination
        count_query = supabase.table('leads').select('id', count='exact')
        if search:
            count_query = count_query.or_(f"name.ilike.%{search}%,email.ilike.%{search}%,phone.ilike.%{search}%")
        if status and status != 'all':
            count_query = count_query.eq('status', status)
        if score_min is not None:
            count_query = count_query.gte('score', score_min)
        if score_max is not None:
            count_query = count_query.lte('score', score_max)
        
        count_response = count_query.execute()
        total_count = count_response.count or 0
        
        return {
            "leads": leads,
            "total": total_count,
            "limit": limit,
            "offset": offset
        }
        
    except Exception as e:
        print(f"Error fetching leads: {e}")
        # Return mock data on error
        mock_leads = [
            {
                "id": "1",
                "name": "John Doe",
                "email": "john@example.com",
                "phone": "+1-555-0123",
                "source": "Website Chat",
                "score": 85,
                "status": "qualified",
                "created_at": "2024-01-15T10:30:00Z",
                "last_contact": "2024-01-16T14:20:00Z",
                "notes": "Interested in 3BR properties downtown. Budget $500k-750k."
            }
        ]
        return {
            "leads": mock_leads,
            "total": 1,
            "limit": limit,
            "offset": offset
        }

@app.get("/api/leads/{lead_id}")
async def get_lead(lead_id: str):
    """Get a specific lead by ID"""
    try:
        response = supabase.table('leads').select('*').eq('id', lead_id).execute()
        
        if not response.data:
            raise HTTPException(status_code=404, detail="Lead not found")
        
        return response.data[0]
        
    except Exception as e:
        print(f"Error fetching lead: {e}")
        raise HTTPException(status_code=500, detail="Error fetching lead")

@app.post("/api/leads")
async def create_lead(lead: Lead):
    """Create a new lead"""
    try:
        lead_data = lead.dict(exclude={'id', 'created_at'})
        response = supabase.table('leads').insert(lead_data).execute()
        
        if response.data:
            return {"message": "Lead created successfully", "lead": response.data[0]}
        else:
            raise HTTPException(status_code=400, detail="Failed to create lead")
            
    except Exception as e:
        print(f"Error creating lead: {e}")
        raise HTTPException(status_code=500, detail="Error creating lead")

@app.put("/api/leads/{lead_id}")
async def update_lead(lead_id: str, lead_update: Dict[str, Any]):
    """Update a lead"""
    try:
        response = supabase.table('leads').update(lead_update).eq('id', lead_id).execute()
        
        if response.data:
            return {"message": "Lead updated successfully", "lead": response.data[0]}
        else:
            raise HTTPException(status_code=404, detail="Lead not found")
            
    except Exception as e:
        print(f"Error updating lead: {e}")
        raise HTTPException(status_code=500, detail="Error updating lead")

@app.delete("/api/leads/{lead_id}")
async def delete_lead(lead_id: str):
    """Delete a lead"""
    try:
        response = supabase.table('leads').delete().eq('id', lead_id).execute()
        
        if response.data:
            return {"message": "Lead deleted successfully"}
        else:
            raise HTTPException(status_code=404, detail="Lead not found")
            
    except Exception as e:
        print(f"Error deleting lead: {e}")
        raise HTTPException(status_code=500, detail="Error deleting lead")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 