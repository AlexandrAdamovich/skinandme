from http import HTTPStatus

from flask import Blueprint, Response, make_response
from flask.views import MethodView
from sqlalchemy.sql import text

from app.controllers.exceptions import UnexpectedProvider
from app.controllers.provider_controller import ProviderController
from app.extensions import db
from app.models.models import CustomerOrder
from app.schemas.schemas import CustomerOrderSchema

api = Blueprint("api", __name__, url_prefix="/api")


class HealthCheck(MethodView):
    """Health endpoint."""

    def get(self) -> Response:
        """Ensure the system is reachable and the database connection is alive."""

        result = db.session.execute(text("SELECT 1;")).first()
        assert result == (1,)

        return make_response("This system is alive!", HTTPStatus.OK)


class SendOrder(MethodView):
    """
    API view for sending orders to shipping providers
    """
    def post(self, order_id: str, provider_id: str) -> Response:
        """
        Handles post requests for the "send-order" URL

        :param: order_id - order ID string to identify the order
        :param: provider_id - provider ID string to identify the provider
        """

        order = CustomerOrder.query.filter_by(order_id=order_id).first()
        if not order:
            message = f"Order with ID {order_id} was not found"
            return make_response({"success": False, "message": message}, HTTPStatus.NOT_FOUND)

        order_data = CustomerOrderSchema(context={"customer": order.customer}).dump(order)

        try:
            success = ProviderController(provider_id).send_order(order_data)
        except UnexpectedProvider:
            message = f"Provider with ID {provider_id} was not found"
            return make_response({"success": False, "message": message}, HTTPStatus.NOT_FOUND)

        if success:
            message = "OK"
            status = HTTPStatus.OK
        else:
            message = "Failed to send order to the provider"
            status = HTTPStatus.INTERNAL_SERVER_ERROR

        return make_response({"success": success, "message": message}, status)


api.add_url_rule("/health", view_func=HealthCheck.as_view("health"))
api.add_url_rule(
    "/send-order/<string:order_id>/shipping-provider/<string:provider_id>/",
    view_func=SendOrder.as_view("send_order")
)
