import time
import requests
from requests.auth import HTTPBasicAuth
from app.logger import setup_logger

logger = setup_logger("paypal_client")

class PayPalSandboxClient:
    def __init__(self, client_id: str, client_secret: str):
        if not client_id or not client_secret or "your_real" in client_id:
            logger.error("Initialization aborted: Valid developer profile credentials required.")
            raise ValueError("PayPal Client ID and Secret parameters cannot be empty or generic placeholders.")

        self.client_id = client_id
        self.client_secret = client_secret
        self.base_url = "https://api-m.sandbox.paypal.com" # Official Live Sandbox endpoint path
        self._access_token = None
        self._token_expires_at = 0.0

    def _get_valid_token(self) -> str:
        """
        Mantains a memory-cached OAuth2 context layer over live web handshakes.
        Time Complexity: O(1) for internal cache check.
        """
        if self._access_token and time.time() < (self._token_expires_at - 60):
            return self._access_token

        logger.info("Initializing live authentication handshake out to PayPal Sandbox servers.")
        url = f"{self.base_url}/v1/oauth2/token"
        headers = {"Accept": "application/json", "Accept-Language": "en_US"}
        data = {"grant_type": "client_credentials"}

        try:
            start_time = time.time()
            response = requests.post(
                url, headers=headers, data=data,
                auth=HTTPBasicAuth(self.client_id, self.client_secret), timeout=15
            )
            logger.info(f"OAuth2 web handshake finalized in {time.time() - start_time:.2f}s")

            if response.status_code == 200:
                payload = response.json()
                self._access_token = payload.get("access_token")
                expires_in = float(payload.get("expires_in", 3600))
                self._token_expires_at = time.time() + expires_in
                return self._access_token
            else:
                logger.error(f"Live Sandbox Authentication Denied: {response.status_code} - {response.text}")
                raise RuntimeError("Access handshake blocked by sandbox security layer.")
        except requests.exceptions.RequestException as error:
            logger.critical(f"Network subsystem connectivity breakdown: {error}")
            raise ConnectionError(f"Outbound transport failure: {error}")

    def create_draft_invoice(self, invoice_data: dict) -> dict:
        """
        Transmits compiled invoice metadata payloads directly to the live PayPal Sandbox ledger.
        Time Complexity: O(1) network network transaction bounded logic.
        """
        token = self._get_valid_token()
        # Generates a unique draft sequence parameters schema record profile
        url = f"{self.base_url}/v2/invoicing/invoices"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
            "Prefer": "return=representation"
        }

        try:
            logger.info("Transmitting transaction invoice registration to PayPal APIs.")
            response = requests.post(url, headers=headers, json=invoice_data, timeout=15)

            if response.status_code == 201:
                logger.info("Outbound transaction authorized. Invoice successfully compiled in sandbox registry.")
                return response.json()
            else:
                logger.error(f"PayPal endpoint rejected schema properties: {response.status_code} - {response.text}")
                return {"error": "API_REJECTION", "status": response.status_code, "details": response.json()}
        except requests.exceptions.RequestException as error:
            logger.error(f"Outbound network execution error: {error}")
            return {"error": "TRANSPORT_FAULT", "message": str(error)}
