from marshmallow_sqlalchemy import SQLAlchemySchema, auto_field
from marshmallow_sqlalchemy.fields import fields, Nested

from app.models.models import CustomerOrder, OrderItemLink, DeliveryServiceEnum, Address


class OrderItemSchema(SQLAlchemySchema):
    """
    Serializer for items related to an order including quantity
    """
    class Meta:
        model = OrderItemLink
        load_instance = True

    item_id = fields.String(attribute="item.item_id")
    weight = fields.Integer(attribute="item.weight")
    quantity = auto_field()


class AddressSchema(SQLAlchemySchema):
    """
    Serializer for address objects
    """
    class Meta:
        model = Address
        load_instance = True

    line_1 = auto_field()
    line_2 = auto_field()
    postcode = auto_field()
    city = auto_field()
    country_code = auto_field()
    recipient = fields.Method("get_recipient_full_name")

    def get_recipient_full_name(self, address):
        """
        Gets value for the recipient field in the serializer
        """
        return address.customer.first_name + " " + address.customer.last_name


class CustomerOrderSchema(SQLAlchemySchema):
    """
    Serializer for customer order objects
    """
    class Meta:
        model = CustomerOrder
        load_instance = True

    order_id = auto_field()
    delivery_service = fields.Enum(enum=DeliveryServiceEnum)
    items = Nested(OrderItemSchema, many=True)
    delivery_address = Nested(AddressSchema)
