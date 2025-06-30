from datetime import datetime
import asyncio
import json
from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from ..models.phone import PhoneRequest
from ..services.enrichment_workflow import run_enrichment

router = APIRouter()


@router.post('/enrich-workflow')
async def enrich_workflow(payload: PhoneRequest):
    """Run the sequential enrichment workflow and return final data."""
    result = await run_enrichment(payload.phone_number)
    return {
        "status": result.get("status"),
        "data": result.get("data"),
        "errors": result.get("errors"),
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }


@router.post('/enrich-stream')
async def enrich_stream(payload: PhoneRequest):
    """Stream progress events during enrichment as newline delimited JSON."""

    async def event_gen():
        queue: asyncio.Queue = asyncio.Queue()

        def _cb(stage: str, data: object) -> None:
            queue.put_nowait({"stage": stage, "data": data})

        task = asyncio.create_task(run_enrichment(payload.phone_number, _cb))
        while True:
            item = await queue.get()
            yield json.dumps(item) + "\n"
            if item.get("stage") == "complete":
                await task
                break

    return StreamingResponse(event_gen(), media_type="application/json")
