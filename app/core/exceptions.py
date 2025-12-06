"""
Custom exceptions for mypadi application.
"""
from typing import Any, Optional, Dict

class MypadiException(Exception):
    """Base exception for mypadi application."""
    
    def __init__(
        self, 
        message: str = "An error occurred",
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)

class VTUException(MypadiException):
    """Exception raised for VTU service errors."""
    
    def __init__(self, message: str = "VTU service error", details: Optional[Dict] = None):
        super().__init__(message, 422, details)

class PaymentException(MypadiException):
    """Exception raised for payment processing errors."""
    
    def __init__(self, message: str = "Payment processing error", details: Optional[Dict] = None):
        super().__init__(message, 402, details)

class FlightServiceException(MypadiException):
    """Exception raised for flight service errors."""
    
    def __init__(self, message: str = "Flight service error", details: Optional[Dict] = None):
        super().__init__(message, 422, details)

class LLMException(MypadiException):
    """Exception raised for AI/Language model errors."""
    
    def __init__(self, message: str = "AI service error", details: Optional[Dict] = None):
        super().__init__(message, 500, details)