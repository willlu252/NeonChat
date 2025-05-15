# app/api/routes/abacus_routes.py
from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, List, Optional
from pydantic import BaseModel

from ...services.abacus_service import abacus_service

# Create a router
router = APIRouter(prefix="/api", tags=["abacus"])

# Request models
class ImageGenerationRequest(BaseModel):
    prompt: str
    size: str = "1024x1024"
    count: int = 1
    quality: str = "standard"

class SearchRequest(BaseModel):
    query: str
    type: str = "normal"  # "normal" or "deep_research"

class DiaryEntryRequest(BaseModel):
    entry_text: str
    user_id: str
    context: Optional[List[Dict[str, str]]] = None

class ChatRequest(BaseModel):
    prompt: str
    model_id: Optional[str] = None
    conversation_history: Optional[List[Dict[str, str]]] = None

# API endpoints
@router.post("/generate-image")
async def generate_image(request: ImageGenerationRequest) -> Dict[str, Any]:
    """
    Generate images using Abacus.ai's image generation capabilities.
    """
    result = await abacus_service.generate_image(
        prompt=request.prompt,
        size=request.size,
        count=request.count,
        quality=request.quality
    )
    
    if not result.get("success", False):
        raise HTTPException(status_code=500, detail=result.get("error", "Unknown error occurred"))
    
    return result

@router.post("/search")
async def search(request: SearchRequest) -> Dict[str, Any]:
    """
    Perform a search using Abacus.ai's search agent.
    """
    result = await abacus_service.search(
        query=request.query,
        search_type=request.type
    )
    
    if not result.get("success", False):
        raise HTTPException(status_code=500, detail=result.get("error", "Unknown error occurred"))
    
    return result

@router.post("/save-diary")
async def save_diary(request: DiaryEntryRequest) -> Dict[str, Any]:
    """
    Save a diary entry using Abacus.ai's diary agent.
    """
    result = await abacus_service.save_diary_entry(
        entry_text=request.entry_text,
        user_id=request.user_id,
        context=request.context
    )
    
    if not result.get("success", False):
        raise HTTPException(status_code=500, detail=result.get("error", "Unknown error occurred"))
    
    return result

@router.post("/chat-abacus")
async def chat_abacus(request: ChatRequest) -> Dict[str, Any]:
    """
    Chat with Abacus.ai models or agents.
    """
    # If model_id is not provided, attempt to use the model picker agent
    if not request.model_id and abacus_service.agent_deployments.get("model_picker"):
        try:
            model_id = await abacus_service.pick_model(
                prompt=request.prompt,
                conversation_history=request.conversation_history
            )
        except Exception as e:
            # If model picking fails, fall back to the generic LLM agent
            model_id = abacus_service.agent_deployments.get("generic_llm", "")
    else:
        model_id = request.model_id
    
    result = await abacus_service.chat(
        prompt=request.prompt,
        model_id=model_id,
        conversation_history=request.conversation_history
    )
    
    if not result.get("success", False):
        raise HTTPException(status_code=500, detail=result.get("error", "Unknown error occurred"))
    
    return result
