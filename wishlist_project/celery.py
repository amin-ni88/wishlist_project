from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'wishlist_project.settings')

app = Celery('wishlist_project')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

# Configure Celery Beat schedule
app.conf.beat_schedule = {
    'check-upcoming-occasions': {
        'task': 'core.tasks.check_upcoming_occasions',
        'schedule': 86400.0,  # Run daily
    },
    'check-subscription-status': {
        'task': 'core.tasks.check_subscription_status',
        'schedule': 3600.0,  # Run hourly
    },
    'process-subscription-renewals': {
        'task': 'core.tasks.subscription_renewal.process_subscription_renewals',
        'schedule': 3600.0,  # Run hourly
    },
    'clean-old-notifications': {
        'task': 'core.tasks.notifications.clean_old_notifications',
        'schedule': 604800.0,  # Run weekly
    },
    'send-daily-contribution-summary': {
        'task': 'core.tasks.notifications.send_daily_contribution_summary',
        'schedule': 86400.0,  # Run daily
    },
    'check-price-changes': {
        'task': 'core.tasks.notifications.check_price_changes',
        'schedule': 3600.0,  # Run hourly
    }
}

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
