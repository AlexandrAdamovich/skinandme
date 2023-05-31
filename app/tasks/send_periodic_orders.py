import celery
from celery.utils.log import get_task_logger
from app.models.models import CustomerOrder, ShippingIntervalEnum
from app.utils.provider_controller import ProviderController
from dateutil.relativedelta import relativedelta
from datetime import datetime

logger = get_task_logger(__name__)


@celery.shared_task()
def send_periodic_orders():
    """
    Periodic tasks that is to be run every day
    to check if any weekly or monthly orders are due for sending
    """

    monthly_orders = CustomerOrder.query.filter_by(
        shipping_interval=ShippingIntervalEnum.monthly
    ).all()
    for order in monthly_orders:
        if order.last_sent_at and datetime.now() >= order.last_sent_at + relativedelta(months=1):
            logger.info(f"Monthly order is being sent: {order.order_id}")
            ProviderController(order.shipping_provider).send_order(order)

    weekly_orders = CustomerOrder.query.filter_by(
        shipping_interval=ShippingIntervalEnum.weekly
    ).all()
    for order in weekly_orders:
        if order.last_sent_at and datetime.now() >= order.last_sent_at + relativedelta(weeks=1):
            logger.info(f"Weekly order is being sent: {order.order_id}")
            ProviderController(order.shipping_provider).send_order(order)
