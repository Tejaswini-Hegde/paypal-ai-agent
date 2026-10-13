import json
import ollama
from app.logger import setup_logger

logger = setup_logger("treasury_agent")

class AITreasuryAgent:
    def __init__(self):
        self.model_name = "mistral"  # Free local language model running via Ollama framework

    def parse_cross_border_intent(self, user_prompt: str) -> dict:
        """
        Uses a local LLM to reason through financial constraints and calculate currency schemas.
        Time Complexity: O(M) where M corresponds to total user input character sequence space.
        Space Complexity: O(1) constant state tracking variables.
        """
        logger.info(f"AI Treasury processing request payload: '{user_prompt}'")

        system_instructions = (
            "You are a professional multi-currency B2B Treasury Agent running on PayPal rails.\n"
            "Your task is to analyze user prompts, extract target financial figures, "
            "identify the required ISO-4217 currency codes (e.g., USD, EUR, GBP, INR, CAD), "
            "and map out the billing line items.\n\n"
            "Respond ONLY with a valid, raw JSON object matching this schema. Do not wrap it in markdown markdown code blocks:\n"
            "{\n"
            '  "action": "CREATE_INVOICE",\n'
            '  "recipient": "email@example.com",\n'
            '  "target_currency": "EUR",\n'
            '  "source_budget_cap": "2500.00",\n'
            '  "source_currency": "USD",\n'
            '  "item_name": "Office Chairs Supply",\n'
            '  "quantity": "50"\n'
            "}\n"
        )

        try:
            response = ollama.generate(
                model=self.model_name,
                system=system_instructions,
                prompt=user_prompt,
                options={"temperature": 0.0}  # Fixed zero temperature ensures stable, reproducible processing outcomes
            )

            raw_output = response['response'].strip()
            logger.info(f"Raw structured inference text block received from model: {raw_output}")
            return json.loads(raw_output)

        except Exception as error:
            logger.error(f"Inference failure encountered in local LLM compilation chain: {error}")
            return {"action": "FAILED", "reason": str(error)}
