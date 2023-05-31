from app.clients.clients import BaseProviderClient, DHLClient, RoyalMailClient
from app.utils.exceptions import UnexpectedProvider
from app.utils.helpers import update_order_last_sent_datetime
from app.schemas.schemas import CustomerOrderSchema
from app.models.models import CustomerOrder, ShippingProviderEnum


class ProviderController:
    """
    Controller class for handling requests to shipping providers

    It includes a factory method to determine the shipping provider client
    based on provider ID
    """
    shipping_providers_clients = {
        ShippingProviderEnum.royal_mail: RoyalMailClient,
        ShippingProviderEnum.dhl: DHLClient
    }

    def __init__(self, provider_id: ShippingProviderEnum) -> None:
        """
        Initializes the client based on the provider ID
        :param provider_id: ID string of the provider
        """
        provider_client_class = self.shipping_providers_clients.get(provider_id)
        if provider_client_class:
            self.client: BaseProviderClient = provider_client_class()
        else:
            raise UnexpectedProvider

    def send_order(self, order: CustomerOrder) -> bool:
        """
        Sends order to the shipping provider
        :param order: Order object which data is to be sent to the provider
        """
        order_data = CustomerOrderSchema(context={"customer": order.customer}).dump(order)
        result = self.client.send_order(order_data)

        if result:
            update_order_last_sent_datetime(order)

        return result
