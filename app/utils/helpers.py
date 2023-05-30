from datetime import datetime
from app.models.models import CustomerOrder
from app.extensions import db


def update_order_last_sent_datetime(order: CustomerOrder, last_sent_at: datetime = None):
    order.last_sent_at = last_sent_at or datetime.now()
    db.session.commit()


