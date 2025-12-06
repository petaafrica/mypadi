"""
Main FastAPI application setup with all routes and middleware.
"""
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import time
import logging

from app.core.config import settings
from app.core.exceptions import MypadiException

# Configure logging
logging.basicConfig(
    level=logging.INFO if not settings.DEBUG else logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('storage/logs/mypadi.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def create_application() -> FastAPI:
    """Create and configure FastAPI application."""
    
    application = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        debug=settings.DEBUG,
        docs_url="/docs" if settings.DEBUG else None,
        redoc_url="/redoc" if settings.DEBUG else None,
    )
    
    # Add CORS middleware
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Add middleware for request logging
    @application.middleware("http")
    async def log_requests(request: Request, call_next):
        start_time = time.time()
        
        response = await call_next(request)
        
        process_time = time.time() - start_time
        logger.info(
            f"{request.client.host if request.client else 'unknown'} - "
            f"\"{request.method} {request.url.path}\" "
            f"{response.status_code} - {process_time:.2f}s"
        )
        
        return response
    
    # Custom exception handler
    @application.exception_handler(MypadiException)
    async def mypadi_exception_handler(request: Request, exc: MypadiException):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "error": exc.message,
                "details": exc.details
            }
        )
    
    # Import and include routers dynamically
    try:
        from app.routes.webhooks import router as webhooks_router
        application.include_router(
            webhooks_router, 
            prefix="/api/v1/webhooks", 
            tags=["webhooks"]
        )
        logger.info("Webhooks router loaded successfully")
    except ImportError as e:
        logger.warning(f"Webhooks router not loaded: {e}")
    
    try:
        from app.routes.users import router as users_router
        application.include_router(
            users_router, 
            prefix="/api/v1/users", 
            tags=["users"]
        )
        logger.info("Users router loaded successfully")
    except ImportError as e:
        logger.warning(f"Users router not loaded: {e}")
    
    try:
        from app.routes.admin import router as admin_router
        application.include_router(
            admin_router, 
            prefix="/api/v1/admin", 
            tags=["admin"]
        )
        logger.info("Admin router loaded successfully")
    except ImportError as e:
        logger.warning(f"Admin router not loaded: {e}")
    
    try:
        from app.routes.agents import router as agents_router
        application.include_router(
            agents_router, 
            prefix="/api/v1/agents", 
            tags=["agents"]
        )
        logger.info("Agents router loaded successfully")
    except ImportError as e:
        logger.warning(f"Agents router not loaded: {e}")
    
    # Health check endpoint
    @application.get("/")
    async def root():
        return {
            "message": f"Welcome to {settings.APP_NAME}!",
            "status": "healthy",
            "version": settings.APP_VERSION,
            "docs": "/docs" if settings.DEBUG else None
        }
    
    @application.get("/health")
    async def health_check():
        """Comprehensive health check."""
        from app.services.ocr_service import ocr_service
        
        checks = {
            "api": "healthy",
            "ocr_service": "unknown",
            "database": "unknown",
            "whatsapp": "unknown"
        }
        
        # Check OCR service
        try:
            # Quick OCR test
            from PIL import Image, ImageDraw
            import io
            
            img = Image.new('RGB', (100, 50), color='white')
            d = ImageDraw.Draw(img)
            d.text((10, 10), "test", fill='black')
            
            img_bytes = io.BytesIO()
            img.save(img_bytes, format='PNG')
            img_bytes = img_bytes.getvalue()
            
            text = ocr_service.extract_text(img_bytes)
            checks["ocr_service"] = "working" if text else "error"
        except Exception as e:
            checks["ocr_service"] = f"error: {str(e)}"
        
        # Check database connection
        try:
            from app.clients.supabase_client import supabase_client
            if supabase_client.client:
                checks["database"] = "connected"
            else:
                checks["database"] = "mock_mode"
        except Exception as e:
            checks["database"] = f"error: {str(e)}"
        
        # Check WhatsApp connection
        try:
            from app.clients.twilio_client import twilio_client
            if twilio_client.client:
                checks["whatsapp"] = "connected"
            else:
                checks["whatsapp"] = "mock_mode"
        except Exception as e:
            checks["whatsapp"] = f"error: {str(e)}"
        
        return {
            "status": "healthy" if all("error" not in str(v) for v in checks.values()) else "degraded",
            "checks": checks,
            "timestamp": time.time()
        }
    
    # OCR test endpoint
    @application.get("/ocr-test")
    async def ocr_test():
        """Test OCR service with a simple image."""
        try:
            from app.services.ocr_service import ocr_service
            from PIL import Image, ImageDraw
            import io
            
            # Create test image
            img = Image.new('RGB', (300, 100), color='white')
            d = ImageDraw.Draw(img)
            d.text((50, 40), "08012345678", fill='black')
            
            img_bytes = io.BytesIO()
            img.save(img_bytes, format='PNG')
            img_bytes = img_bytes.getvalue()
            
            # Test OCR
            phone = ocr_service.extract_phone_number(img_bytes)
            
            return {
                "ocr_service": "working" if phone else "not_working",
                "extracted_phone": phone,
                "expected_phone": "08012345678",
                "match": phone == "08012345678"
            }
        except Exception as e:
            return {
                "ocr_service": "error",
                "error": str(e)
            }
    
    return application

# Create the FastAPI app instance
app = create_application()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="debug" if settings.DEBUG else "info"
    )