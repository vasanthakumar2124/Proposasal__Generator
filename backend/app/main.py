from contextlib import asynccontextmanager

from fastapi.middleware.cors import CORSMiddleware

from fastapi import FastAPI

from app.api.routes import router as proposal_router
from app.api.ai_routes import router as ai_router
from app.database.mongodb import client


@asynccontextmanager
async def lifespan(app: FastAPI):

    try:
        await client.admin.command("ping")
        print("MongoDB Connected Successfully")
    except Exception as e:
        print(f"MongoDB Connection Failed: {e}")

    yield

    client.close()
    print("MongoDB Connection Closed")


app = FastAPI(
    title="AI Proposal Generator API",
    description="POC Backend for AI Proposal Generator",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(

    CORSMiddleware,

    allow_origins=[
        "http://localhost:5173"
    ],

    allow_credentials=True,

    allow_methods=["*"],

    allow_headers=["*"]

)

# Register Routers
app.include_router(proposal_router)
app.include_router(ai_router)


@app.get("/")
async def root():
    return {
        "message": "Welcome to AI Proposal Generator"
    }


@app.get("/health")
async def health():
    return {
        "status": "healthy"
    }