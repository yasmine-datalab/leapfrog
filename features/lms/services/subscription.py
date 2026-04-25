"""Subscription Service"""

from pydantic import UUID4
from schemas.subscription import Subscription

from core import settings, logger, get_session


async def get_user_subscription(
    user_id: UUID4,
) -> Subscription | None:
    """Get User subscription"""
    session = get_session()
    try:

        response = session.get(
            f"{settings.SUBSCRIPTION_BASE_URL}/subscriptions/user/me",
            params={"user_id": user_id},
        )

        if response.ok:
            return Subscription(**response.json())

        return None
    # pylint: disable=W0718
    except Exception as error:
        logger.error("Unexpected error: %s", error)

    return None
