import enum
from typing import List

from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship, DeclarativeBase, Mapped, mapped_column

from app.extensions import db


class DeliveryServiceEnum(enum.Enum):
    standard = "standard"
    express = "express"


class Base(DeclarativeBase):
    pass


class OrderItemsAssociation(Base):
    __tablename__ = "order_items_associations"

    customer_order_id: Mapped[int] = mapped_column(ForeignKey("customer_orders.id"), primary_key=True)
    item_id: Mapped[int] = mapped_column(ForeignKey("items.id"), primary_key=True)

    quantity: Mapped[int] = db.Column(db.Integer, default=1, nullable=False)
    item: Mapped["Item"] = relationship()
    customer_order: Mapped["CustomerOrder"] = relationship()


class Item(Base):
    """Item model."""

    __tablename__ = "items"

    id: Mapped[int] = mapped_column(primary_key=True)
    item_id = db.Column(db.String(35), unique=True)
    weight = db.Column(db.Integer)


class CustomerOrder(Base):
    """Customer order model."""
    __tablename__ = "customer_orders"

    id: Mapped[int] = mapped_column(primary_key=True)
    order_id = db.Column(db.String(35), unique=True)
    delivery_service = db.Column(
        db.Enum(DeliveryServiceEnum), default=DeliveryServiceEnum.standard, nullable=False
    )
    items: Mapped[List["OrderItemsAssociation"]] = relationship(back_populates="customer_order")

    customer_id = db.Column(db.Integer, db.ForeignKey("customer.id"))
    delivery_address_id = db.Column(db.Integer, db.ForeignKey("address.id"))

    customer = relationship("Customer", foreign_keys=customer_id)
    delivery_address = relationship("Address", foreign_keys=delivery_address_id)


class Customer(Base):
    """Customer model."""
    __tablename__ = "customer"

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(255))
    last_name = db.Column(db.String(255))

    customer_orders = relationship("CustomerOrder", viewonly=True)


class Address(Base):
    """Address model."""
    __tablename__ = "address"

    id = db.Column(db.Integer, primary_key=True)
    line_1 = db.Column(db.String(255))
    line_2 = db.Column(db.String(255))
    postcode = db.Column(db.String(255))
    city = db.Column(db.String(255))
    country_code = db.Column(db.String(255))
