import requests

"""
Given more time I would add more viable logging
"""


class HttpClient:
    """
    Base client for making http requests
    """
    def __init__(self):
        """
        Initializes a client instance
        """
        self.session = requests.Session()
        self.login()

    def login(self):
        """
        Authorize with the API
        """
        pass

    def request(self, method, url, params=None, payload=None, headers=None):
        """
        Sends an HTTP request
        :param method: HTTP method to use for the request
        :param url: URL destination of the request
        :param params: HTTP parameters of the request
        :param payload: request body
        :param headers: HTTP headers of the request
        """
        try:
            response = self.session.request(method, url, params, payload, headers)
            response.raise_for_status()
        except requests.ConnectionError as exc:
            print(f"HTTP request failed due to a connection problem. URL: {url} Error: {exc}")
            return False, {}
        except requests.HTTPError as exc:
            print(f"Server responded an HTTP error. URL: {url} Error code: {exc.response.status_code}")
            return False, exc.response.json()

        return True, response.json()

    def post(self, url, params=None, payload=None, headers=None):
        """
        Sends a post request to the specified URL
        :param url: URL destination for the request
        :param params: HTTP parameters of the request
        :param headers: HTTP headers of the request
        """
        return self.request("post", url, params, payload, headers)


class BaseProviderClient(HttpClient):
    """
    Base HTTP client for shipping providers
    """
    def send_order(self, order_data: dict) -> bool:
        pass


class DHLClient(BaseProviderClient):
    """
    HTTP client for sending orders to DHL shipping provider
    """
    API_URL = "http://dummy.dhl.com/create-order/"
    AUTH_TOKEN = "test-dhl-token"

    def login(self):
        """
        Authorize with the DHL API
        """
        self.session.headers.update({"Authorization": f"Bearer {self.AUTH_TOKEN}"})

    def send_order(self, order_data: dict) -> bool:
        """
        Send order data to the provider
        """
        success, _ = self.post(self.API_URL, payload=order_data)

        return success


class RoyalMailClient(BaseProviderClient):
    """
    HTTP client for sending orders to Royal Mail shipping provider
    """
    API_URL = "http://dummy.royal-mail.com/create-order/"
    LOGIN = "test-royal-mail-login"
    PASSWORD = "test-royal-mail-password"

    def login(self) -> None:
        """
        Authorize with the Royal Mail API
        """
        self.session.auth = (self.LOGIN, self.PASSWORD)

    def send_order(self, order_data: dict) -> bool:
        """
        Send order data to the shipping provider

        :param order_data: dictionary with the order data
        """
        success, _ = self.post(self.API_URL, payload=order_data)

        return success
