from app.clients.clients import BaseProviderClient, DHLClient, RoyalMailClient
from app.controllers.exceptions import UnexpectedProvider


class ShippingProviders:
    dhl = "dhl"
    royal_mail = "royal_mail"


class ProviderController:
    """
    Controller class for handling requests to shipping providers

    It includes a factory method to determine the shipping provider client
    based on provider ID
    """
    shipping_providers_clients = {
        ShippingProviders.royal_mail: RoyalMailClient,
        ShippingProviders.dhl: DHLClient
    }

    def __init__(self, provider_id: str) -> None:
        """
        Initializes the client based on the provider ID
        :param provider_id: ID string of the provider
        """
        provider_client_class = self.shipping_providers_clients.get(provider_id)
        if provider_client_class:
            self.client: BaseProviderClient = provider_client_class()
        else:
            raise UnexpectedProvider

    def send_order(self, order_data: dict) -> bool:
        """
        Sends order to the shipping provider
        :param order_data: dictionary containing the order data
        """
        return self.client.send_order(order_data)

