# app/clients/twilio_client.py
"""
Twilio client for WhatsApp messaging.
"""
import logging
from typing import Optional, Dict, Any
from twilio.rest import Client as TwilioClient
from twilio.base.exceptions import TwilioRestException

from app.core.config import settings

logger = logging.getLogger(__name__)

class TwilioWhatsAppClient:
    def __init__(self):
        self.client: Optional[TwilioClient] = None
        self._connect()
    
    def _connect(self):
        """Initialize Twilio client."""
        try:
            if not settings.TWILIO_ACCOUNT_SID or not settings.TWILIO_AUTH_TOKEN:
                logger.warning("Twilio credentials not set. Using mock mode.")
                self.client = None
                return
            
            self.client = TwilioClient(
                settings.TWILIO_ACCOUNT_SID,
                settings.TWILIO_AUTH_TOKEN
            )
            logger.info("Twilio client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Twilio client: {str(e)}")
            self.client = None
    
    async def send_message(self, to: str, body: str) -> bool:
        """Send WhatsApp message to user."""
        try:
            if not self.client:
                logger.info(f"[MOCK] Would send to {to}: {body[:50]}...")
                return True
            
            message = self.client.messages.create(
                body=body,
                from_=settings.TWILIO_WHATSAPP_NUMBER,
                to=f"whatsapp:{to}"
            )
            
            logger.info(f"Message sent to {to}: SID {message.sid}")
            return True
            
        except TwilioRestException as e:
            logger.error(f"Twilio error sending to {to}: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Error sending message to {to}: {str(e)}")
            return False
    
    async def send_image(self, to: str, media_url: str, body: str = "") -> bool:
        """Send image via WhatsApp."""
        try:
            if not self.client:
                logger.info(f"[MOCK] Would send image to {to}: {media_url}")
                return True
            
            message = self.client.messages.create(
                body=body,
                media_url=[media_url],
                from_=settings.TWILIO_WHATSAPP_NUMBER,
                to=f"whatsapp:{to}"
            )
            
            logger.info(f"Image sent to {to}: {message.sid}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending image to {to}: {str(e)}")
            return False

# Global Twilio client instance
twilio_client = TwilioWhatsAppClient()