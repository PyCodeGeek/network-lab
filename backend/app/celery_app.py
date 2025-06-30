# backend/app/celery_app.py - Celery configuration
# ================================================

from celery import Celery
import os

# def make_celery(app):
#     """Create Celery instance with Flask app context."""
#     celery = Celery(
#         app.import_name,
#         backend=app.config['CELERY_RESULT_BACKEND'],
#         broker=app.config['CELERY_BROKER_URL']
#     )
    
#     # Update configuration
#     celery.conf.update(
#         task_serializer='json',
#         accept_content=['json'],
#         result_serializer='json',
#         timezone='UTC',
#         enable_utc=True,
#         result_expires=3600,
#         task_routes={
#             'app.tasks.telemetry.*': {'queue': 'telemetry'},
#             'app.tasks.provisioning.*': {'queue': 'provisioning'},
#             'app.tasks.reports.*': {'queue': 'reports'},
#         },
#         beat_schedule={
#             'collect-telemetry': {
#                 'task': 'app.tasks.telemetry.collect_all_telemetry',
#                 'schedule': 300.0,  # Every 5 minutes
#             },
#             'cleanup-old-data': {
#                 'task': 'app.tasks.maintenance.cleanup_old_telemetry',
#                 'schedule': 86400.0,  # Daily
#             },
#         }
#     )
    
#     class ContextTask(celery.Task):
#         """Make celery tasks work with Flask app context."""
#         def __call__(self, *args, **kwargs):
#             with app.app_context():
#                 return self.run(*args, **kwargs)
    
#     celery.Task = ContextTask
#     return celery

def make_celery():
    """Create Celery instance"""
    
    # Get configuration from environment
    broker_url = os.environ.get('CELERY_BROKER_URL', 'redis://redis:6379/0')
    result_backend = os.environ.get('CELERY_RESULT_BACKEND', 'redis://redis:6379/0')
    
    # Create Celery instance
    celery_app = Celery(
        'network_lab',
        broker=broker_url,
        backend=result_backend,
        include=['app.tasks']  # Include task modules
    )
    
    # Configuration
    celery_app.conf.update(
        task_serializer='json',
        accept_content=['json'],
        result_serializer='json',
        timezone='UTC',
        enable_utc=True,
        result_expires=3600,
        task_routes={
            'app.tasks.*': {'queue': 'default'},
        },
        beat_schedule={
            'test-task': {
                'task': 'app.tasks.test_task',
                'schedule': 300.0,  # Every 5 minutes
            },
        }
    )
    
    return celery_app

# Create the Celery instance
celery = make_celery()

if __name__ == '__main__':
    celery.start()