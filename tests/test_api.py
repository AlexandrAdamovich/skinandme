from flask import url_for
from mock import patch, Mock
from app.extensions import db
from app.models import Address, Customer, CustomerOrder, Item, OrderItemLink
from app.clients.clients import DHLClient


def test_send_customer_order__shipping_provider_api_called_with_correct_parameters(app):
    """Test customer order model."""

    response_mock = Mock(json=Mock(return_value={}), status_code=200)
    session_mock = Mock(request=Mock(return_value=response_mock))
    session_patch = patch(
        'app.clients.clients.requests.Session', return_value=session_mock
    )

    customer_order = CustomerOrder(
        order_id="test-order",
        delivery_service="standard",
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

    order_item_link = OrderItemLink(
        customer_order=customer_order,
        item=Item(item_id="mercedes", weight=200000),
        quantity=3
    )
    db.session.add(customer_order)
    db.session.add(order_item_link)
    db.session.commit()
    with app.test_request_context(), app.test_client() as test_client, session_patch:
        response = test_client.post(url_for("api.send_order", order_id="test-order", provider_id="dhl"))

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
    customer_order = CustomerOrder(
        order_id="test-order",
        delivery_service="standard",
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

    with app.test_request_context(), app.test_client() as test_client, session_patch:
        response = test_client.post(
            url_for("api.send_order", order_id="test-order", provider_id="invalid-provider")
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
            url_for("api.send_order", order_id="test-order", provider_id="dhl")
        )

        session_mock.request.assert_not_called()
        assert response.status_code == 404
        assert response.json == {"success": False, "message": f"Order with ID test-order was not found"}
