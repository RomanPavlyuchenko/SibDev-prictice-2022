import os

from celery import Celery
from celery.schedules import crontab

from . import celery_config

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('apps.targets')
app.config_from_object(celery_config)

app.conf.beat_schedule = {
    'first_task_anything': {
        'task': 'apps.targets.tasks.accrual_interest',
        'schedule': crontab(hour=0, minute=0),
    }
}
app.autodiscover_tasks(['apps.targets'])
