"""Rabbit MQ tools"""

import aio_pika

from .config import settings
from .log import logger


async def rabbit_connection():
    """Init Rabbit MQ connection"""

    logger.info("Connecting to RabbitMQ ...")
    connection = await aio_pika.connect_robust(
        host=settings.RABBIT_MQ_HOST,
        port=settings.RABBIT_MQ_PORT,
        login=settings.RABBIT_MQ_USER,
        password=settings.RABBIT_MQ_PASSWORD,
    )

    return connection
