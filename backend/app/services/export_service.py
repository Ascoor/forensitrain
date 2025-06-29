import io
from typing import Tuple
from fastapi.responses import StreamingResponse, JSONResponse
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

from .phone_service import a_enrich_phone_data


async def generate_export(phone_number: str, fmt: str = "json"):
    """Return StreamingResponse with report in given format."""
    data = await a_enrich_phone_data(phone_number)
    if fmt == "pdf":
        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=letter)
        y = 750
        for key, value in data.get("data", {}).items():
            c.drawString(30, y, f"{key}: {value}")
            y -= 15
        c.save()
        buffer.seek(0)
        return StreamingResponse(buffer, media_type="application/pdf")
    return JSONResponse(content=data)
