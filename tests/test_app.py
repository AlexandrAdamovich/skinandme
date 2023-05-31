from http import HTTPStatus

from flask import url_for

from app.extensions import db
from app.models import Address, Customer, CustomerOrder, ShippingEvent
from app.models.models import ShippingEventsEnum
from datetime import datetime


def test_api_health_endpoint(app):
    """Test API health endpoint."""

    with app.test_request_context(), app.test_client() as test_client:
        response = test_client.get(url_for("api.health"))

    assert response.status_code == HTTPStatus.OK


def test_customer_order_model():
    """Test customer order model."""

    customer_order = CustomerOrder(
        order_id="test-order",
        shipping_provider="dhl",
        customer=Customer(
            first_name="Joe",
            last_name="Doe",
        ),
        delivery_address=Address(
            line_1="179 Harrow Road",
            postcode="W2 6NB",
            city="London",
            country_code="GB",
        ),
    )

    db.session.add(customer_order)
    db.session.commit()

    customer = db.session.query(Customer).one()
    assert customer.first_name == "Joe"
    assert customer.last_name == "Doe"

    address = db.session.query(Address).one()
    assert address.line_1 == "179 Harrow Road"
    assert address.postcode == "W2 6NB"
    assert address.city == "London"
    assert address.country_code == "GB"

    customer_order = (
        db.session.query(CustomerOrder)
        .filter(CustomerOrder.customer_id == customer.id)
        .filter(CustomerOrder.delivery_address_id == address.id)
        .one()
    )
    assert customer_order.id == 1


def test_shipping_event_model():
    """Test shipping event model."""

    event_time = datetime.now()
    shipping_event = ShippingEvent(
        event_name="delivered",
        event_time=event_time,
        order=CustomerOrder(
            order_id="test-order",
            shipping_provider="dhl",
            customer=Customer(
                first_name="Joe",
                last_name="Doe",
            ),
            delivery_address=Address(
                line_1="179 Harrow Road",
                postcode="W2 6NB",
                city="London",
                country_code="GB",
            ),
        ),
    )

    db.session.add(shipping_event)
    db.session.commit()

    shipping_event = db.session.query(ShippingEvent).one()
    assert shipping_event.event_name == ShippingEventsEnum.delivered
    assert shipping_event.event_time == event_time
    assert shipping_event.order.order_id == "test-order"

    order = db.session.query(CustomerOrder).one()
    assert order.order_id == "test-order"

    shipping_event = (
        db.session.query(ShippingEvent)
        .filter(ShippingEvent.order_id == order.id)
        .one()
    )
    assert shipping_event.id == 1
