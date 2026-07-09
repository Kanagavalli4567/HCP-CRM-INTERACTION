# backend/app/agents/tools.py
from typing import Dict, Any, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from .. import crud, schemas

class HCPTools:
    def __init__(self, db: Session):
        self.db = db
    
    def log_interaction(self, hcp_id: int, interaction_data: Dict[str, Any]) -> Dict[str, Any]:
        """Tool 1: Log Interaction - Captures interaction data with AI summarization"""
        try:
            # Prepare interaction data
            interaction = schemas.InteractionCreate(
                hcp_id=hcp_id,
                interaction_type=interaction_data.get('interaction_type', 'Meeting'),
                date=interaction_data.get('date', datetime.now()),
                topics=interaction_data.get('topics', ''),
                summary=interaction_data.get('summary', ''),
                sentiment=interaction_data.get('sentiment', 'Neutral'),
                outcomes=interaction_data.get('outcomes', ''),
                follow_up=interaction_data.get('follow_up', ''),
                materials_shared=interaction_data.get('materials_shared', ''),
                samples_distributed=interaction_data.get('samples_distributed', '')
            )
            
            # Save to database
            created_interaction = crud.create_interaction(self.db, interaction)
            
            return {
                "success": True,
                "message": "✅ Interaction logged successfully!",
                "interaction_id": created_interaction.id,
                "data": {
                    "id": created_interaction.id,
                    "hcp_id": created_interaction.hcp_id,
                    "type": created_interaction.interaction_type,
                    "date": created_interaction.date.isoformat(),
                    "summary": created_interaction.summary
                }
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"❌ Failed to log interaction: {str(e)}"
            }
    
    def edit_interaction(self, interaction_id: int, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """Tool 2: Edit Interaction - Modifies logged data"""
        try:
            update = schemas.InteractionUpdate(**update_data)
            updated_interaction = crud.update_interaction(self.db, interaction_id, update)
            
            if updated_interaction:
                return {
                    "success": True,
                    "message": "✅ Interaction updated successfully!",
                    "interaction_id": interaction_id,
                    "data": {
                        "id": updated_interaction.id,
                        "type": updated_interaction.interaction_type,
                        "summary": updated_interaction.summary
                    }
                }
            else:
                return {
                    "success": False,
                    "message": "❌ Interaction not found"
                }
        except Exception as e:
            return {
                "success": False,
                "message": f"❌ Failed to update interaction: {str(e)}"
            }
    
    def get_hcp_details(self, hcp_id: int) -> Dict[str, Any]:
        """Tool 3: Get HCP Details - Retrieves HCP information"""
        try:
            hcp = crud.get_hcp(self.db, hcp_id)
            if hcp:
                return {
                    "success": True,
                    "data": {
                        "id": hcp.id,
                        "name": hcp.name,
                        "specialty": hcp.specialty or "Not specified",
                        "hospital": hcp.hospital or "Not specified",
                        "email": hcp.email or "Not specified",
                        "phone": hcp.phone or "Not specified"
                    }
                }
            return {"success": False, "message": "❌ HCP not found"}
        except Exception as e:
            return {"success": False, "message": f"❌ Error: {str(e)}"}
    
    def get_interaction_history(self, hcp_id: int, limit: int = 5) -> Dict[str, Any]:
        """Tool 4: Get Interaction History - Retrieves past interactions"""
        try:
            interactions = crud.get_hcp_interactions(self.db, hcp_id, limit)
            if interactions:
                return {
                    "success": True,
                    "data": [
                        {
                            "id": i.id,
                            "type": i.interaction_type,
                            "date": i.date.isoformat(),
                            "summary": i.summary or "No summary",
                            "sentiment": i.sentiment or "Neutral"
                        }
                        for i in interactions
                    ]
                }
            return {"success": True, "data": [], "message": "No interactions found"}
        except Exception as e:
            return {"success": False, "message": f"❌ Error: {str(e)}"}
    
    def schedule_follow_up(self, hcp_id: int, follow_up_data: Dict[str, Any]) -> Dict[str, Any]:
        """Tool 5: Schedule Follow-up - Schedules future interactions"""
        try:
            return {
                "success": True,
                "message": "✅ Follow-up scheduled successfully!",
                "follow_up": {
                    "hcp_id": hcp_id,
                    "date": follow_up_data.get('date', datetime.now().isoformat()),
                    "notes": follow_up_data.get('notes', 'Follow-up meeting'),
                    "type": follow_up_data.get('type', 'Call')
                }
            }
        except Exception as e:
            return {"success": False, "message": f"❌ Error: {str(e)}"}
    
    def search_hcp(self, search_term: str) -> Dict[str, Any]:
        """Tool 6: Search HCP - Find HCPs by name or specialty"""
        try:
            hcps = crud.get_hcps(self.db)
            results = [
                hcp for hcp in hcps 
                if search_term.lower() in hcp.name.lower() 
                or (hcp.specialty and search_term.lower() in hcp.specialty.lower())
            ]
            return {
                "success": True,
                "data": [
                    {
                        "id": hcp.id,
                        "name": hcp.name,
                        "specialty": hcp.specialty or "Not specified"
                    }
                    for hcp in results[:5]
                ]
            }
        except Exception as e:
            return {"success": False, "message": f"❌ Error: {str(e)}"}