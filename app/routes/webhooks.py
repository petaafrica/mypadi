# Update app/routes/webhooks.py
import aiohttp
from app.clients.twilio_client import twilio_client
from app.clients.supabase_client import supabase_client
from app.services.ocr_service import ocr_service
import base64
import io


logger = logging.getLogger(__name__)
router = APIRouter() 
async def process_message(phone: str, message: str, media_url: str = None):
    """Process incoming WhatsApp message with OCR support."""
    try:
        logger.info(f"Processing message from {phone}")
        
        # Get or create user
        user = await supabase_client.get_or_create_user(phone)
        
        response = ""
        
        # Check for image with phone number
        if media_url and ("image" in media_url or "jpeg" in media_url or "png" in media_url):
            logger.info(f"Processing image from {phone}")
            
            # Extract phone number from image
            phone_number = await ocr_service.extract_phone_from_url(media_url)
            
            if phone_number:
                response = f"I found phone number: {phone_number} 📞\n"
                response += "How much airtime should I send? (e.g., ₦500)"
                
                # Store for context (we'll implement this later)
                logger.info(f"OCR successful: {phone} found {phone_number}")
            else:
                response = "I couldn't find a phone number in the image. 📸\n"
                response += "Please make sure the number is clear and try again!"
        
        # Handle text messages
        elif message:
            message_lower = message.lower().strip()
            
            if any(word in message_lower for word in ["hello", "hi", "hey"]):
                response = "Hello! I'm mypadi, your assistant! 👋\n"
                response += "Send me a photo of a phone number to send airtime!"
            
            elif "airtime" in message_lower:
                response = "To buy airtime:\n"
                response += "1. Send a photo of the phone number 📸\n"
                response += "2. Tell me the amount (e.g., ₦500)\n"
                response += "3. I'll send it instantly! ⚡"
            
            elif "help" in message_lower:
                response = "I can help you with:\n"
                response += "📞 Airtime purchase\n"
                response += "📱 Data bundles\n"
                response += "💡 Electricity bills\n"
                response += "📺 TV subscriptions\n"
                response += "🎓 WAEC/JAMB PINs\n\n"
                response += "Just send a photo or tell me what you need!"
            
            else:
                response = f"You said: {message}\n"
                response += "Try sending a photo of a phone number for airtime! 📸"
        
        # Send response
        if response:
            await twilio_client.send_message(phone, response)
            logger.info(f"Sent response to {phone}")
        else:
            logger.warning(f"No response generated for {phone}")
        
    except Exception as e:
        logger.error(f"Error processing message from {phone}: {str(e)}")
        # Send error message
        try:
            await twilio_client.send_message(
                phone,
                "Sorry, I encountered an error. Please try again later. 😔"
            )
        except:
            pass
__all__ = ["router"] 