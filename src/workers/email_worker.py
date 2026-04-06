"""
Background email worker — processes a Redis-backed email queue.
Run with: python -m src.workers.email_worker
"""
import asyncio
import json
import logging

logger = logging.getLogger(__name__)

EMAIL_QUEUE_KEY = "email:queue"
MAX_RETRIES = 3

async def process_email_job(redis, job: dict) -> bool:
    """Process a single email job dict. Returns True on success."""
    from src.services.email import EmailService
    svc = EmailService()
    job_type = job.get("type")
    to = job.get("to")
    try:
        if job_type == "welcome":
            await svc.send_welcome(to=to, username=job["username"])
        elif job_type == "reset":
            await svc.send_password_reset(to=to, reset_token=job["token"])
        elif job_type == "notification":
            await svc.send_notification(to=to, title=job["title"], body_text=job["body"])
        else:
            logger.warning("Unknown email job type: %s", job_type)
            return False
        logger.info("Email job processed: type=%s to=%s", job_type, to)
        return True
    except Exception as exc:
        logger.error("Email job failed: %s — %s", job, exc)
        return False

async def run_worker(redis) -> None:
    """Continuously pop and process jobs from the email queue."""
    logger.info("Email worker started")
    while True:
        try:
            raw = await redis.blpop(EMAIL_QUEUE_KEY, timeout=5)
            if raw is None:
                continue
            _, data = raw
            job = json.loads(data)
            retry = job.get("_retry", 0)
            success = await process_email_job(redis, job)
            if not success and retry < MAX_RETRIES:
                job["_retry"] = retry + 1
                await redis.rpush(EMAIL_QUEUE_KEY, json.dumps(job))
                logger.info("Re-queued email job (attempt %d)", job["_retry"])
        except asyncio.CancelledError:
            break
        except Exception as exc:
            logger.exception("Worker loop error: %s", exc)
            await asyncio.sleep(1)
    logger.info("Email worker stopped")

if __name__ == "__main__":
    import aioredis
    from src.core.config import settings
    logging.basicConfig(level=logging.INFO)
    async def _main():
        redis = await aioredis.from_url(settings.REDIS_URL, decode_responses=True)
        await run_worker(redis)
    asyncio.run(_main())