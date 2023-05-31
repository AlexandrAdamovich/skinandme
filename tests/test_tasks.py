from datetime import datetime, timedelta

from mock import patch, Mock

from app.clients.clients import DHLClient
from app.extensions import db
from app.models import CustomerOrder, Item, OrderItemLink
from app.models.models import ShippingIntervalEnum
from app.tasks.send_periodic_orders import send_periodic_orders
from tests.test_utils import create_test_customer_order


def test_send_periodic_monthly_order__order_is_sent_and_last_sent_time_is_updated(app):

    response_mock = Mock(json=Mock(return_value={}), status_code=200)
    session_mock = Mock(request=Mock(return_value=response_mock))
    session_patch = patch(
        'app.clients.clients.requests.Session', return_value=session_mock
    )

    customer_order = create_test_customer_order(
        shipping_interval=ShippingIntervalEnum.monthly,
        last_sent_at=datetime.now() - timedelta(days=31)
    )

    order_item_link = OrderItemLink(
        customer_order=customer_order,
        item=Item(item_id="mercedes", weight=200000),
        quantity=3
    )
    db.session.add(order_item_link)
    db.session.commit()

    with app.test_request_context(), session_patch:
        send_periodic_orders.apply()

        expected_outgoing_order_data = {
            "order_id": "test-order",
            "delivery_service": "standard",
            "delivery_address": {
                "line_1": "179 Harrow Road",
                "line_2": None,
                "postcode": "W2 6NB",
                "city": "London",
                "country_code": "GB",
                "recipient": "Joe Doe"
            },
            "items": [{"item_id": "mercedes", "quantity": 3, "weight": 200000}]
        }

        session_mock.request.assert_called_once_with(
            "post", DHLClient.API_URL, None, expected_outgoing_order_data, None
        )

        updated_customer_order = CustomerOrder.query.get(customer_order.id)
        assert updated_customer_order.last_sent_at >= datetime.now() - timedelta(seconds=3)


def test_send_periodic_monthly_order_that_is_not_yet_due__order_is_not_sent(app):

    response_mock = Mock(json=Mock(return_value={}), status_code=200)
    session_mock = Mock(request=Mock(return_value=response_mock))
    session_patch = patch(
        'app.clients.clients.requests.Session', return_value=session_mock
    )

    last_sent_at = datetime.now() - timedelta(days=29)
    customer_order = create_test_customer_order(
        shipping_interval=ShippingIntervalEnum.monthly,
        last_sent_at=last_sent_at
    )

    order_item_link = OrderItemLink(
        customer_order=customer_order,
        item=Item(item_id="mercedes", weight=200000),
        quantity=3
    )
    db.session.add(order_item_link)
    db.session.commit()

    with app.test_request_context(), session_patch:
        send_periodic_orders.apply()
        session_mock.request.assert_not_called()

        updated_customer_order = CustomerOrder.query.get(customer_order.id)
        assert updated_customer_order.last_sent_at == last_sent_at


def test_send_periodic_weekly_order__order_is_sent_and_last_sent_time_is_updated(app):

    response_mock = Mock(json=Mock(return_value={}), status_code=200)
    session_mock = Mock(request=Mock(return_value=response_mock))
    session_patch = patch(
        'app.clients.clients.requests.Session', return_value=session_mock
    )

    customer_order = create_test_customer_order(
        shipping_interval=ShippingIntervalEnum.weekly,
        last_sent_at=datetime.now() - timedelta(days=7)
    )

    order_item_link = OrderItemLink(
        customer_order=customer_order,
        item=Item(item_id="mercedes", weight=200000),
        quantity=3
    )
    db.session.add(order_item_link)
    db.session.commit()

    with app.test_request_context(), session_patch:
        send_periodic_orders.apply()

        expected_outgoing_order_data = {
            "order_id": "test-order",
            "delivery_service": "standard",
            "delivery_address": {
                "line_1": "179 Harrow Road",
                "line_2": None,
                "postcode": "W2 6NB",
                "city": "London",
                "country_code": "GB",
                "recipient": "Joe Doe"
            },
            "items": [{"item_id": "mercedes", "quantity": 3, "weight": 200000}]
        }

        session_mock.request.assert_called_once_with(
            "post", DHLClient.API_URL, None, expected_outgoing_order_data, None
        )

        updated_customer_order = CustomerOrder.query.get(customer_order.id)
        assert updated_customer_order.last_sent_at >= datetime.now() - timedelta(seconds=3)


def test_send_periodic_weekly_order_that_is_not_yet_due__order_is_not_sent(app):

    response_mock = Mock(json=Mock(return_value={}), status_code=200)
    session_mock = Mock(request=Mock(return_value=response_mock))
    session_patch = patch(
        'app.clients.clients.requests.Session', return_value=session_mock
    )

    last_sent_at = datetime.now() - timedelta(days=6)
    customer_order = create_test_customer_order(
        shipping_interval=ShippingIntervalEnum.weekly,
        last_sent_at=last_sent_at
    )

    order_item_link = OrderItemLink(
        customer_order=customer_order,
        item=Item(item_id="mercedes", weight=200000),
        quantity=3
    )
    db.session.add(order_item_link)
    db.session.commit()

    with app.test_request_context(), session_patch:
        send_periodic_orders.apply()
        session_mock.request.assert_not_called()

        updated_customer_order = CustomerOrder.query.get(customer_order.id)
        assert updated_customer_order.last_sent_at == last_sent_at


def test_send_periodic_monthly_order_with_last_sent_date_unset__order_is_not_sent(app):

    response_mock = Mock(json=Mock(return_value={}), status_code=200)
    session_mock = Mock(request=Mock(return_value=response_mock))
    session_patch = patch(
        'app.clients.clients.requests.Session', return_value=session_mock
    )

    customer_order = create_test_customer_order(
        shipping_interval=ShippingIntervalEnum.monthly,
        last_sent_at=None
    )

    order_item_link = OrderItemLink(
        customer_order=customer_order,
        item=Item(item_id="mercedes", weight=200000),
        quantity=3
    )
    db.session.add(order_item_link)
    db.session.commit()

    with app.test_request_context(), session_patch:
        send_periodic_orders.apply()
        session_mock.request.assert_not_called()

        updated_customer_order = CustomerOrder.query.get(customer_order.id)
        assert updated_customer_order.last_sent_at is None
