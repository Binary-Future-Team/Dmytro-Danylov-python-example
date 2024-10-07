import os

from celery import Celery
from celery.schedules import crontab
from envparse import env

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "***.settings")

RABBITMQ_HOST = env.str("RABBITMQ_HOST")
RABBITMQ_PORT = env.int("RABBITMQ_PORT")
RABBITMQ_USER = env.str("RABBITMQ_DEFAULT_USER")
RABBITMQ_PASSWORD = env.str("RABBITMQ_DEFAULT_PASS")

app = Celery("***")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

app.conf.broker_url = f"amqp://{RABBITMQ_USER}:{RABBITMQ_PASSWORD}@{RABBITMQ_HOST}:{RABBITMQ_PORT}/"
app.conf.beat_max_loop_interval = 120
app.conf.beat_schedule = {
    # disabled by request from *** when modev to Klaviyo
    # "notify_about_new_colors": {
    #     "task": "colors.tasks.notify_about_new_colors",
    #     "schedule": crontab(minute="0", hour="14"),  # every day at 14:00
    # },
    # disabled by request from *** when modev to Klaviyo
    # "notify_unsynced_products": {
    #     "task": "products.tasks.notify_unsynced_products",
    #     "schedule": crontab(minute="0", hour="2"),  # every day at 02:00
    # },
    "generate_products_feed": {
        "task": "products.tasks.generate_products_feed",
        "schedule": crontab(minute="0", hour="3"),  # every day at 03:00
    },
    "generate_products_feed": {
        "task": "products.tasks.generate_products_feed",
        "schedule": crontab(minute="0", hour="3"),  # every day at 03:00
    },
    "sync_vendors_products": {
        "task": "vendors.tasks.sync_vendors_products",
        "schedule": crontab(minute="0", hour="1"),  # every day at 01:00
    },
    "clear_archived_products": {
        "task": "vendors.tasks.clear_archived_products",
        "schedule": crontab(minute="0", hour="10"),  # every day at 10:00
    },
    "update_consignment_payment_reference": {
        "task": "orders.tasks.update_consignment_payment_reference",
        "schedule": crontab(minute="*/15"),  # every 15 minutes
    },
    "sync_shopify_orders": {
        "task": "orders.tasks.sync_shopify_orders",
        "schedule": crontab(minute="0", hour="*/6"),  # every 6 hours
    },
    "create_missing_shopify_orders": {
        "task": "orders.tasks.create_missing_shopify_orders",
        "schedule": crontab(minute="0", hour="*/4"),  # every 4 hours
    },
    "notify_about_invalid_connection": {
        "task": "orders.tasks.notify_about_invalid_connection",
        "schedule": crontab(minute="0", hour="11"),  # every day at 11:00
    },
    "set_in_payout_date": {
        "task": "orders.tasks.set_in_payout_date",
        "schedule": crontab(minute="0", hour="*/4"),  # every 6 hours
    },
    # "notify_vendor_about_unsynced_products": {
    #     "task": "vendors.tasks.notify_vendor_about_unsynced_products",
    #     "schedule": crontab(minute="0", hour="20"),  # every day at 20:00
    # },
}

app.conf.timezone = "UTC"
