# app/services/ocr_service.py
"""
DeepSeek-OCR service for mypadi
Extracts phone numbers, meter numbers, etc. from images
"""
import logging
import re
from typing import Optional
from PIL import Image
import io
import requests
import aiohttp
import asyncio

logger = logging.getLogger(__name__)

class OCRService:
    def __init__(self):
        self.ocr_model = None
        self._load_model()
    
    def _load_model(self):
        """Load DeepSeek-OCR model (CPU mode)"""
        try:
            from transformers import pipeline
            self.ocr_model = pipeline(
                "image-to-text",
                model="deepseek-ai/deepseek-ocr-v2-base",
                device=-1  # CPU mode
            )
            logger.info("DeepSeek-OCR model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load OCR model: {str(e)}")
            raise
    
    def extract_text(self, image_bytes: bytes) -> str:
        """Extract text from image bytes"""
        try:
            # Convert bytes to image
            image = Image.open(io.BytesIO(image_bytes))
            
            # Preprocess for better OCR
            image = self._preprocess_image(image)
            
            # Run OCR
            result = self.ocr_model(image)
            text = result[0]['generated_text']
            
            logger.info(f"OCR extracted text: {text[:100]}...")
            return text
        except Exception as e:
            logger.error(f"OCR extraction failed: {str(e)}")
            return ""
    
    def extract_phone_number(self, image_bytes: bytes) -> Optional[str]:
        """Extract Nigerian phone number from image"""
        text = self.extract_text(image_bytes)
        if not text:
            return None
        
        # Nigerian phone number patterns
        patterns = [
            r'0[789][01]\d{8}',  # 08012345678
            r'\+234[789][01]\d{8}',  # +2348012345678
            r'234[789][01]\d{8}',  # 2348012345678
            r'[789][01]\d{8}',  # 8012345678 (without leading 0)
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text)
            if matches:
                # Standardize to 08012345678 format
                number = matches[0]
                if number.startswith('+234'):
                    number = '0' + number[4:]
                elif number.startswith('234'):
                    number = '0' + number[3:]
                elif len(number) == 10:  # 8012345678
                    number = '0' + number
                
                logger.info(f"Found phone number: {number}")
                return number
        
        return None
    
    def _preprocess_image(self, image: Image.Image) -> Image.Image:
        """Preprocess image for better OCR results"""
        # Resize if too large
        if image.size[0] > 1200 or image.size[1] > 1200:
            image = image.resize((1200, 1200))
        
        # Convert to RGB if needed
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        return image

    async def extract_from_url(self, image_url: str) -> str:
        """Download image from URL and extract text."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(image_url) as response:
                    if response.status == 200:
                        image_bytes = await response.read()
                        return self.extract_text(image_bytes)
                    else:
                        logger.error(f"Failed to download image: {response.status}")
                        return ""
        except Exception as e:
            logger.error(f"Error downloading image: {str(e)}")
            return ""
    
    async def extract_phone_from_url(self, image_url: str) -> Optional[str]:
        """Download image and extract phone number."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(image_url) as response:
                    if response.status == 200:
                        image_bytes = await response.read()
                        return self.extract_phone_number(image_bytes)
        except Exception as e:
            logger.error(f"Error extracting phone from URL: {str(e)}")
    

        return None



# Global OCR service instance
ocr_service = OCRService()