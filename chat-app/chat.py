import os
from fastapi import FastAPI, Request, Response
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import openai
import asyncio

app = FastAPI(title="Real Estate Chat API", version="1.0.0")

# CORS for frontend
origins = [
    "http://localhost:3000",
    "http://localhost:3001",
    "http://localhost:5173",
    "https://pubx-real.netlify.app",
    "https://roy-estate-agent.netlify.app",
    os.getenv("CORS_ORIGIN", "*")
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")

@app.get("/")
async def root():
    return JSONResponse({
        "message": "Real Estate Chat API is running!", 
        "status": "ok",
        "version": "1.0.0",
        "endpoints": {
            "GET /api/chat": "Health check endpoint",
            "POST /api/chat": "Chat with the real estate agent"
        }
    })

@app.get("/api/chat")
async def chat_get():
    return JSONResponse({
        "message": "Real Estate Chat API endpoint", 
        "method": "GET",
        "status": "ready"
    })

@app.post("/api/chat")
async def chat_endpoint(request: Request):
    try:
        data = await request.json()
        user_message = data.get("message", "")
        
        if not user_message:
            return JSONResponse(
                {"error": "No message provided"}, 
                status_code=400
            )

        # For now, just echo the message (LangGraph/LLM integration coming next)
        # Later: Replace with LangGraph orchestration and OpenAI streaming
        response_message = f"Echo: {user_message}"
        
        return JSONResponse({
            "response": response_message,
            "status": "success",
            "message_length": len(user_message)
        })
        
    except Exception as e:
        return JSONResponse(
            {"error": str(e), "status": "error"}, 
            status_code=500
        )

@app.get("/health")
async def health_check():
    return JSONResponse({
        "status": "healthy",
        "openai_configured": bool(os.getenv("OPENAI_API_KEY")),
        "cors_origin": os.getenv("CORS_ORIGIN", "not_set")
    })

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080) 