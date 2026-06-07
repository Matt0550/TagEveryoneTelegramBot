import os
import sys

# Add the src directory to the sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import sentry_sdk
import uvicorn
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.routing import APIRoute
from sentry_sdk.integrations.asyncio import AsyncioIntegration
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.starlette import StarletteIntegration
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.middleware.cors import CORSMiddleware

from api.v1.routes.public import router as public_router
from models import CustomResponse
from utils.config import settings
from utils.logger_base import logger

if settings.SENTRY_DSN:
    logger.info("Sentry is enabled. Initializing Sentry SDK...")
    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        send_default_pii=True,
        auto_enabling_integrations=True,
        integrations=[
            FastApiIntegration(),
            StarletteIntegration(),
            AsyncioIntegration(),
        ],
    )


def custom_generate_unique_id(route: APIRoute) -> str:
    if route.tags:
        return f"{route.tags[0]}-{route.name}"
    return route.name


app = FastAPI(
    title="Tag Everyone Telegram Bot",
    default_response_class=CustomResponse,
    version=settings.API_VERSION,
    generate_unique_id_function=custom_generate_unique_id,
)

cors_origins = (
    settings.API_BACKEND_CORS_ORIGINS
    if settings.API_BACKEND_CORS_ORIGINS
    else [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5500",
    ]
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# * Error handlers
@app.exception_handler(Exception)
async def generic_exception_handler(_request: Request, exc: Exception):
    logger.error(f"Internal server error: {exc}")
    return CustomResponse(
        "Internal server error. Please try again later.",
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(_request: Request, exc: StarletteHTTPException):
    logger.error(f"HTTP error: {exc.detail}")
    return CustomResponse(exc.detail, status_code=exc.status_code)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(_request: Request, exc: RequestValidationError):
    logger.error(f"Validation error: {exc.errors()}")
    errors = exc.errors()
    message = "Validation error"
    if len(errors) > 0:
        message = errors[0].get("msg", "Validation error")
    return CustomResponse(message, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)


app.include_router(
    public_router, prefix=f"/api/{settings.API_VERSION}/public", tags=["Public API"]
)

# if settings.ENABLE_ADMIN_API:
#     app.include_router(
#         admin_router,
#         prefix=f"/api/{settings.API_VERSION}/admin",
#         tags=["Administration API"],
#     )


@app.get("/api/status", tags=["System"])
def system_status():
    return {"status": 200, "message": "OK"}


if __name__ == "__main__":
    print(f"Tag Everyone Telegram Bot REST API {settings.API_VERSION}")
    print("© 2026 Matteo Sillitti. All rights reserved.")
    print("Running on port: ", settings.API_PORT)
    print("Environment: ", settings.ENVIRONMENT)

    ssl_keyfile = (
        "certs/key.pem"
        if settings.API_USE_SSL and settings.ENVIRONMENT == "local"
        else None
    )
    ssl_certfile = (
        "certs/cert.pem"
        if settings.API_USE_SSL and settings.ENVIRONMENT == "local"
        else None
    )

    if ssl_keyfile and ssl_certfile:
        import os

        if not os.path.exists(ssl_keyfile) or not os.path.exists(ssl_certfile):
            logger.warning(
                f"SSL enabled but certificates not found at {ssl_keyfile} or {ssl_certfile}. Disabling SSL."
            )
            ssl_keyfile = None
            ssl_certfile = None

    uvicorn.run(
        "api.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        workers=settings.API_WORKERS,
        reload=settings.ENVIRONMENT == "local" and settings.API_SERVER_RELOAD,
        forwarded_allow_ips="*" if settings.API_IS_BEHIND_PROXY else None,
        log_level="info",
        ssl_keyfile=ssl_keyfile,
        ssl_certfile=ssl_certfile,
        http="h11" if settings.ENVIRONMENT == "local" else "auto",
        timeout_graceful_shutdown=1 if settings.ENVIRONMENT == "local" else None,
    )
