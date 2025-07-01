from datetime import datetime
from fastapi import APIRouter

from ..models.geosocial import FootprintRequest, FootprintResponse, FootprintResult
from ..services.geosocial_service import extract_footprint

router = APIRouter()


@router.post('/footprint', response_model=FootprintResponse)
async def geosocial_footprint(payload: FootprintRequest):
    try:
        data = await extract_footprint(payload.username)
        result = FootprintResult(
            count=len(data.get('tweets', [])),
            locations=[
                {
                    'lat': t.get('latitude'),
                    'lon': t.get('longitude'),
                    'text': t.get('text'),
                    'created_at': t.get('created_at'),
                }
                for t in data.get('tweets', [])
            ],
        )
        return {
            'status': 'success',
            'data': result,
            'errors': None,
            'timestamp': datetime.utcnow().isoformat() + 'Z',
        }
    except Exception as exc:  # noqa: BLE001
        return {
            'status': 'error',
            'data': None,
            'errors': str(exc),
            'timestamp': datetime.utcnow().isoformat() + 'Z',
        }
