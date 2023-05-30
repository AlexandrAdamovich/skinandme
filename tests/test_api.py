from flask import url_for
from mock import patch, Mock
from app.extensions import db
from app.models import Address, Customer, CustomerOrder, Item, OrderItemLink, ShippingEvent
from app.clients.clients import DHLClient
from datetime import datetime
from app.models.models import ShippingEventsEnum


def create_test_customer_order(**kwargs):
    default_order_data = {
        "order_id": "test-order",
        "shipping_provider": "dhl",
        "delivery_service": "standard",
        "customer": Customer(
            first_name="Joe",
            last_name="Doe",
        ),
        "delivery_address": Address(
            line_1="179 Harrow Road",
            postcode="W2 6NB",
            city="London",
            country_code="GB",
        ),
    }
    order_data = {**default_order_data, **kwargs}

    customer_order = CustomerOrder(**order_data)
    db.session.add(customer_order)
    db.session.commit()

    return customer_order


def test_send_customer_order__shipping_provider_api_called_with_correct_parameters(app):
    """Test customer order model."""

    response_mock = Mock(json=Mock(return_value={}), status_code=200)
    session_mock = Mock(request=Mock(return_value=response_mock))
    session_patch = patch(
        'app.clients.clients.requests.Session', return_value=session_mock
    )

    customer_order = create_test_customer_order()

    order_item_link = OrderItemLink(
        customer_order=customer_order,
        item=Item(item_id="mercedes", weight=200000),
        quantity=3
    )
    db.session.add(order_item_link)
    db.session.commit()

    with app.test_request_context(), app.test_client() as test_client, session_patch:
        response = test_client.post(url_for("api.send_order", order_id="test-order"))

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
        assert response.status_code == 200
        assert response.json == {"success": True, "message": "OK"}


def test_send_customer_order_with_invalid_provider__404_error_in_response(app):
    """Test customer order model."""

    response_mock = Mock(json=Mock(return_value={}), status_code=200)
    session_mock = Mock(request=Mock(return_value=response_mock))
    session_patch = patch(
        'app.clients.clients.requests.Session', return_value=session_mock
    )
    create_test_customer_order(shipping_provider="invalid-provider")

    with app.test_request_context(), app.test_client() as test_client, session_patch:
        response = test_client.post(
            url_for("api.send_order", order_id="test-order")
        )

        session_mock.request.assert_not_called()
        assert response.status_code == 404
        assert response.json == {"success": False, "message": f"Provider with ID invalid-provider was not found"}


def test_send_customer_order_with_invalid_order_id__404_error_in_response(app):
    """Test customer order model."""

    response_mock = Mock(json=Mock(return_value={}), status_code=200)
    session_mock = Mock(request=Mock(return_value=response_mock))
    session_patch = patch(
        'app.clients.clients.requests.Session', return_value=session_mock
    )

    with app.test_request_context(), app.test_client() as test_client, session_patch:
        response = test_client.post(
            url_for("api.send_order", order_id="test-order")
        )

        session_mock.request.assert_not_called()
        assert response.status_code == 404
        assert response.json == {"success": False, "message": f"Order with ID test-order was not found"}


def test_handle_shipping_event_endpoint__shipping_event_saved_into_db_linked_to_order(app):
    customer_order = create_test_customer_order()

    event_time = datetime.now()
    shipping_event = {
        "event_name": "delivered",
        "event_time": event_time.isoformat(),
        "order_id": "test-order"
    }
    with app.test_request_context(), app.test_client() as test_client:
        response = test_client.post(
            url_for("api.handle_shipping_event"),
            json=shipping_event,
            headers={"Content-type": "application/json"}
        )

        assert response.status_code == 200
        assert response.json == {"message": "OK"}

        shipping_event_obj = ShippingEvent.query.filter_by(order_id=customer_order.id).first()
        assert shipping_event_obj.event_name == ShippingEventsEnum.delivered
        assert shipping_event_obj.event_time == event_time


def test_handle_shipping_event_with_invalid_order_id__400_error_in_response(app):
    customer_order = create_test_customer_order()

    event_time = datetime.now()
    shipping_event = {
        "event_name": "delivered",
        "event_time": event_time.isoformat(),
        "order_id": "invalid-test-order"
    }
    with app.test_request_context(), app.test_client() as test_client:
        response = test_client.post(
            url_for("api.handle_shipping_event"),
            json=shipping_event,
            headers={"Content-type": "application/json"}
        )

        assert response.status_code == 400
        assert response.json == {"message": {"order_id": [f"Order with string ID invalid-test-order was not found"]}}

        shipping_event_obj = ShippingEvent.query.filter_by(order_id=customer_order.id).first()
        assert shipping_event_obj is None


def test_handle_shipping_event_with_invalid_event_name__400_error_in_response(app):
    customer_order = create_test_customer_order()

    event_time = datetime.now()
    shipping_event = {
        "event_name": "catapulted",
        "event_time": event_time.isoformat(),
        "order_id": "test-order"
    }
    with app.test_request_context(), app.test_client() as test_client:
        response = test_client.post(
            url_for("api.handle_shipping_event"),
            json=shipping_event,
            headers={"Content-type": "application/json"}
        )

        assert response.status_code == 400
        assert response.json == {
            "message": {"event_name": ['Must be one of: waiting_for_collection, in_transit, delivered, failed.']}
        }

        shipping_event_obj = ShippingEvent.query.filter_by(order_id=customer_order.id).first()
        assert shipping_event_obj is None
