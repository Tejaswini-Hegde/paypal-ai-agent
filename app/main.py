import os
import sys
from dotenv import load_dotenv
from app.agent import AITreasuryAgent
from app.paypal_client import PayPalSandboxClient
from app.database import LocalStateLedger
from app.logger import setup_logger

load_dotenv()
logger = setup_logger("treasury_pipeline")

def fetch_live_exchange_rate(source: str, target: str) -> float:
    """Simulates real-world live multi-currency currency valuation updates."""
    mock_rates = {
        ("USD", "EUR"): 0.92, ("USD", "GBP"): 0.77,
        ("USD", "INR"): 84.00, ("USD", "USD"): 1.00
    }
    return mock_rates.get((source, target), 1.00)

def run_treasury_pipeline(user_command: str):
    logger.info("Initializing high-efficiency agent execution pipeline.")

    client_id = os.getenv("PAYPAL_SANDBOX_CLIENT_ID")
    client_secret = os.getenv("PAYPAL_SANDBOX_CLIENT_SECRET")

    if not client_id or not client_secret:
        logger.critical("Aborting: Critical developer key mappings missing from system environment configurations.")
        sys.exit(1)

    try:
        db = LocalStateLedger()
        agent = AITreasuryAgent()

        intent = agent.parse_cross_border_intent(user_command)
        if intent.get("action") != "CREATE_INVOICE":
            print(f"[-] Execution Terminated: Non-compatible execution intent detected.")
            return

        src_curr = intent["source_currency"].upper()
        tgt_curr = intent["target_currency"].upper()
        budget_cap = float(intent["source_budget_cap"])

        live_rate = fetch_live_exchange_rate(src_curr, tgt_curr)
        historical_average = db.calculate_historical_volatility(src_curr, tgt_curr)

        # Volatility Guard Algorithm Check
        if historical_average > 0.0:
            deviation = abs(live_rate - historical_average) / historical_average
            if deviation > 0.05:
                logger.critical(f"Volatility exception threshold breached! Market variance hit {deviation*100:.2f}%")
                print(f"\n[!] Risk Alert: Transaction halted. Current market variance drifts {deviation*100:.1f}% from baseline ledger averages.")
                return

        converted_total = budget_cap * live_rate

        paypal_payload = {
            "detail": {
                "currency_code": tgt_curr,
                "note": f"Cross-Border Procurement via AI Treasury Agent. Base Budget: {budget_cap} {src_curr}."
            },
            "primary_recipients": [{"billing_info": {"email_address": intent["recipient"]}}],
            "items": [{
                "name": intent["item_name"],
                "quantity": intent["quantity"],
                "unit_amount": {
                    "currency_code": tgt_curr,
                    "value": f"{converted_total / float(intent['quantity']):.2f}"
                }
            }]
        }

        paypal = PayPalSandboxClient(client_id, client_secret)
        result = paypal.create_draft_invoice(paypal_payload)

        if "error" in result:
            print(f"[-] PayPal API Registry Processing Refusal: {result['error']}")
        else:
            invoice_id = result.get('id')
            print(f"\n[+] Multi-Currency Transaction Securely Authorized!")
            print(f"[+] Operational Target: {tgt_curr} | Execution Capital Allocation Total: {converted_total:.2f} {tgt_curr}")
            print(f"[+] PayPal Target Reference ID: {invoice_id}")

            db.log_transaction({
                "invoice_id": invoice_id, "source_currency": src_curr, "target_currency": tgt_curr,
                "source_amount": budget_cap, "converted_amount": converted_total,
                "exchange_rate": live_rate, "status": "DRAFT_RECORDED"
            })
            print("[+] Operational state configuration variables preserved securely on local storage track records.\n")

    except Exception as runtime_error:
        logger.exception(f"Fatal error encountered inside processing thread execution loop: {runtime_error}")

if __name__ == "__main__":
    sample_complex_prompt = (
        "Send an invoice request to supplier@euro-distribution.com for 50 custom parts. "
        "The overall project budget limit is 2500 USD, but convert the final execution balance "
        "into EUR dynamically to match their standard local compliance requirements."
    )
    run_treasury_pipeline(sample_complex_prompt)
