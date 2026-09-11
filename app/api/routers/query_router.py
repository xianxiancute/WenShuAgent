import asyncio
from fastapi import APIRouter
from fastapi.params import Depends
from typing import Annotated
from starlette.responses import StreamingResponse

from app.api.dependencies import get_query_service
from app.api.schemas.query_schema import QuerySchema
from app.services.query_service import QueryService

query_router = APIRouter()

# async def fake_streamer():
#     for i in range(10):
#         await asyncio.sleep(0.5)
#         yield f"data: step: {i}\n\n"
#
# async def get_query_service():
#     return QueryService()

@query_router.post("/api/query")
async def query_handler(query: QuerySchema, query_service: Annotated[QueryService, Depends(get_query_service)]):
    return StreamingResponse(query_service.query(query.query), media_type="text/event-stream")