import logging

from .celery.celery import app

from .models.target_balance import create_daily_percent


@app.task()
def accrual_interest():
    logging.info(f'percent was accrued for {create_daily_percent()} targets')
