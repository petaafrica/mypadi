"""
API routes for agent management and operations.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any

from app.agent_system.agent_manager import agent_manager
from app.models.user_models import AgentOnboardingRequest
from app.core.security import get_current_user

router = APIRouter()

@router.post("/onboard")
async def onboard_agent(
    onboarding_data: AgentOnboardingRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Onboard a user as a mypadi agent."""
    try:
        result = await agent_manager.onboard_agent(
            user_id=current_user["id"],
            onboarding_data=onboarding_data.dict()
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/dashboard")
async def get_agent_dashboard(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get agent dashboard with performance metrics."""
    try:
        dashboard = await agent_manager.get_agent_dashboard(current_user["id"])
        return dashboard
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/payout")
async def request_payout(
    amount: float,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Request commission payout."""
    try:
        result = await agent_manager.process_agent_payout(
            agent_id=current_user["id"],
            amount=amount
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/transactions")
async def get_agent_transactions(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get agent's transaction history."""
    # Implementation for transaction history
    pass