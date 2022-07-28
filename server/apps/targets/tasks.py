import logging

from .celery.celery import app

from .viewsets.target import percent_accrual


@app.task()
def accrual_interest():
    logging.info(f'percent was accrued for {len(percent_accrual())} targets')
