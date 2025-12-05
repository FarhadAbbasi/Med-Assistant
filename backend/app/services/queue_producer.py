import asyncio
import aio_pika
from app.core.config import get_settings

async def publish_analyze_job(payload: dict):
    s = get_settings()
    connection = await aio_pika.connect_robust(
        host=s.rabbitmq_host,
        port=s.rabbitmq_port,
        login=s.rabbitmq_user,
        password=s.rabbitmq_pass,
    )
    async with connection:
        channel = await connection.channel()
        exchange = await channel.declare_exchange(s.rabbitmq_exchange, aio_pika.ExchangeType.TOPIC, durable=True)
        queue = await channel.declare_queue(s.rabbitmq_queue_analyze, durable=True)
        await queue.bind(exchange, routing_key=s.rabbitmq_queue_analyze)
        await exchange.publish(
            aio_pika.Message(body=str(payload).encode("utf-8")),
            routing_key=s.rabbitmq_queue_analyze,
        )
