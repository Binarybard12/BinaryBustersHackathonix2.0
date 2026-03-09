from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
import time
import logging
from .routes import router as api_router

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Smart Internship Portal API",
    description="AI-powered internship matching and ATS scoring engine",
    version="1.0.0"
)

# Production Middlewares
app.add_middleware(GZipMiddleware, minimum_size=1000)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"], # Tighten in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def add_process_time_header(request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    logger.info(f"Method: {request.method} Path: {request.url.path} Time: {process_time:.4f}s")
    return response

app.include_router(api_router, prefix="/api")

# Root endpoint for health check
@app.get("/")
async def root():
    return {"message": "Smart Internship Portal API is running"}
