from celery.schedules import crontab


imports = ('app.tasks.send_periodic_orders',)
timezone = 'UTC'

accept_content = ['json', 'msgpack', 'yaml']
broker_url = "redis://redis:6379/"
result_backend = "redis://redis:6379"

beat_schedule = {
    'test-celery': {
        'task': 'app.tasks.send_periodic_orders.send_periodic_orders',
        # Every minute
        'schedule': crontab(hour=0, minute=0),
    }
}
