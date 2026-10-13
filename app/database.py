import json
import os
import time
from app.logger import setup_logger

logger = setup_logger("database_engine")

class LocalStateLedger:
    def __init__(self, storage_path: str = "ledger.json"):
        self.storage_path = storage_path
        if not os.path.exists(self.storage_path):
            with open(self.storage_path, "w") as file:
                json.dump([], file)
            logger.info(f"Initialized blank tracking document repository at: {self.storage_path}")

    def log_transaction(self, transaction_record: dict) -> bool:
        """
        Appends transactional payload records cleanly to disk storage mapping configurations.
        Time Complexity: O(N) where N corresponds to absolute historic file density sizing.
        """
        try:
            with open(self.storage_path, "r") as file:
                history = json.load(file)

            transaction_record["timestamp"] = time.time()
            history.append(transaction_record)

            with open(self.storage_path, "w") as file:
                json.dump(history, file, indent=2)

            logger.info(f"Transaction successfully tracked under tracking ID index: {transaction_record.get('invoice_id')}")
            return True
        except Exception as error:
            logger.error(f"Failed to record state execution change event inside storage document: {error}")
            return False

    def calculate_historical_volatility(self, source_currency: str, target_currency: str) -> float:
        """
        Scans ledger state arrays to calculate target baseline conversion values.
        Time Complexity: O(K) where K represents localized historical record instances.
        """
        try:
            with open(self.storage_path, "r") as file:
                history = json.load(file)

            matching_rates = [
                record["exchange_rate"] for record in history
                if record.get("source_currency") == source_currency and record.get("target_currency") == target_currency
            ]

            if not matching_rates:
                return 0.0

            return sum(matching_rates) / len(matching_rates)
        except Exception as error:
            logger.error(f"Could not compute historical treasury metrics: {error}")
            return 0.0
