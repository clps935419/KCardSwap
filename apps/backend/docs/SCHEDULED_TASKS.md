# Scheduled Tasks Configuration Guide

This guide explains how to configure scheduled tasks for subscription management in production.

## Overview

The subscription system requires a daily task to expire subscriptions that have passed their expiry date. In POC, this is handled by a manual endpoint, but production environments should use a proper scheduler.

## POC Implementation

**Manual Endpoint**: `POST /api/v1/subscriptions/expire-subscriptions`

For testing and POC purposes, you can manually trigger the expiry job:

```bash
curl -X POST http://localhost:8080/api/v1/subscriptions/expire-subscriptions
```

This endpoint is also suitable for triggering from external schedulers like Cloud Scheduler or cron jobs.

## Production Implementations

### Option 1: APScheduler (In-Process)

**Pros**: Simple, no external dependencies, runs within the FastAPI process
**Cons**: Doesn't scale well with multiple instances (use with load balancer sticky sessions or single instance)

**Installation**:
```bash
poetry add apscheduler
```

**Implementation** (`apps/backend/app/scheduled/subscription_jobs.py`):

```python
"""Scheduled jobs for subscription management"""
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
import logging

from app.shared.infrastructure.database.connection import get_db_session
from app.modules.identity.infrastructure.repositories.subscription_repository_impl import SubscriptionRepositoryImpl
from app.modules.identity.application.use_cases.subscription.expire_subscriptions_use_case import ExpireSubscriptionsUseCase

logger = logging.getLogger(__name__)

async def expire_subscriptions_job():
    """Daily job to expire subscriptions"""
    logger.info("Running expire subscriptions job")
    
    async for session in get_db_session():
        try:
            subscription_repo = SubscriptionRepositoryImpl(session)
            use_case = ExpireSubscriptionsUseCase(subscription_repo)
            result = await use_case.execute()
            await session.commit()
            
            logger.info(f"Expired {result['expired_count']} subscriptions")
        except Exception as e:
            logger.error(f"Error in expire subscriptions job: {e}")
            await session.rollback()
        finally:
            await session.close()

def start_scheduler():
    """Start the APScheduler"""
    scheduler = AsyncIOScheduler()
    
    # Run daily at 2 AM
    scheduler.add_job(
        expire_subscriptions_job,
        CronTrigger(hour=2, minute=0),
        id='expire_subscriptions',
        name='Expire Subscriptions Daily',
        replace_existing=True
    )
    
    scheduler.start()
    logger.info("Scheduler started")
    return scheduler
```

**Integration with FastAPI** (`apps/backend/app/main.py`):

```python
from contextlib import asynccontextmanager

# Import scheduler
from app.scheduled.subscription_jobs import start_scheduler

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for FastAPI"""
    
    # Start scheduler on startup
    scheduler = start_scheduler()
    
    yield
    
    # Shutdown scheduler
    scheduler.shutdown()
    container.unwire()
    container.shared().db_connection_provider().close()
```

### Option 2: Celery Beat (Distributed)

**Pros**: Scales well, distributed task execution, better for multiple instances
**Cons**: Requires Redis/RabbitMQ message broker

**Installation**:
```bash
poetry add celery redis
```

**Celery Configuration** (`apps/backend/app/celery_app.py`):

```python
"""Celery application for background tasks"""
from celery import Celery
from celery.schedules import crontab

from app.config import settings

# Create Celery app
celery_app = Celery(
    'kcardswap',
    broker=settings.CELERY_BROKER_URL,  # e.g., 'redis://localhost:6379/0'
    backend=settings.CELERY_RESULT_BACKEND
)

# Configure Celery Beat schedule
celery_app.conf.beat_schedule = {
    'expire-subscriptions-daily': {
        'task': 'app.tasks.subscription_tasks.expire_subscriptions',
        'schedule': crontab(hour=2, minute=0),  # 2 AM daily
    },
}

celery_app.conf.timezone = 'UTC'
```

**Task Definition** (`apps/backend/app/tasks/subscription_tasks.py`):

```python
"""Celery tasks for subscription management"""
from app.celery_app import celery_app
from app.shared.infrastructure.database.connection import get_db_session
from app.modules.identity.infrastructure.repositories.subscription_repository_impl import SubscriptionRepositoryImpl
from app.modules.identity.application.use_cases.subscription.expire_subscriptions_use_case import ExpireSubscriptionsUseCase
import logging

logger = logging.getLogger(__name__)

@celery_app.task(name='app.tasks.subscription_tasks.expire_subscriptions')
def expire_subscriptions():
    """Celery task to expire subscriptions"""
    logger.info("Running expire subscriptions task")
    
    # Note: Celery tasks are sync, so we need to use sync database operations
    # or run async code with asyncio.run()
    
    import asyncio
    
    async def _expire():
        async for session in get_db_session():
            try:
                subscription_repo = SubscriptionRepositoryImpl(session)
                use_case = ExpireSubscriptionsUseCase(subscription_repo)
                result = await use_case.execute()
                await session.commit()
                
                logger.info(f"Expired {result['expired_count']} subscriptions")
                return result
            except Exception as e:
                logger.error(f"Error in expire subscriptions task: {e}")
                await session.rollback()
                raise
            finally:
                await session.close()
    
    return asyncio.run(_expire())
```

