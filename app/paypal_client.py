import time
import requests
from requests.auth import HTTPBasicAuth
from app.logger import setup_logger

logger = setup_logger("paypal_client")

class PayPalSandboxClient:
    def __init__(self, client_id: str, client_secret: str):
        if not client_id or not client_secret:
            logger.error("Initialization failed: Missing operational secret parameters.")
            raise ValueError("PayPal Client ID and Secret cannot be empty string arguments.")

        self.client_id = client_id
        self.client_secret = client_secret
        self.base_url = "https://paypal.com"
        self._access_token = None
        self._token_expires_at = 0.0

    def _get_valid_token(self) -> str:
        """
        Maintains an optimized memory cache for OAuth2 access tokens.
        Time Complexity: O(1) constant check.
        Space Complexity: O(1).
        """
        if self._access_token and time.time() < (self._token_expires_at - 60):
            return self._access_token

        logger.info("Access token missing or expired. Initializing sandbox OAuth2 handshake.")
        url = f"{self.base_url}/v1/oauth2/token"
        headers = {"Accept": "application/json", "Accept-Language": "en_US"}
        data = {"grant_type": "client_credentials"}

        try:
            start_time = time.time()
            response = requests.post(
                url, headers=headers, data=data,
                auth=HTTPBasicAuth(self.client_id, self.client_secret), timeout=15
            )
            logger.info(f"OAuth2 Token request completed in {time.time() - start_time:.2f}s")

            if response.status_code == 200:
                payload = response.json()
                self._access_token = payload.get("access_token")
                expires_in = float(payload.get("expires_in", 3600))
                self._token_expires_at = time.time() + expires_in
                logger.info("New bearer token successfully stored in application state cache.")
                return self._access_token
            else:
                logger.error(f"OAuth Handshake Refused: Status {response.status_code} - {response.text}")
                raise RuntimeError(f"PayPal authentication boundary block failure.")
        except requests.exceptions.RequestException as error:
            logger.critical(f"Network subsystem connectivity breakdown: {error}")
            raise ConnectionError(f"API Transport error: {error}")

    def create_draft_invoice(self, invoice_data: dict) -> dict:
        """
        Transmits compiled invoice metadata payloads straight to the sandbox API.
        Time Complexity: O(1) network transaction bound.
        """
        token = self._get_valid_token()
        url = f"{self.base_url}/v2/invoicing/invoices"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
            "Prefer": "return=representation"
        }

        try:
            logger.info("Transmitting structured draft invoice payload configuration.")
            response = requests.post(url, headers=headers, json=invoice_data, timeout=15)

            if response.status_code == 201:
                logger.info("Invoice validation successfully completed within sandbox registry.")
                return response.json()
            else:
                logger.error(f"Invoicing endpoint rejected transaction layout: {response.status_code} - {response.text}")
                return {"error": "API_REJECTION", "status": response.status_code, "details": response.text}
        except requests.exceptions.RequestException as error:
            logger.error(f"Failed network packet transmission to invoicing API framework: {error}")
            return {"error": "TRANSPORT_FAULT", "message": str(error)}
