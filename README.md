# PayAgent.json — Autonomous AI Multi-Currency B2B Treasury Agent

Built exclusively for the **PayPal AI Hackathon 2026**.

## 🚀 Executive & Business Scope Summary

### The Multi-Billion Dollar Friction
Cross-border B2B procurement is the backbone of global supply chains, yet it remains riddled with transaction overhead. Moving corporate funds internationally demands manual intervention—calculating figures, looking up exchange rates, navigating compliance codes, and matching invoice balances. More critically, companies face extreme exposure to **Foreign Exchange (FX) market volatility**. A sudden currency split mid-transaction can shatter project margins.

### The Innovation
**PayAgent.json** solves this by putting **"AI behind the wheel"** of global enterprise payments. It translates messy, unstructured human text instructions (e.g., procurement goals or supplier emails) into secure cross-border payment pipelines. 

By integrating an automated **FX Volatility Guard** loop over secure **PayPal REST rails**, the agent intercepts transactions dynamically if currency variance slips past a safe 5% threshold—saving businesses thousands of dollars in hidden FX losses while eliminating manual billing entry completely.

---

## 🏗️ System Process & Runtime Workflow

The entire system processes user commands through an event-driven validation architecture:

## How it runs!!

[1. Messy User Prompt]  ──> "Secure 50 parts for a budget cap of 2500 USD in EUR"
│
▼
[2. AITreasuryAgent]    ──> Local AI extracts: Email, Volatility Caps, and ISO Currencies
│
▼
[3. FX Validation Guard]──> Reads current cross-rate, scans history ledger profiles
│
┌─────────────┴─────────────┐
▼ (Deviation > 5%)          ▼ (Safe Threshold)
[HALT & RISK ALERT]         [4. PayPal Token Cache Engine]
│
▼
[5. PayPal Invoicing V2 REST API]
│
▼
[6. Local Ledger Append Log]

## 📦 Modular Architecture & Component Mappings

The codebase follows an enterprise separation-of-concerns layout. Here is exactly what each module does:

### 1. `app/agent.py` (The Intelligent Parser Engine)
* **Purpose:** Functions as the local natural language processing (NLP) heart.
* **Logic:** Leverages local open-source models via the `ollama` framework. It uses a custom system prompt script running at zero temperature to extract parameters (target email, currencies, base amounts) deterministically.
* **Complexity:** Time Complexity maps at \(\mathcal{O}(M)\) where M is token density. Space Complexity tracks at \(\mathcal{O}(1)\).

### 2. `app/paypal_client.py` (The Secure Network Adapter)
* **Purpose:** Handles encrypted communications with the official PayPal Sandbox REST API environment.
* **Logic:** Interfaces directly with the `/v1/oauth2/token` and `/v2/invoicing/invoices` endpoints. Includes an embedded local memory expiration cache timer to prevent redundant authentication handshakes.
* **Complexity:** Time Complexity runs at uniform \(\mathcal{O}(1)\) for active cache retrievals.

### 3. `app/database.py` (The Persistent Ledger Machine)
* **Purpose:** Operates as an append-only JSON file engine serving as the agent's permanent memory.
* **Logic:** Securely writes payment metadata history records on local storage profiles and executes tracking computations to calculate baseline currency conversion means.
* **Complexity:** Writes track at \(\mathcal{O}(1)\) append speed; calculations scale at \(\mathcal{O}(K)\) relative to matching currency records.

### 4. `app/logger.py` (The Operational Monitor)
* **Purpose:** Employs rotating diagnostic streams (`app_execution.log`) to log system activities, response latencies, and execution halts cleanly.
### 5. `app/main.py` (The Core Pipeline Interceptor)
* **Purpose:** The centralized coordinator that loads environment configurations, invokes the agent, executes security checks, and calls the API adapter.

---

## 💻 Step-by-Step Execution Guide

### Prerequisites
* Python 3.10 or higher installed.
* [Ollama](https://ollama.com) running locally with the `mistral` model active (`ollama run mistral`).
* A valid PayPal Sandbox Merchant token profile.

### 1. Project Initialization & Dependency Build
```bash
# Clone the repository layout
git clone https://github.com
cd paypal-ai-agent

# Build your isolated virtual workspace environment
python3 -m venv venv
source venv/bin/activate

# Fetch the structural framework requirements
pip install -r requirements.txt
```

### 2. Configure Environment Parameters
Create a file named `.env` inside the root directory:
```text
PAYPAL_SANDBOX_CLIENT_ID=YOUR_ACTUAL_SANDBOX_CLIENT_ID
PAYPAL_SANDBOX_CLIENT_SECRET=YOUR_ACTUAL_SANDBOX_CLIENT_SECRET
```

### 3. Run the Production Pipeline
```bash
python -m app.main
```

### 4. Run the Unit Testing Architecture
```bash
python -m unittest discover -s tests
```
---

## 📊 Expected Operational Outputs

### Scenario A: Successful Pipeline Execution (Safe FX Conditions)
When you trigger the runtime pipeline under normal market conditions, the terminal parses the user request, catches credentials, validates live rates against the ledger file, and posts directly to PayPal:

```text
[2026-10-13 17:01:10] INFO [treasury_pipeline.run_treasury_pipeline:20] Initializing high-efficiency agent execution pipeline.
[2026-10-13 17:01:10] INFO [treasury_agent.parse_cross_border_intent:22] AI Treasury processing request payload...
[2026-10-13 17:01:11] INFO [paypal_client._get_valid_token:25] Access token missing or expired. Initializing sandbox OAuth2 handshake.
[2026-10-13 17:01:12] INFO [paypal_client.create_draft_invoice:52] Transmitting structured draft invoice payload configuration.

[+] Multi-Currency Transaction Securely Authorized!
[+] Operational Target: EUR | Execution Capital Allocation Total: 2300.00 EUR
[+] PayPal Target Reference ID: INV2-R57A-XXXX-XXXX-XXXX
[+] Operational state configuration variables preserved securely on local storage track records.
```

### Scenario B: Volatility Guard Triggered (High-Risk Market Shifts)
If a currency pair experiences an unexpected variance spike exceeding 5% compared to your historical `ledger.json` logs, the system halts the transfer to protect corporate funds:

```text
[2026-10-13 17:02:45] INFO [treasury_pipeline.run_treasury_pipeline:20] Initializing high-efficiency agent execution pipeline.
[2026-10-13 17:02:46] CRITICAL [treasury_pipeline.run_treasury_pipeline:42] Volatility exception threshold breached! Market variance hit 8.42%

[!] Risk Alert: Transaction halted. Current market variance drifts 8.42% from baseline ledger averages.
```

---

## ⚖️ License
Distributed openly under the terms of the MIT License. See `LICENSE` for more options.
