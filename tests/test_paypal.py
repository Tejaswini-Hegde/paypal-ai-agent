import unittest
from unittest.mock import patch, MagicMock
import time

# Absolute path imports mapped out explicitly
from app.agent import AITreasuryAgent
from app.paypal_client import PayPalSandboxClient
from app.database import LocalStateLedger


class TestAITreasuryAgent(unittest.TestCase):
    def setUp(self):
        self.agent = AITreasuryAgent()

    @patch('ollama.generate')
    def test_parse_cross_border_intent_success(self, mock_ollama):
        """Verifies the AI agent extracts multi-currency properties correctly from clean responses."""
        mock_response = {
            'response': (
                '{\n'
                '  "action": "CREATE_INVOICE",\n'
                '  "recipient": "supplier@euro-distribution.com",\n'
                '  "target_currency": "EUR",\n'
                '  "source_budget_cap": "2500.00",\n'
                '  "source_currency": "USD",\n'
                '  "item_name": "Custom Parts Assembly",\n'
                '  "quantity": "50"\n'
                '}'
            )
        }
        mock_ollama.return_value = mock_response

        prompt = "Send 2500 USD to supplier@euro-distribution.com converted to EUR"
        result = self.agent.parse_cross_border_intent(prompt)

        self.assertEqual(result["action"], "CREATE_INVOICE")
        self.assertEqual(result["target_currency"], "EUR")
        self.assertEqual(result["source_currency"], "USD")
        self.assertEqual(float(result["source_budget_cap"]), 2500.00)
        self.assertEqual(result["recipient"], "supplier@euro-distribution.com")


class TestPayPalSandboxClient(unittest.TestCase):
    def setUp(self):
        self.client_id = "MOCK_CLIENT_ID"
        self.client_secret = "MOCK_SECRET"
        self.client = PayPalSandboxClient(self.client_id, self.client_secret)

    @patch('requests.post')
    def test_token_caching_logic(self, mock_post):
        """Confirms the client reuses cached OAuth tokens instead of making redundant API calls."""
        # Setup mock network transaction feedback structure
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "access_token": "MOCK_BEARER_TOKEN_ABC123",
            "expires_in": 3600
        }
        mock_post.return_value = mock_response

        # Execute original token acquisition call
        token_one = self.client._get_valid_token()

        # Trigger follow-up check instantly within safe caching limits
        token_two = self.client._get_valid_token()

        self.assertEqual(token_one, "MOCK_BEARER_TOKEN_ABC123")
        self.assertEqual(token_two, "MOCK_BEARER_TOKEN_ABC123")
        # Assert that network layer execution occurred exactly once
        mock_post.assert_called_once()


class TestLocalStateLedger(unittest.TestCase):
    def setUp(self):
        # Instantiate a detached ledger configuration targeting a temporary test file path
        self.test_db_path = "test_ledger_mock.json"
        self.db = LocalStateLedger(self.test_db_path)

    def tearDown(self):
        # Clean up filesystem debris safely post testing validation runs
        import os
        if os.path.exists(self.test_db_path):
            os.remove(self.test_db_path)

    def test_log_and_volatility_calculation(self):
        """Validates append routines and history tracking loops."""
        record_one = {
            "invoice_id": "INV-001", "source_currency": "USD", "target_currency": "EUR",
            "source_amount": 100.0, "converted_amount": 92.0, "exchange_rate": 0.92
        }
        record_two = {
            "invoice_id": "INV-002", "source_currency": "USD", "target_currency": "EUR",
            "source_amount": 200.0, "converted_amount": 188.0, "exchange_rate": 0.94
        }

        self.db.log_transaction(record_one)
        self.db.log_transaction(record_two)

        # Expected mathematical mean: (0.92 + 0.94) / 2 = 0.93
        calculated_average = self.db.calculate_historical_volatility("USD", "EUR")
        self.assertAlmostEqual(calculated_average, 0.93, places=2)


if __name__ == '__main__':
    unittest.main()
