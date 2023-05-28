from app.models.models import CustomerOrder, OrderItemsAssociation, DeliveryServiceEnum
from marshmallow_sqlalchemy import SQLAlchemySchema, auto_field
from marshmallow_sqlalchemy.fields import fields, Nested

from marshmallow_sqlalchemy import SQLAlchemySchema, auto_field


class OrderItemSchema(SQLAlchemySchema):
    class Meta:
        model = OrderItemsAssociation
        load_instance = True

    item_id = fields.String(attribute="item.item_id")
    weight = fields.Integer(attribute="item.weight")
    quantity = auto_field()


class CustomerOrderSchema(SQLAlchemySchema):
    class Meta:
        model = CustomerOrder
        load_instance = True

    order_id = auto_field()
    delivery_service = fields.Enum(enum=DeliveryServiceEnum)
    order_items = Nested(OrderItemSchema, many=True)
