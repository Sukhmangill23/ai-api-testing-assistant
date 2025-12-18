from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.database import engine, Base
from app.routers import test_generation, test_execution, reports

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AI-Powered API Testing Assistant",
    description="Automatically generate and execute API tests using AI",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check route - PUT THIS FIRST!
@app.get("/health")
def health_check():
    return {"status": "healthy"}

# Include routers
app.include_router(test_generation.router)
app.include_router(test_execution.router)
app.include_router(reports.router)

# Mount static files for frontend - PUT THIS LAST!
app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
