# app/celery_app.py
from app import create_app
from extensions import celery

app = create_app()
celery.conf.update(app.config)
