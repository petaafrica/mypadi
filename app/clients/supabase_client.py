# app/clients/supabase_client.py
"""
Supabase client for database operations.
"""
import logging
from typing import Optional, Dict, Any, List
from supabase import create_client, Client

from app.core.config import settings

logger = logging.getLogger(__name__)

class SupabaseClient:
    def __init__(self):
        self.client: Optional[Client] = None
        self._connect()
    
    def _connect(self):
        """Connect to Supabase database."""
        try:
            if not settings.SUPABASE_URL or not settings.SUPABASE_KEY:
                logger.warning("Supabase URL or Key not set. Using mock mode for development.")
                self.client = None
                return
            
            self.client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
            logger.info("Connected to Supabase successfully")
        except Exception as e:
            logger.error(f"Failed to connect to Supabase: {str(e)}")
            self.client = None
    
    async def get_or_create_user(self, phone: str) -> Optional[Dict[str, Any]]:
        """Get user by phone or create if doesn't exist."""
        try:
            if not self.client:
                # Mock response for development
                return {
                    "id": "mock-user-id",
                    "phone": phone,
                    "language_preference": "pidgin",
                    "user_type": "customer",
                    "wallet_balance": 0.0
                }
            
            # Check if user exists
            response = self.client.table("users")\
                .select("*")\
                .eq("phone", phone)\
                .execute()
            
            if response.data and len(response.data) > 0:
                logger.info(f"User found: {phone}")
                return response.data[0]
            
            # Create new user
            new_user = {
                "phone": phone,
                "language_preference": "pidgin",
                "user_type": "customer",
                "wallet_balance": 0.0
            }
            
            response = self.client.table("users")\
                .insert(new_user)\
                .execute()
            
            logger.info(f"New user created: {phone}")
            return response.data[0] if response.data else None
            
        except Exception as e:
            logger.error(f"Error getting/creating user {phone}: {str(e)}")
            return None
    
    async def create_transaction(self, transaction_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create a new transaction record."""
        try:
            if not self.client:
                # Mock for development
                return {
                    "id": "mock-transaction-id",
                    **transaction_data
                }
            
            response = self.client.table("transactions")\
                .insert(transaction_data)\
                .execute()
            
            return response.data[0] if response.data else None
            
        except Exception as e:
            logger.error(f"Error creating transaction: {str(e)}")
            return None

# Global Supabase client instance
supabase_client = SupabaseClient()