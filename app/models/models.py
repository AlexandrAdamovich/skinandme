import datetime
import enum
from typing import List

from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column

from app.extensions import db


class DeliveryServiceEnum(enum.Enum):
    """Delivery service types enum"""

    standard = "standard"
    express = "express"


class OrderItemLink(db.Model):
    """Many-to-many links model connecting orders with items"""

    __tablename__ = "order_items_links"

    customer_order_id: Mapped[int] = mapped_column(ForeignKey("customer_orders.id"), primary_key=True)
    item_id: Mapped[int] = mapped_column(ForeignKey("items.id"), primary_key=True)

    quantity: Mapped[int] = db.Column(db.Integer, default=1, nullable=False)
    item: Mapped["Item"] = relationship()
    customer_order: Mapped["CustomerOrder"] = relationship()


class Item(db.Model):
    """Item model."""

    __tablename__ = "items"

    id: Mapped[int] = mapped_column(primary_key=True)
    item_id = db.Column(db.String(35), unique=True)
    weight = db.Column(db.Integer)


class ShippingIntervalEnum(enum.Enum):
    monthly = "monthly"
    weekly = "weekly"


class ShippingProviderEnum(enum.Enum):
    dhl = "dhl"
    royal_mail = "royal_mail"
    amazon_prime = "amazon_prime"


class CustomerOrder(db.Model):
    """Customer order model."""

    __tablename__ = "customer_orders"

    id: Mapped[int] = mapped_column(primary_key=True)
    order_id = db.Column(db.String(35), unique=True)
    delivery_service = db.Column(
        db.Enum(DeliveryServiceEnum), default=DeliveryServiceEnum.standard, nullable=False
    )
    items: Mapped[List["OrderItemLink"]] = relationship(back_populates="customer_order")

    customer_id = db.Column(db.Integer, db.ForeignKey("customer.id"))
    delivery_address_id = db.Column(db.Integer, db.ForeignKey("address.id"))
    customer = relationship("Customer", foreign_keys=customer_id)
    delivery_address = relationship("Address", foreign_keys=delivery_address_id)

    created_at = db.Column(db.DateTime, default=datetime.datetime.now)
    shipping_interval = db.Column(db.Enum(ShippingIntervalEnum), nullable=True)
    shipping_provider = db.Column(db.Enum(ShippingProviderEnum), nullable=False)
    last_sent_at = db.Column(db.DateTime, nullable=True)


class Customer(db.Model):
    """Customer model."""

    __tablename__ = "customer"

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(255))
    last_name = db.Column(db.String(255))

    customer_orders = relationship("CustomerOrder", viewonly=True)


class Address(db.Model):
    """Address model."""

    __tablename__ = "address"

    id = db.Column(db.Integer, primary_key=True)
    line_1 = db.Column(db.String(255))
    line_2 = db.Column(db.String(255))
    postcode = db.Column(db.String(255))
    city = db.Column(db.String(255))
    country_code = db.Column(db.String(255))


class ShippingEventsEnum(enum.Enum):
    """Enum declaring possible types of shipping events"""

    waiting_for_collection = "waiting-for-collection"
    in_transit = "in-transit"
    delivered = "delivered"
    failed = "failed-to-deliver"


class ShippingEvent(db.Model):
    """Shipping event model."""

    __tablename__ = "shipping_events"

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("customer_orders.id"))
    order = relationship("CustomerOrder", foreign_keys=order_id)
    event_name = db.Column(db.Enum(ShippingEventsEnum), nullable=False)
    event_time = db.Column(db.DateTime, nullable=False)
