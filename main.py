"""Micro Service entry point module"""

from contextlib import asynccontextmanager
from jose import ExpiredSignatureError, JWTError
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi_keycloak import KeycloakError
import uvicorn

from api import router_v1

from core import settings, idp, init_database, close_database, configure_logging

configure_logging()


@asynccontextmanager
async def lifespan(_: FastAPI):
    """Lifespan to initialize database and RabbitMQ consumers."""

    try:
        await init_database()

        yield

    finally:

        await close_database()


app = FastAPI(lifespan=lifespan, title=settings.API_TITLE)

# Init IDP Connection
idp.add_swagger_config(app)

# Exceptions management


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(_: Request, exc: RequestValidationError):
    """Validation  exception handler"""

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        # Unprocessable Entity
        content={"detail": exc.errors()},
    )


@app.exception_handler(ValueError)
async def value_error_exception_handler(_: Request, exc: ValueError):
    """Value error exception handler"""
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"message": str(exc)},
    )


@app.exception_handler(JWTError)
async def jwt_error_exception_handler(_: Request, exc: JWTError):
    """JWT Error exception handler"""
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={"detail": str(exc)},
    )


@app.exception_handler(KeycloakError)
async def keycloak_error_exception_handler(_: Request, exc: KeycloakError):
    """Keycloak error exception handler"""

    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.reason},
    )


@app.exception_handler(ExpiredSignatureError)
async def expired_token_error_exception_handler(_: Request, exc: ExpiredSignatureError):
    """Expired token exception handler"""
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={"detail": str(exc)},
    )


@app.exception_handler(Exception)
async def default_error_exception_handler(_: Request, exc: Exception):
    """default exception handler"""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": str(exc)},
    )


# Register router
app.include_router(router_v1.router, prefix="/api/v1")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["Home"])
def read_root():
    """Root Endpoint"""

    return settings.API_TITLE + " " + settings.API_VERSION + " is running!"


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=True,
    )