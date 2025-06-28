from fastapi import FastAPI
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from slowapi.errors import RateLimitExceeded

from .routes.phone import router as phone_router, limiter, rate_limit_handler

load_dotenv()

app = FastAPI(title="ForensiTrain API")

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, rate_limit_handler)

# Allow frontend development origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", include_in_schema=False)
def index() -> RedirectResponse:
    """Redirect to the React development server."""
    return RedirectResponse(url="http://localhost:5173", status_code=307)

@app.get("/api/health")
def health_check():
    return {"status": "ok"}

# Include phone analysis routes
app.include_router(phone_router, prefix="/api/phone")
