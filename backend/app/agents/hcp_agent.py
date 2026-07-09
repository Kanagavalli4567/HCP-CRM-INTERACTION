# backend/app/agents/hcp_agent.py
import json
import re
from typing import Dict, Any, Optional
from datetime import datetime
from langgraph.graph import StateGraph, END
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
from sqlalchemy.orm import Session
from ..config import Config
from .tools import HCPTools

class HCPAgent:
    def __init__(self, db: Session):
        self.db = db
        self.tools = HCPTools(db)
        
        # Initialize Groq LLM
        try:
            self.llm = ChatGroq(
                temperature=0.7,
                groq_api_key=Config.GROQ_API_KEY,
                model_name=Config.GROQ_MODEL
            )
            self.llm_available = True
        except Exception as e:
            print(f"⚠️ Groq LLM not available: {e}. Using fallback responses.")
            self.llm_available = False
        
        # Build LangGraph workflow
        self.graph = self._build_graph()
    
    def _build_graph(self):
        """Build the LangGraph workflow"""
        graph = StateGraph(dict)
        
        # Add nodes
        graph.add_node("process_input", self._process_input)
        graph.add_node("analyze_intent", self._analyze_intent)
        graph.add_node("execute_tool", self._execute_tool)
        graph.add_node("generate_response", self._generate_response)
        
        # Define edges
        graph.set_entry_point("process_input")
        graph.add_edge("process_input", "analyze_intent")
        graph.add_conditional_edges(
            "analyze_intent",
            self._route_to_tool_or_response,
            {
                "tool": "execute_tool",
                "response": "generate_response"
            }
        )
        graph.add_edge("execute_tool", "generate_response")
        graph.add_edge("generate_response", END)
        
        return graph.compile()
    
    def _process_input(self, state: dict) -> dict:
        """Process the input message"""
        user_message = state.get("message", "").strip()
        state["processed_message"] = user_message
        return state
    
    def _analyze_intent(self, state: dict) -> dict:
        """Analyze user intent using LLM or pattern matching"""
        message = state.get("processed_message", "").lower()
        
        # Try LLM first if available
        if self.llm_available:
            try:
                prompt = f"""
                Analyze this message and determine the user's intent.
                Message: {message}
                
                Possible intents:
                - log_interaction: User wants to log a new interaction
                - edit_interaction: User wants to edit an existing interaction
                - view_hcp: User wants to see HCP details
                - view_history: User wants to see interaction history
                - schedule_followup: User wants to schedule a follow-up
                - search_hcp: User wants to search for an HCP
                - general_query: User is asking a general question
                - greeting: User is just saying hello
                
                Also extract any parameters like hcp_name, date, topics, etc.
                
                Respond with JSON: 
                {{
                    "intent": "intent_type",
                    "confidence": 0.0-1.0,
                    "params": {{"key": "value"}}
                }}
                """
                
                response = self.llm.invoke([HumanMessage(content=prompt)])
                intent_data = json.loads(response.content)
                state["intent"] = intent_data.get("intent", "general_query")
                state["confidence"] = intent_data.get("confidence", 0.5)
                state["params"] = intent_data.get("params", {})
                return state
            except Exception as e:
                print(f"LLM intent analysis failed: {e}")
        
        # Fallback: Pattern matching
        intent = "general_query"
        params = {}
        
        if any(word in message for word in ["hi", "hello", "hey", "greetings"]):
            intent = "greeting"
        elif any(word in message for word in ["log", "record", "add", "create", "new"]) and "interaction" in message:
            intent = "log_interaction"
            # Extract potential HCP name
            hcp_match = re.search(r'(?:with|for|dr\.?|doctor)\s+([a-zA-Z\s]+)', message)
            if hcp_match:
                params["hcp_name"] = hcp_match.group(1).strip()
        elif any(word in message for word in ["edit", "update", "change", "modify"]) and "interaction" in message:
            intent = "edit_interaction"
        elif any(word in message for word in ["view", "show", "get", "details"]) and "hcp" in message:
            intent = "view_hcp"
        elif any(word in message for word in ["history", "past", "previous", "old"]) and "interaction" in message:
            intent = "view_history"
        elif any(word in message for word in ["schedule", "plan", "set", "arrange"]) and ("follow" in message or "meeting" in message):
            intent = "schedule_followup"
        elif "search" in message and "hcp" in message:
            intent = "search_hcp"
        
        state["intent"] = intent
        state["confidence"] = 0.7 if intent != "general_query" else 0.3
        state["params"] = params
        return state
    
    def _route_to_tool_or_response(self, state: dict) -> str:
        """Route to tool or generate direct response"""
        intent = state.get("intent", "general_query")
        confidence = state.get("confidence", 0)
        
        # Tools that require execution
        tool_intents = ["log_interaction", "edit_interaction", "view_hcp", 
                       "view_history", "schedule_followup", "search_hcp"]
        
        if intent in tool_intents and confidence > 0.5:
            return "tool"
        return "response"
    
    def _execute_tool(self, state: dict) -> dict:
        """Execute the appropriate tool"""
        intent = state.get("intent")
        message = state.get("processed_message", "")
        params = state.get("params", {})
        
        # Get HCP ID from params or state
        hcp_id = params.get("hcp_id") or state.get("hcp_id")
        
        # If we have hcp_name but no id, try to find it
        if not hcp_id and params.get("hcp_name"):
            hcp_name = params.get("hcp_name")
            # Search for HCP by name
            hcps = crud.get_hcps(self.db)
            for hcp in hcps:
                if hcp_name.lower() in hcp.name.lower():
                    hcp_id = hcp.id
                    break
        
        result = None
        
        try:
            if intent == "log_interaction":
                # Extract interaction details from message
                if not hcp_id:
                    return {"success": False, "message": "❌ Please specify which HCP you want to log an interaction for."}
                
                interaction_data = {
                    "hcp_id": hcp_id,
                    "interaction_type": params.get("type", "Meeting"),
                    "topics": params.get("topics", "General discussion"),
                    "summary": params.get("summary", ""),
                    "sentiment": params.get("sentiment", "Neutral"),
                    "outcomes": params.get("outcomes", ""),
                    "follow_up": params.get("follow_up", "")
                }
                
                result = self.tools.log_interaction(hcp_id, interaction_data)
                
            elif intent == "edit_interaction":
                interaction_id = params.get("interaction_id")
                if not interaction_id:
                    return {"success": False, "message": "❌ Please specify which interaction to edit."}
                result = self.tools.edit_interaction(interaction_id, params)
                
            elif intent == "view_hcp":
                if not hcp_id:
                    return {"success": False, "message": "❌ Please specify which HCP you want to view."}
                result = self.tools.get_hcp_details(hcp_id)
                
            elif intent == "view_history":
                if not hcp_id:
                    return {"success": False, "message": "❌ Please specify which HCP's history you want to view."}
                result = self.tools.get_interaction_history(hcp_id)
                
            elif intent == "schedule_followup":
                if not hcp_id:
                    return {"success": False, "message": "❌ Please specify which HCP to schedule a follow-up with."}
                followup_data = {
                    "date": params.get("date", datetime.now().isoformat()),
                    "notes": params.get("notes", "Follow-up meeting"),
                    "type": params.get("type", "Call")
                }
                result = self.tools.schedule_follow_up(hcp_id, followup_data)
                
            elif intent == "search_hcp":
                search_term = params.get("search_term", message)
                result = self.tools.search_hcp(search_term)
                
        except Exception as e:
            result = {"success": False, "message": f"❌ Error executing tool: {str(e)}"}
        
        state["tool_result"] = result
        return state
    
    def _generate_response(self, state: dict) -> dict:
        """Generate final response"""
        tool_result = state.get("tool_result")
        message = state.get("processed_message", "")
        intent = state.get("intent", "general_query")
        
        # If greeting, respond with friendly message
        if intent == "greeting":
            state["response"] = """👋 Hello! I'm your AI-powered HCP CRM assistant.

I can help you with:
• 📝 **Log interactions** with HCPs
• 🔍 **Search and view** HCP profiles
• 📊 **View interaction history**
• ✏️ **Edit existing interactions**
• 📅 **Schedule follow-ups**

How can I assist you today? Just describe what you'd like to do!"""
            return state
        
        # If tool was executed
        if tool_result:
            if tool_result.get("success"):
                # Format success response with emojis
                if intent == "log_interaction":
                    state["response"] = f"""✅ **Interaction logged successfully!**

📋 Interaction ID: {tool_result.get('interaction_id')}
📅 Date: {tool_result.get('data', {}).get('date', 'Just now')}
📝 Summary: {tool_result.get('data', {}).get('summary', 'No summary')}

Would you like to log another interaction or view the updated history?"""
                elif intent == "edit_interaction":
                    state["response"] = f"""✅ **Interaction updated successfully!**

🔄 Changes have been saved.
📋 Updated ID: {tool_result.get('interaction_id')}

Is there anything else you'd like to edit?"""
                elif intent == "view_hcp":
                    data = tool_result.get('data', {})
                    state["response"] = f"""👤 **HCP Profile**

**Name:** {data.get('name', 'N/A')}
**Specialty:** {data.get('specialty', 'N/A')}
**Hospital:** {data.get('hospital', 'N/A')}
**Email:** {data.get('email', 'N/A')}
**Phone:** {data.get('phone', 'N/A')}

Would you like to view their interaction history or log a new interaction?"""
                elif intent == "view_history":
                    interactions = tool_result.get('data', [])
                    if interactions:
                        history_text = "\n".join([
                            f"• {i['date'][:10]} - **{i['type']}** - {i['summary'][:50]}..."
                            for i in interactions
                        ])
                        state["response"] = f"""📊 **Interaction History**

{history_text}

Would you like to view more details or log a new interaction?"""
                    else:
                        state["response"] = "📊 No interactions found for this HCP. Would you like to log one?"
                elif intent == "schedule_followup":
                    state["response"] = f"""📅 **Follow-up Scheduled!**

{tool_result.get('message')}
📌 Notes: {tool_result.get('follow_up', {}).get('notes', 'No notes')}

Would you like to schedule another follow-up?"""
                elif intent == "search_hcp":
                    results = tool_result.get('data', [])
                    if results:
                        result_text = "\n".join([
                            f"• **{r['name']}** - {r['specialty']} (ID: {r['id']})"
                            for r in results
                        ])
                        state["response"] = f"""🔍 **Search Results**

{result_text}

To view details or log an interaction, please specify which HCP you'd like to work with."""
                    else:
                        state["response"] = "🔍 No HCPs found matching your search. Try a different name or specialty."
                else:
                    state["response"] = f"✅ {tool_result.get('message', 'Operation completed successfully!')}"
            else:
                state["response"] = f"❌ {tool_result.get('message', 'Sorry, something went wrong.')}"
        else:
            # Generate general response with LLM
            if self.llm_available:
                try:
                    prompt = f"""
                    User message: {message}
                    Intent detected: {intent}
                    
                    Respond as a helpful HCP CRM assistant. 
                    - Be friendly and professional
                    - If the user wants to do something, guide them
                    - Suggest possible actions if the intent is unclear
                    - Keep responses concise but informative
                    """
                    
                    response = self.llm.invoke([HumanMessage(content=prompt)])
                    state["response"] = response.content
                except Exception as e:
                    state["response"] = f"I understand you're interested in HCP management. Could you tell me more about what you'd like to do? I can help with logging interactions, viewing profiles, checking history, or scheduling follow-ups."
            else:
                state["response"] = """I'm here to help you manage HCP interactions! I can:

1. 📝 **Log a new interaction** - "Log a meeting with Dr. Smith"
2. 🔍 **View HCP details** - "Show me Dr. Johnson's profile"
3. 📊 **View history** - "Show interactions with Dr. Chen"
4. ✏️ **Edit interactions** - "Update the last meeting"
5. 📅 **Schedule follow-up** - "Schedule a call with Dr. Williams"

What would you like to do?"""
        
        return state
    
    def process_message(self, message: str, hcp_id: Optional[int] = None) -> Dict[str, Any]:
        """Process a user message through the agent"""
        initial_state = {
            "message": message,
            "hcp_id": hcp_id,
            "intent": "",
            "confidence": 0,
            "params": {},
            "tool_result": None,
            "response": ""
        }
        
        try:
            result = self.graph.invoke(initial_state)
            return {
                "response": result.get("response", "I processed your request. How can I help further?"),
                "intent": result.get("intent", "general_query"),
                "tool_result": result.get("tool_result")
            }
        except Exception as e:
            return {
                "response": f"I encountered an error while processing your request. Please try again with a clearer description.",
                "intent": "error",
                "tool_result": {"success": False, "message": str(e)}
            }