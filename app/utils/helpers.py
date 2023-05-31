from datetime import datetime
from app.models.models import CustomerOrder
from app.extensions import db


def update_order_last_sent_datetime(order: CustomerOrder, last_sent_at: datetime = None):
    """
    Update last sent datetime of the order to the given datetime or current datetime by default
    :param order: Order object to update
    :param last_sent_at: new value for the last_sent_at field of the order
    """

    order.last_sent_at = last_sent_at or datetime.now()
    db.session.commit()


