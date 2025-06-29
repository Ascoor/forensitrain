from fastapi import FastAPI
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from slowapi.errors import RateLimitExceeded

from .routes.phone import router as phone_router, limiter, rate_limit_handler
from .routes.image import router as image_router
from .routes.social import router as social_router

load_dotenv()

app = FastAPI(title="ForensiTrain API")

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, rate_limit_handler)

# Allow frontend development origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:7000", "http://localhost:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", include_in_schema=False)
def index() -> HTMLResponse:
    """Simple landing page explaining how to access the frontend."""
    html = (
        "<html><body>"
        "<h1>ForensiTrain API</h1>"
        "<p>The React frontend runs separately on port 7000. "
        "Start it with <code>npm run dev</code> and open "
        "<a href='http://localhost:7000'>http://localhost:7000</a>." 
        "</p>"
        "</body></html>"
    )
    return HTMLResponse(content=html)

@app.get("/api/health")
def health_check():
    return {"status": "ok"}

# Include phone analysis routes
app.include_router(phone_router, prefix="/api/phone")
app.include_router(image_router, prefix="/api")
app.include_router(social_router, prefix="/api/social")
