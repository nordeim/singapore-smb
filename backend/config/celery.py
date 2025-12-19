"""
Celery configuration for Singapore SMB E-commerce Platform.

This module configures the Celery application for asynchronous task processing.
"""
import os
from celery import Celery
from celery.schedules import crontab

# Set the default Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')

# Create Celery app
app = Celery('singapore_smb')

# Configure Celery using Django settings
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover tasks from installed apps
app.autodiscover_tasks()

# =============================================================================
# TASK QUEUES
# =============================================================================

app.conf.task_queues = {
    'default': {
        'exchange': 'default',
        'routing_key': 'default',
    },
    'commerce': {
        'exchange': 'commerce',
        'routing_key': 'commerce',
    },
    'inventory': {
        'exchange': 'inventory',
        'routing_key': 'inventory',
    },
    'accounting': {
        'exchange': 'accounting',
        'routing_key': 'accounting',
    },
    'payments': {
        'exchange': 'payments',
        'routing_key': 'payments',
    },
    'notifications': {
        'exchange': 'notifications',
        'routing_key': 'notifications',
    },
}

# =============================================================================
# BEAT SCHEDULE (Periodic Tasks)
# =============================================================================

app.conf.beat_schedule = {}

if os.environ.get('ENABLE_CELERY_BEAT', '') == '1':
    app.conf.beat_schedule = {
        # Inventory tasks
        'check-low-stock-every-15-mins': {
            'task': 'apps.inventory.tasks.check_low_stock',
            'schedule': crontab(minute='*/15'),
        },
        'cleanup-expired-reservations': {
            'task': 'apps.inventory.tasks.cleanup_expired_reservations',
            'schedule': crontab(minute='*/5'),
        },
        
        # Commerce tasks
        'cleanup-abandoned-carts-daily': {
            'task': 'apps.commerce.tasks.cleanup_abandoned_carts',
            'schedule': crontab(hour=2, minute=0),  # 2 AM daily
        },
        
        # Accounting tasks
        'generate-daily-reports': {
            'task': 'apps.accounting.tasks.generate_daily_reports',
            'schedule': crontab(hour=0, minute=30),  # 12:30 AM daily
        },
        'gst-filing-reminder': {
            'task': 'apps.accounting.tasks.gst_filing_reminder',
            'schedule': crontab(day_of_month=1, hour=9, minute=0),  # 1st of month, 9 AM
        },
        
        # Compliance tasks
        'pdpa-data-retention-cleanup': {
            'task': 'apps.compliance.tasks.pdpa_data_retention_cleanup',
            'schedule': crontab(hour=3, minute=0),  # 3 AM daily
        },
    }

# =============================================================================
# TASK ANNOTATIONS
# =============================================================================

app.conf.task_annotations = {
    '*': {
        'rate_limit': '100/s',  # Default rate limit
    },
    'apps.payments.tasks.*': {
        'rate_limit': '10/s',  # Lower rate for payment tasks
        'max_retries': 3,
    },
}

# =============================================================================
# DEBUG TASK
# =============================================================================

@app.task(bind=True, ignore_result=True)
def debug_task(self):
    """Debug task to verify Celery is working."""
    print(f'Request: {self.request!r}')
