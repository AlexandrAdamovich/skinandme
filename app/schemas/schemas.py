from marshmallow_sqlalchemy import SQLAlchemySchema, auto_field
from marshmallow_sqlalchemy.fields import fields, Nested
from marshmallow.exceptions import ValidationError
from app.models.models import CustomerOrder, OrderItemLink, DeliveryServiceEnum, Address, ShippingEvent, ShippingEventsEnum


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


class OrderAddressNestedSchema(SQLAlchemySchema):
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
        return self.context["customer"].first_name + " " + self.context["customer"].last_name


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
    delivery_address = Nested(OrderAddressNestedSchema)


class ShippingEventSchema(SQLAlchemySchema):
    """
    Schema for deserializing json shipping events into objects
    """
    class Meta:
        model = ShippingEvent
        load_instance = True

    event_time = fields.DateTime()
    event_name = fields.Enum(enum=ShippingEventsEnum)
    order_id = fields.Method(serialize="get_str_order_id", deserialize="convert_order_id_str_to_int")

    def get_str_order_id(self, obj):
        """
        Expose public string ID of the order instead of the internal one
        """
        return obj.order.order_id

    def convert_order_id_str_to_int(self, str_order_id):
        """
        Deserialization method to turn a public string order ID
        into an internal integer order ID
        """
        order = CustomerOrder.query.filter_by(order_id=str_order_id).first()
        if not order:
            message = f"Order with string ID {str_order_id} was not found"
            raise ValidationError(message, "order_id", str_order_id)

        return order.id


