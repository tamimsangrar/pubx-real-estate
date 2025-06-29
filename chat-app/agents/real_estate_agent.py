from typing import Dict, List, Any, Optional
from langgraph.graph import StateGraph, END
from pydantic import BaseModel
import json
import os
from .config_manager import AgentConfigManager
from .tools import RealEstateTools
from .my_openai import MyOpenAI

class ConversationState(BaseModel):
    messages: List[Dict[str, Any]] = []
    user_input: str = ""
    agent_response: str = ""
    current_step: str = "greeting"
    user_context: Dict[str, Any] = {}
    lead_info: Dict[str, Any] = {}
    tools_used: List[str] = []

class RealEstateAgent:
    def __init__(self):
        self.config_manager = AgentConfigManager()
        self.tools = RealEstateTools()
        self.llm = MyOpenAI()
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow for real estate conversations"""
        workflow = StateGraph(ConversationState)
        
        # Add nodes
        workflow.add_node("analyze_intent", self._analyze_intent)
        workflow.add_node("greeting", self._handle_greeting)
        workflow.add_node("property_search", self._handle_property_search)
        workflow.add_node("lead_qualification", self._handle_lead_qualification)
        workflow.add_node("schedule_viewing", self._handle_schedule_viewing)
        workflow.add_node("provide_info", self._provide_general_info)
        workflow.add_node("escalate_human", self._escalate_to_human)
        workflow.add_node("generate_response", self._generate_response)
        
        # Set entry point
        workflow.set_entry_point("analyze_intent")
        
        # Add conditional edges based on intent analysis
        workflow.add_conditional_edges(
            "analyze_intent",
            self._route_conversation,
            {
                "greeting": "greeting",
                "property_search": "property_search", 
                "lead_qualification": "lead_qualification",
                "schedule_viewing": "schedule_viewing",
                "general_info": "provide_info",
                "escalate": "escalate_human"
            }
        )
        
        # All nodes flow to response generation
        for node in ["greeting", "property_search", "lead_qualification", 
                    "schedule_viewing", "provide_info", "escalate_human"]:
            workflow.add_edge(node, "generate_response")
        
        workflow.add_edge("generate_response", END)
        
        return workflow.compile()
    
    async def _analyze_intent(self, state: ConversationState) -> ConversationState:
        """Analyze user intent to route conversation"""
        config = await self.config_manager.get_agent_config()
        
        intent_prompt = f"""
        Analyze the user's message and determine their intent. 
        Agent personality: {config.get('personality', 'Professional real estate assistant')}
        
        User message: {state.user_input}
        Conversation history: {state.messages[-3:] if state.messages else []}
        
        Classify intent as one of:
        - greeting: First contact, hello, introduction
        - property_search: Looking for properties, homes, apartments
        - lead_qualification: Budget, timeline, preferences questions
        - schedule_viewing: Want to see properties, book appointments
        - general_info: Market info, neighborhood questions, process questions
        - escalate: Complex issues, complaints, need human agent
        
        Respond with just the intent classification.
        """
        
        # OpenAI expects messages as list of dicts with 'role' and 'content'
        messages = [
            {"role": "system", "content": intent_prompt}
        ]
        response = await self.llm.ainvoke(messages)
        intent = response.content.strip().lower()
        
        # Default to general_info if intent unclear
        if intent not in ["greeting", "property_search", "lead_qualification", 
                         "schedule_viewing", "general_info", "escalate"]:
            intent = "general_info"
            
        state.current_step = intent
        return state
    
    def _route_conversation(self, state: ConversationState) -> str:
        """Route conversation based on analyzed intent"""
        return state.current_step
    
    async def _handle_greeting(self, state: ConversationState) -> ConversationState:
        """Handle greeting and introduction"""
        config = await self.config_manager.get_agent_config()
        
        greeting_context = {
            "is_first_interaction": len(state.messages) == 0,
            "personality": config.get('personality', ''),
            "available_services": config.get('services', [])
        }
        
        state.user_context.update(greeting_context)
        return state
    
    async def _handle_property_search(self, state: ConversationState) -> ConversationState:
        """Handle property search requests"""
        # Extract search criteria from user input
        search_criteria = await self.tools.extract_search_criteria(state.user_input)
        
        # Perform property search (mock for now)
        properties = await self.tools.search_properties(search_criteria)
        
        state.user_context.update({
            "search_criteria": search_criteria,
            "found_properties": properties,
            "needs_more_criteria": len(search_criteria) < 3
        })
        
        state.tools_used.append("property_search")
        return state
    
    async def _handle_lead_qualification(self, state: ConversationState) -> ConversationState:
        """Handle lead qualification questions"""
        qualification_data = await self.tools.extract_qualification_info(state.user_input)
        
        state.lead_info.update(qualification_data)
        state.user_context.update({
            "qualification_complete": len(state.lead_info) >= 4,
            "missing_info": await self.tools.get_missing_qualification_fields(state.lead_info)
        })
        
        state.tools_used.append("lead_qualification")
        return state
    
    async def _handle_schedule_viewing(self, state: ConversationState) -> ConversationState:
        """Handle viewing appointment scheduling"""
        scheduling_info = await self.tools.extract_scheduling_info(state.user_input)
        
        state.user_context.update({
            "scheduling_request": scheduling_info,
            "available_slots": await self.tools.get_available_slots(),
            "needs_contact_info": not state.lead_info.get('phone') or not state.lead_info.get('email')
        })
        
        state.tools_used.append("schedule_viewing")
        return state
    
    async def _provide_general_info(self, state: ConversationState) -> ConversationState:
        """Provide general real estate information"""
        info_type = await self.tools.classify_info_request(state.user_input)
        relevant_info = await self.tools.get_market_info(info_type)
        
        state.user_context.update({
            "info_type": info_type,
            "relevant_info": relevant_info
        })
        
        state.tools_used.append("general_info")
        return state
    
    async def _escalate_to_human(self, state: ConversationState) -> ConversationState:
        """Handle escalation to human agent"""
        escalation_reason = await self.tools.analyze_escalation_need(state.user_input)
        
        state.user_context.update({
            "escalation_reason": escalation_reason,
            "human_agent_needed": True,
            "priority_level": await self.tools.determine_priority(escalation_reason)
        })
        
        state.tools_used.append("escalate_human")
        return state
    
    async def _generate_response(self, state: ConversationState) -> ConversationState:
        """Generate final response based on context and configuration"""
        config = await self.config_manager.get_agent_config()
        
        system_prompt = f"""
        You are a {config.get('personality', 'professional and friendly real estate assistant')}.
        
        System Instructions: {config.get('system_prompt', 'Help users with real estate needs')}
        
        Current conversation step: {state.current_step}
        User input: {state.user_input}
        Context: {json.dumps(state.user_context, indent=2)}
        Lead info: {json.dumps(state.lead_info, indent=2)}
        Tools used: {state.tools_used}
        
        Response style: {config.get('response_style', 'conversational')}
        Max response length: {config.get('max_response_length', 200)} words
        
        Generate an appropriate response that:
        1. Addresses the user's needs based on the current step
        2. Uses the context information effectively
        3. Maintains the configured personality
        4. Encourages next steps in the real estate journey
        """
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": state.user_input}
        ]
        
        response = await self.llm.ainvoke(messages)
        state.agent_response = response.content
        
        # Add to conversation history
        state.messages.extend([
            {"role": "user", "content": state.user_input},
            {"role": "assistant", "content": state.agent_response}
        ])
        
        return state
    
    async def chat(self, message: str, conversation_history: List[Dict] = None) -> Dict[str, Any]:
        """Main chat interface"""
        initial_state = ConversationState(
            user_input=message,
            messages=conversation_history or []
        )
        
        # Run the graph
        final_state = await self.graph.ainvoke(initial_state)
        
        # Save conversation and lead data if configured
        if final_state.lead_info:
            await self.tools.save_lead_data(final_state.lead_info)
        
        return {
            "response": final_state.agent_response,
            "conversation_history": final_state.messages,
            "lead_info": final_state.lead_info,
            "tools_used": final_state.tools_used,
            "current_step": final_state.current_step
        } 