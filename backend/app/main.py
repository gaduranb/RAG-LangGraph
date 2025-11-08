from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from langchain_core.messages import HumanMessage
import time

from app.agent.graph import agent_graph

app = FastAPI(title="Banking Login & Security Helper API")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://frontend:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    question: str

class Citation(BaseModel):
    title: str
    url: str

class ChatResponse(BaseModel):
    answer: str
    citations: List[Citation]
    timing_ms: int
    tool_calls: Optional[List[str]] = []

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    start_time = time.time()

    # Initialize state
    initial_state = {
        "messages": [HumanMessage(content=request.question)],
        "question": request.question,
        "answer": None,
        "citations": None,
        "tool_calls": [],
        "is_out_of_scope": False,
        "needs_holidays": False
    }

    # Run the agent graph
    result = await agent_graph.ainvoke(initial_state)

    timing_ms = int((time.time() - start_time) * 1000)

    # Extract results
    answer = result.get("answer", "I apologize, but I encountered an error processing your request.")
    citations_data = result.get("citations", [])
    tool_calls = result.get("tool_calls", [])

    # Convert citations to Pydantic models
    citations = [Citation(**c) for c in citations_data]

    return ChatResponse(
        answer=answer,
        citations=citations,
        timing_ms=timing_ms,
        tool_calls=tool_calls
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
