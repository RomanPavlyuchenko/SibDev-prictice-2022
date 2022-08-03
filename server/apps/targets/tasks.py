import logging

from .celery.celery import app

from .models.target_balance import create_daily_percent


@app.task()
def accrual_interest():
    percents_count = create_daily_percent()
    logging.info(f'percent was accrued for {percents_count} targets')
