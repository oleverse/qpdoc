from app.services.llm import openai_service
from fastapi import APIRouter

router = APIRouter(prefix='/llm', tags=['llm'])


@router.post("/llm")
async def llm_endpoint(query: str):
    answer = openai_service.run_llm(query)
    return {"answer": answer}
