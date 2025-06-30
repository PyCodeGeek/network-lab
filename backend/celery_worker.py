"""
Celery worker entry point
"""

import os
import sys

# Add the backend directory to Python path
sys.path.insert(0, '/app')

from app.celery_app import celery

if __name__ == '__main__':
    celery.start()