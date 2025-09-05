#!/usr/bin/env python3
"""
Main entry point for the LangGraph memory agent application.
This file provides a web server interface for Railway deployment.
"""

import os
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import json

# Import the graph from memory_agent.py
from memory_agent import graph
from langgraph.store.memory import InMemoryStore

# Initialize FastAPI app
app = FastAPI(
    title="Memory Agent API",
    description="A LangGraph-based memory agent with user profile and todo management",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the store
store = InMemoryStore()

# Pydantic models for API
class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    user_id: Optional[str] = "default-user"

class ChatResponse(BaseModel):
    response: str
    user_id: str

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "Memory Agent API is running", "status": "healthy"}

@app.get("/health")
async def health_check():
    """Health check endpoint for Railway"""
    return {"status": "healthy", "service": "memory-agent"}

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Main chat endpoint that processes messages through the LangGraph agent
    """
    try:
        # Convert messages to LangChain format
        from langchain_core.messages import HumanMessage, AIMessage
        
        messages = []
        for msg in request.messages:
            if msg.role == "user":
                messages.append(HumanMessage(content=msg.content))
            elif msg.role == "assistant":
                messages.append(AIMessage(content=msg.content))
        
        # Create configuration
        config = {
            "configurable": {
                "user_id": request.user_id
            }
        }
        
        # Run the graph
        result = graph.invoke(
            {"messages": messages},
            config=config,
            stream_mode="values"
        )
        
        # Extract the response
        if result and "messages" in result:
            last_message = result["messages"][-1]
            response_content = last_message.content if hasattr(last_message, 'content') else str(last_message)
        else:
            response_content = "I apologize, but I couldn't process your request."
        
        return ChatResponse(
            response=response_content,
            user_id=request.user_id
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing chat: {str(e)}")

@app.get("/memory/{user_id}")
async def get_memory(user_id: str):
    """
    Get stored memory for a specific user
    """
    try:
        # Search for memories in different namespaces
        profile_memories = store.search(("profile", user_id))
        todo_memories = store.search(("todo", user_id))
        instruction_memories = store.search(("instructions", user_id))
        
        return {
            "user_id": user_id,
            "profile": [mem.value for mem in profile_memories],
            "todos": [mem.value for mem in todo_memories],
            "instructions": [mem.value for mem in instruction_memories]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving memory: {str(e)}")

if __name__ == "__main__":
    # Get port from environment variable (Railway sets this)
    port = int(os.environ.get("PORT", 8000))
    
    # Run the server
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=False
    )
