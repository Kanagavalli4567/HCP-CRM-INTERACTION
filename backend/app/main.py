from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import engine, Base
from .routers import interactions, hcp, agent

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="HCP CRM API", version="1.0.0")

# CORS middleware - Allow frontend to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(interactions.router)
app.include_router(hcp.router)
app.include_router(agent.router)

@app.get("/")
def root():
    return {"message": "HCP CRM API is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)