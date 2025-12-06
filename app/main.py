"""
Main FastAPI application setup with all routes and middleware.
"""
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import time
import logging

from app.core.config import settings
from app.routes import webhooks, users, admin
from app.core.exceptions import MypadiException

# Configure logging
logging.basicConfig(
    level=logging.INFO,
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
        docs_url="/docs" if settings.DEBUG else None,  # Hide docs in production
        redoc_url="/redoc" if settings.DEBUG else None,
    )
    
    # Add CORS middleware
    application.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Adjust in production
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
            f"{request.client.host} - \"{request.method} {request.url.path}\" "
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
    
    # Include routers
    application.include_router(
        webhooks.router, 
        prefix="/api/v1/webhooks", 
        tags=["webhooks"]
    )
    application.include_router(
        users.router, 
        prefix="/api/v1/users", 
        tags=["users"]
    )
    application.include_router(
        admin.router, 
        prefix="/api/v1/admin", 
        tags=["admin"]
    )
    application.include_router(  # NEW: Agent routes
        agents.router, 
        prefix="/api/v1/agents", 
        tags=["agents"]
    )
    # Health check endpoint
    @application.get("/")
    async def root():
        return {
            "message": f"Welcome to {settings.APP_NAME}!",
            "status": "healthy",
            "version": settings.APP_VERSION
        }
    
    @application.get("/health")
    async def health_check():
        return {"status": "healthy", "timestamp": time.time()}
    
    return application


    # Add to app/main.py after existing routes
    @app.get("/ocr-test")
    async def ocr_test():
        """Test OCR service with a simple image."""
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
        from app.services.ocr_service import ocr_service
        phone = ocr_service.extract_phone_number(img_bytes)
        
        return {
            "ocr_service": "working" if phone else "not working",
            "extracted_phone": phone,
            "test_image": "created_with_number_08012345678"
        }

# Create the FastAPI app instance
app = create_application()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info"
    )