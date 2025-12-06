# app/routes/admin.py
"""
Admin monitoring routes.
"""
from fastapi import APIRouter

router = APIRouter()

@router.get("/health")
async def admin_health():
    """Admin health check."""
    return {"status": "healthy", "service": "admin"}

@router.get("/stats")
async def get_stats():
    """Get system statistics."""
    return {
        "users": 0,
        "transactions": 0,
        "agents": 0,
        "revenue": 0.0
    }