**Running Celery Worker and Beat**:

```bash
# Terminal 1: Start Celery worker
celery -A app.celery_app worker --loglevel=info

# Terminal 2: Start Celery beat scheduler
celery -A app.celery_app beat --loglevel=info
```

### Option 3: Cloud Scheduler (Serverless)

**Pros**: No infrastructure to manage, scales automatically, works with any cloud provider
**Cons**: Requires exposing endpoint or using cloud functions

#### Google Cloud Scheduler

```bash
# Create a Cloud Scheduler job
gcloud scheduler jobs create http expire-subscriptions \
    --schedule="0 2 * * *" \
    --uri="https://your-app.com/api/v1/subscriptions/expire-subscriptions" \
    --http-method=POST \
    --oidc-service-account-email="scheduler@your-project.iam.gserviceaccount.com" \
    --oidc-token-audience="https://your-app.com"
```

#### AWS EventBridge

```yaml
# CloudFormation/SAM template
SubscriptionExpiryRule:
  Type: AWS::Events::Rule
  Properties:
    Description: "Trigger subscription expiry daily"
    ScheduleExpression: "cron(0 2 * * ? *)"  # 2 AM UTC daily
    State: ENABLED
    Targets:
      - Arn: !GetAtt ExpireSubscriptionsFunction.Arn
        Id: ExpireSubscriptionsTarget
```

### Option 4: Kubernetes CronJob

**Pros**: Cloud-native, scales with cluster, integrates with existing K8s infrastructure
**Cons**: Requires Kubernetes

```yaml
# k8s/cronjobs/expire-subscriptions.yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: expire-subscriptions
spec:
  schedule: "0 2 * * *"  # 2 AM daily
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: expire-subscriptions
            image: your-backend-image:latest
            command:
            - python
            - -c
            - |
              import asyncio
              from app.shared.infrastructure.database.connection import get_db_session
              from app.modules.identity.infrastructure.repositories.subscription_repository_impl import SubscriptionRepositoryImpl
              from app.modules.identity.application.use_cases.subscription.expire_subscriptions_use_case import ExpireSubscriptionsUseCase
              
              async def main():
                  async for session in get_db_session():
                      try:
                          repo = SubscriptionRepositoryImpl(session)
                          use_case = ExpireSubscriptionsUseCase(repo)
                          result = await use_case.execute()
                          await session.commit()
                          print(f"Expired {result['expired_count']} subscriptions")
                      finally:
                          await session.close()
              
              asyncio.run(main())
            env:
            - name: DATABASE_URL
              valueFrom:
                secretKeyRef:
                  name: backend-secrets
                  key: database-url
          restartPolicy: OnFailure
```

## Monitoring and Alerting

Regardless of which scheduler you choose, implement monitoring:

### Logging

```python
logger.info(f"Subscription expiry job completed: {result['expired_count']} expired")
logger.error(f"Subscription expiry job failed: {error}")
```

### Metrics (Prometheus)

```python
from prometheus_client import Counter, Histogram

subscription_expiry_counter = Counter(
    'subscription_expiry_total',
    'Total subscriptions expired'
)

subscription_expiry_duration = Histogram(
    'subscription_expiry_duration_seconds',
    'Time taken to expire subscriptions'
)

# In the job
with subscription_expiry_duration.time():
    result = await use_case.execute()
    subscription_expiry_counter.inc(result['expired_count'])
```

### Alerting

Configure alerts for:
- Job failures
- No subscriptions expired in X days (might indicate a problem)
- Excessive expiries (might indicate a configuration issue)

## Environment Variables

Add to `apps/backend/.env`:

```bash
# APScheduler
SCHEDULER_ENABLED=true
SCHEDULER_TIMEZONE=UTC

# Celery
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/1

# Cloud Scheduler (if protecting endpoint)
SCHEDULER_API_KEY=your-secret-key-here
```

## Security Considerations

1. **Endpoint Protection**: If using cloud schedulers, protect the endpoint:
   - API key authentication
   - IP whitelist
   - OIDC/OAuth tokens

2. **Idempotency**: The endpoint is already idempotent, safe to retry

3. **Timeout**: Set appropriate timeouts for large subscription bases

## Testing

Test the scheduled task manually:

```bash
# Test the endpoint
curl -X POST http://localhost:8080/api/v1/subscriptions/expire-subscriptions

# Test with specific date (add parameter to use case for testing)
# Or manipulate subscription expiry dates in test database
```

## Recommendation

For most deployments:
- **Development/POC**: Manual endpoint or simple cron job
- **Small Production**: APScheduler (single instance)
- **Medium Production**: Celery Beat (if already using Celery)
- **Large/Cloud Production**: Cloud Scheduler or Kubernetes CronJob
- **Enterprise**: Kubernetes CronJob with monitoring and alerting

Choose based on your existing infrastructure and scale requirements.
