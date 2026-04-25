""" Database connection module
"""

from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie

from models import (
    Module,
    Lesson,
    Instructor,
    Course,
    Student,
    CourseProgress,
    Review,
    Certificate,
)

from core import settings


# pylint: disable=line-too-long
client = AsyncIOMotorClient(
    f"mongodb://{settings.MONGO_USER}:{settings.MONGO_PASSWORD}@{settings.MONGO_HOST}:{settings.MONGO_PORT}",
    uuidRepresentation="standard",
)


async def init_database():
    """Init database connection"""

    await init_beanie(
        database=client[settings.MONGO_DB],
        document_models=[
           
        ],
    )


async def close_database():
    """Close the database connection."""

    client.close()
