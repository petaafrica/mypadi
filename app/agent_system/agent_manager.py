"""
Agent management system for mypadi.
Handles agent onboarding, commissions, and performance tracking.
"""
import logging
import uuid
from typing import Optional, Dict, Any, List
from datetime import datetime

from app.core.exceptions import MypadiException
from app.clients.supabase_client import supabase

logger = logging.getLogger(__name__)

class AgentManager:
    """Manages agent operations and commission tracking."""
    
    def __init__(self):
        self.commission_rate = 0.05  # 5% default commission
    
    async def onboard_agent(self, user_id: str, onboarding_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Onboard a new agent with verification process.
        
        Args:
            user_id: The user ID to convert to agent
            onboarding_data: Agent business and identification info
            
        Returns:
            Agent profile data
        """
        try:
            # Generate unique agent code
            agent_code = self._generate_agent_code()
            
            # Create agent profile
            agent_profile = {
                "user_id": user_id,
                "agent_code": agent_code,
                "business_name": onboarding_data.get("business_name"),
                "business_address": onboarding_data.get("business_address"),
                "state": onboarding_data.get("state"),
                "lga": onboarding_data.get("lga"),
                "id_type": onboarding_data.get("id_type"),
                "id_number": onboarding_data.get("id_number"),
                "id_image_url": onboarding_data.get("id_image_url"),
                "is_verified": False,  # Requires admin verification
                "created_at": datetime.utcnow().isoformat()
            }
            
            # Insert agent profile into database
            result = await supabase.table("agent_profiles").insert(agent_profile).execute()
            
            if not result.data:
                raise MypadiException("Failed to create agent profile")
            
            # Update user type to agent
            await supabase.table("users").update({
                "user_type": "agent",
                "updated_at": datetime.utcnow().isoformat()
            }).eq("id", user_id).execute()
            
            logger.info(f"Agent onboarding initiated for user {user_id} with code {agent_code}")
            
            return {
                "success": True,
                "agent_code": agent_code,
                "message": "Agent onboarding submitted for verification",
                "next_steps": "Admin verification required within 24-48 hours"
            }
            
        except Exception as e:
            logger.error(f"Agent onboarding failed for user {user_id}: {str(e)}")
            raise MypadiException(f"Agent onboarding failed: {str(e)}")
    
    async def record_commission(
        self, 
        agent_id: str, 
        transaction_id: str, 
        transaction_type: str,
        transaction_amount: float,
        customer_phone: str
    ) -> Dict[str, Any]:
        """
        Record commission for an agent's transaction.
        
        Args:
            agent_id: The agent's user ID
            transaction_id: Unique transaction ID
            transaction_type: Type of transaction (airtime, data, bill, flight)
            transaction_amount: Total transaction amount
            customer_phone: Customer's phone number
            
        Returns:
            Commission record
        """
        try:
            commission_amount = transaction_amount * self.commission_rate
            
            commission_record = {
                "id": str(uuid.uuid4()),
                "agent_id": agent_id,
                "transaction_id": transaction_id,
                "transaction_type": transaction_type,
                "transaction_amount": transaction_amount,
                "commission_rate": self.commission_rate,
                "commission_amount": commission_amount,
                "customer_phone": customer_phone,
                "created_at": datetime.utcnow().isoformat()
            }
            
            # Insert commission record
            result = await supabase.table("commission_records").insert(commission_record).execute()
            
            if not result.data:
                raise MypadiException("Failed to record commission")
            
            # Update agent's pending commission
            agent_profile = await supabase.table("agent_profiles").select("*").eq("user_id", agent_id).execute()
            if agent_profile.data:
                current_pending = agent_profile.data[0].get("pending_commission", 0)
                total_commission = agent_profile.data[0].get("total_commission", 0)
                total_transactions = agent_profile.data[0].get("total_transactions", 0)
                
                await supabase.table("agent_profiles").update({
                    "pending_commission": current_pending + commission_amount,
                    "total_commission": total_commission + commission_amount,
                    "total_transactions": total_transactions + 1,
                    "updated_at": datetime.utcnow().isoformat()
                }).eq("user_id", agent_id).execute()
            
            logger.info(f"Commission recorded for agent {agent_id}: ₦{commission_amount}")
            
            return {
                "success": True,
                "commission_amount": commission_amount,
                "transaction_amount": transaction_amount,
                "commission_rate": self.commission_rate
            }
            
        except Exception as e:
            logger.error(f"Commission recording failed for agent {agent_id}: {str(e)}")
            raise MypadiException(f"Commission recording failed: {str(e)}")
    
    async def get_agent_dashboard(self, agent_id: str) -> Dict[str, Any]:
        """
        Get agent dashboard data with performance metrics.
        
        Args:
            agent_id: The agent's user ID
            
        Returns:
            Dashboard data with stats and recent transactions
        """
        try:
            # Get agent profile
            agent_result = await supabase.table("agent_profiles").select("*").eq("user_id", agent_id).execute()
            if not agent_result.data:
                raise MypadiException("Agent profile not found")
            
            agent_profile = agent_result.data[0]
            
            # Get recent commissions (last 30 days)
            thirty_days_ago = datetime.utcnow().replace(day=datetime.utcnow().day-30)
            commissions_result = await supabase.table("commission_records")\
                .select("*")\
                .eq("agent_id", agent_id)\
                .gte("created_at", thirty_days_ago.isoformat())\
                .order("created_at", desc=True)\
                .limit(20)\
                .execute()
            
            # Calculate monthly stats
            monthly_commission = sum(
                commission.get("commission_amount", 0) 
                for commission in commissions_result.data
            )
            
            monthly_transactions = len(commissions_result.data)
            
            dashboard_data = {
                "agent_code": agent_profile.get("agent_code"),
                "business_name": agent_profile.get("business_name"),
                "is_verified": agent_profile.get("is_verified", False),
                "total_commission": agent_profile.get("total_commission", 0),
                "pending_commission": agent_profile.get("pending_commission", 0),
                "total_transactions": agent_profile.get("total_transactions", 0),
                "monthly_commission": monthly_commission,
                "monthly_transactions": monthly_transactions,
                "commission_rate": self.commission_rate,
                "recent_transactions": commissions_result.data[:10],
                "performance_tier": agent_profile.get("agent_tier", "bronze")
            }
            
            return dashboard_data
            
        except Exception as e:
            logger.error(f"Failed to get dashboard for agent {agent_id}: {str(e)}")
            raise MypadiException(f"Failed to load agent dashboard: {str(e)}")
    
    def _generate_agent_code(self) -> str:
        """Generate unique agent code in format MPAGENTXXXX."""
        import random
        import string
        
        # Generate random 4-digit number
        random_digits = ''.join(random.choices(string.digits, k=4))
        agent_code = f"MPAGENT{random_digits}"
        
        return agent_code
    
    async def process_agent_payout(self, agent_id: str, amount: float) -> Dict[str, Any]:
        """
        Process commission payout for an agent.
        
        Args:
            agent_id: The agent's user ID
            amount: Amount to payout
            
        Returns:
            Payout result
        """
        try:
            # Get agent's pending commission
            agent_profile = await supabase.table("agent_profiles").select("*").eq("user_id", agent_id).execute()
            if not agent_profile.data:
                raise MypadiException("Agent profile not found")
            
            pending_commission = agent_profile.data[0].get("pending_commission", 0)
            
            if amount > pending_commission:
                raise MypadiException("Requested amount exceeds pending commission")
            
            if amount < 1000:  # Minimum payout
                raise MypadiException("Minimum payout amount is ₦1000")
            
            # Process payout (integrate with PalmPay later)
            # For now, just update the pending commission
            new_pending = pending_commission - amount
            
            await supabase.table("agent_profiles").update({
                "pending_commission": new_pending,
                "updated_at": datetime.utcnow().isoformat()
            }).eq("user_id", agent_id).execute()
            
            # Record payout transaction
            payout_record = {
                "id": str(uuid.uuid4()),
                "agent_id": agent_id,
                "amount": amount,
                "status": "processed",
                "processed_at": datetime.utcnow().isoformat()
            }
            
            await supabase.table("payout_records").insert(payout_record).execute()
            
            logger.info(f"Payout processed for agent {agent_id}: ₦{amount}")
            
            return {
                "success": True,
                "amount_paid": amount,
                "remaining_balance": new_pending,
                "message": f"₦{amount} payout processed successfully"
            }
            
        except Exception as e:
            logger.error(f"Payout processing failed for agent {agent_id}: {str(e)}")
            raise MypadiException(f"Payout processing failed: {str(e)}")

# Create global agent manager instance
agent_manager = AgentManager()