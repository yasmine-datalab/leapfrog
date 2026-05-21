""" IDP utilities
"""

from typing import List
import requests
from fastapi import HTTPException, status
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
from pydantic_core import PydanticCustomError, InitErrorDetails
from fastapi_keycloak import FastAPIKeycloak, KeycloakUser, OIDCUser
from fastapi_keycloak.exceptions import UserNotFound, KeycloakError

from utils import token_fetcher, token_saver
from .config import settings
from .log import logger


def init_keycloak():
    """Init Keycloak instance for FastAPI"""
    logger.info("Initializing Keycloak connection for client: %s", settings.KEYCLOAK_CLIENT_ID)
    print("KEYCLOAK_SERVER =", settings.KEYCLOAK_SERVER)
    print("KEYCLOAK_REALM =", settings.KEYCLOAK_REALM)
    return FastAPIKeycloak(
        server_url=settings.KEYCLOAK_SERVER,
        client_id=settings.KEYCLOAK_CLIENT_ID,
        client_secret=settings.KEYCLOAK_CLIENT_SECRET,
        admin_client_id=settings.KEYCLOAK_ADMIN_CLIENT_ID,
        admin_client_secret=settings.KEYCLOAK_ADMIN_CLIENT_SECRET,
        realm=settings.KEYCLOAK_REALM,
        callback_uri=settings.KEYCLOAK_CALLBACK_URI,
        ssl_verification= False
    )


idp = init_keycloak()


def get_keycloak_user(
    current_user: OIDCUser,
    required_roles: List[str] = None,
    fetch_user: bool = False,
) -> KeycloakUser:
    """Retrieves a KeycloakUser from the current_user."""

    if required_roles:
        msg = f"One of these roles ({', '.join(required_roles)}) is required to perform this action"
        if not any(role in current_user.roles for role in required_roles):

            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=msg,
            )

    if fetch_user:
        try:

            return idp.get_user(query=f"username={current_user.email}")

        except (UserNotFound, KeycloakError) as error:

            raise HTTPException(
                status_code=error.status_code,
                detail=f"Error retrieving Keycloak user: {error.reason}",
            ) from error

    return None


async def verify_user_id(user_id: str | None):
    """Verify user id in keycloack or raise error 422"""

    if user_id is None:
        raise RequestValidationError(
            errors=ValidationError.from_exception_data(
                line_errors=[
                    InitErrorDetails(
                        type=PydanticCustomError(
                            "missing",
                            "User id is required.",
                        ),
                        loc=["user_id"],
                    )
                ],
                title="Validation Error",
            ).errors()
        )

    try:
        _ = idp.get_user(user_id=user_id)
    except (UserNotFound, KeycloakError) as e:
        raise RequestValidationError(
            errors=ValidationError.from_exception_data(
                line_errors=[
                    InitErrorDetails(
                        type=PydanticCustomError(
                            "missing",
                            "User id is invalid or not found.",
                        ),
                        loc=["user_id"],
                    )
                ],
                title="Validation Error",
            ).errors()
        ) from e

    return True


def get_token():
    """get Token"""
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    response = None
    url = f"http://{settings.KEYCLOAK_SERVER}/realms/{settings.KEYCLOAK_REALM}/protocol/openid-connect/token"
    try:
        data = {
            "client_id": settings.KEYCLOAK_CLIENT_ID,
            "client_secret": settings.KEYCLOAK_CLIENT_SECRET,
            "grant_type": "client_credentials",
        }
        response = requests.post(
            url=url, headers=headers, data=data, timeout=10
        )
        response.raise_for_status()  # Lève une exception pour les codes d'état HTTP 4xx/5xx
        token_data = response.json()

        return token_data["access_token"]
    except Exception as e:
        status_code = response.status_code if response is not None else "N/A"
        error_body = response.text if response is not None else str(e)
        logger.error(
            "Keycloak Token Request Failed: Client ID='%s', Status=%s, Response=%s",
            settings.KEYCLOAK_CLIENT_ID, status_code, error_body
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication with identity provider failed",
        ) from e


def get_session():
    """Get Session"""
    # fetching token
    token = token_fetcher()
    if token is None or not idp.token_is_valid(token=token):
        token = get_token()
        token_saver(token=token)
    session = requests.Session()
    # Configuration de la session si nécessaire (headers, etc.)
    session.headers.setdefault("Authorization", f"Bearer {token}")
    session.headers.setdefault("Content-Type", "application/json")
    return session
