from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from slowapi.errors import RateLimitExceeded
import importlib

from .core.logging_config import configure_logging


from .routers.phone import router as phone_router, limiter, rate_limit_handler
from .routers.image import router as image_router
from .routers.social import router as social_router
from .routers.integration import router as integration_router
from .routers.workflow import router as workflow_router
from .routers.geosocial import router as geosocial_router
from .routers.osint import router as osint_router


load_dotenv()
configure_logging()

app = FastAPI(title="ForensiTrain API")


def _check_dependencies():
    """Attempt to import heavy optional packages."""
    modules = ["cvlib", "face_recognition", "tensorflow", "dlib"]
    status = {}
    for name in modules:
        try:
            importlib.import_module(name)
            status[name] = "available"
        except Exception as exc:  # noqa: BLE001
            status[name] = f"error: {exc}"
    try:  # GPU check
        import tensorflow as tf

        gpu = tf.config.list_physical_devices("GPU")
        if not gpu:
            gpu = tf.config.list_physical_devices("XLA_GPU")
        if not gpu:
            gpu = tf.config.list_physical_devices("TPU")
        if not gpu:
            gpu = tf.config.list_physical_devices("XLA_TPU")
        if not gpu:
            gpu = tf.config.list_physical_devices("CPU")
        status["tensorflow_gpu"] = bool(gpu)
    except Exception:  # noqa: BLE001
        pass
    return status


app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, rate_limit_handler)


@app.on_event("startup")
async def startup_event() -> None:
    """Check heavy dependencies once at startup."""
    app.state.dependencies = _check_dependencies()


# Allow frontend development origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:7000"],  # لا تستخدم "*" مع allow_credentials=True
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
    """Return app status and availability of heavy dependencies."""
    deps = getattr(app.state, "dependencies", {})
    return {"status": "ok", "dependencies": deps}


# Include phone analysis routes
app.include_router(phone_router, prefix="/api/phone")
app.include_router(image_router, prefix="/api")
app.include_router(social_router, prefix="/api/social")
app.include_router(integration_router, prefix="/api")
app.include_router(workflow_router, prefix="/api/workflow")
app.include_router(geosocial_router, prefix="/api/geosocial")
app.include_router(osint_router, prefix="/api/osint")
