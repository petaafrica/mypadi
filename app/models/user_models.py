"""
Database models for users and agents.
"""
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, EmailStr, validator
from datetime import datetime
from enum import Enum

class UserType(str, Enum):
    CUSTOMER = "customer"
    AGENT = "agent"
    ADMIN = "admin"

class UserStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    PENDING = "pending"

class UserBase(BaseModel):
    phone: str
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    language_preference: str = "pidgin"
    user_type: UserType = UserType.CUSTOMER

class UserCreate(UserBase):
    referral_code: Optional[str] = None

class User(UserBase):
    id: str
    wallet_balance: float = 0.0
    status: UserStatus = UserStatus.ACTIVE
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class AgentProfile(BaseModel):
    user_id: str
    agent_code: str  # Unique agent identification code
    business_name: Optional[str] = None
    business_address: Optional[str] = None
    state: Optional[str] = None
    lga: Optional[str] = None  # Local Government Area
    id_type: Optional[str] = None  # ID card type
    id_number: Optional[str] = None
    id_image_url: Optional[str] = None
    is_verified: bool = False
    total_commission: float = 0.0
    pending_commission: float = 0.0
    total_transactions: int = 0
    agent_tier: str = "bronze"  # bronze, silver, gold
    
    class Config:
        from_attributes = True

class AgentOnboardingRequest(BaseModel):
    business_name: str
    business_address: str
    state: str
    lga: str
    id_type: str
    id_number: str
    id_image_url: str

class CommissionRecord(BaseModel):
    agent_id: str
    transaction_id: str
    transaction_type: str
    transaction_amount: float
    commission_rate: float
    commission_amount: float
    customer_phone: str
    created_at: datetime
    
    class Config:
        from_attributes = True