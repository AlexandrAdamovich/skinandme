from app.extensions import db
from app.models import Address, Customer, CustomerOrder


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
