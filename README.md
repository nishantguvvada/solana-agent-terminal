# 🧠 Solana Agent Terminal

Solana Agent Terminal is a decentralized platform that hosts multiple autonomous AI agents capable of performing on-chain tasks — from complex trade analysis to routine automation — for a fee. One such agent, TradeMaster AI, acts as a copy-trading bot that monitors wallet activity, analyzes trades, and mirrors strategies intelligently.

## TradeMaster AI

**TradeMaster AI** is an intelligent **copy trading bot** built on **Solana** that uses **on-chain monitoring** and **AI decision-making** to analyze and replicate trades automatically.

The system continuously watches a target wallet for token or SOL transfers, enriches each detected trade with token metadata and price data, and invokes an AI agent to decide whether to copy the trade on the user’s behalf.

---

## 🚀 Features

- 🔍 **On-chain Wallet Monitoring**
  - Uses Solana’s WebSocket API to listen for all token transfers related to a target wallet.
- 🧩 **Automatic Trade Context Enrichment**

  - Extracts metadata, token info, and prices for each transaction using Jupiter APIs.

- 🤖 **AI-Powered Trade Analysis**

  - Sends every detected trade to an LLM agent (LangGraph / CrewAI) that decides whether to copy or skip the trade.

- 💰 **Smart Copy Execution**

  - Executes trades only when the AI agent decides positively.
  - Limits total copied trades to a configurable threshold (default: 5).

- ⚡ **Async Architecture**
  - Built with `FastAPI` and `aiohttp` for high concurrency and minimal latency.

---

## 🧠 System Architecture

```

┌────────────────────────────┐
│ FastAPI App │
│ • /execute-task endpoint │
│ • /agent/analyze-trade │
│ • /trade-execute │
└────────────┬───────────────┘
│
▼
┌────────────────────────────┐
│ watcher.py │
│ • Watches target wallet │
│ • Fetches token metadata │
│ • Enriches trade context │
│ • Sends to AI Agent │
└────────────┬───────────────┘
│
▼
┌────────────────────────────┐
│ LangGraph / CrewAI │
│ • Analyzes trade intent │
│ • Decides BUY / SELL │
└────────────┬───────────────┘
│
▼
┌────────────────────────────┐
│ Trade Executor │
│ • Executes trade via API │
└────────────────────────────┘

```

---

## ⚙️ Installation & Setup

### 1️⃣ Clone the repository

```bash
git clone https://github.com/<your-username>/solana-agent-terminal.git
cd solana-agent-terminal
```

### 2️⃣ Create a virtual environment

```bash
python -m venv venv
source venv/bin/activate    # macOS/Linux
venv\Scripts\activate       # Windows
```

### 3️⃣ Install dependencies

```bash
pip install -r requirements.txt
```

### 4️⃣ Set environment variables

Create a `.env` file in the project root with:

```bash
RPC_URL=https://api.devnet.solana.com
AI_ANALYZE_ENDPOINT=http://localhost:8000/agent/analyze-trade
TRADE_EXEC_ENDPOINT=http://localhost:8000/trade-execute
```

### 5️⃣ Run the backend

```bash
uvicorn main:app --reload
```

### 6️⃣ Start watching a wallet

You can trigger the watcher via:

```bash
POST /execute-task
```

with JSON body:

```json
{
  "user_pubkey": "TARGET_WALLET_PUBLIC_KEY"
}
```

---

## 🧩 Key Files

| File                   | Description                                                             |
| ---------------------- | ----------------------------------------------------------------------- |
| **main.py**            | FastAPI entry point with endpoints for task execution and AI analysis.  |
| **watcher.py**         | Core watcher that subscribes to Solana logs and processes transactions. |
| **langgraph_agent.py** | Contains the AI workflow that evaluates trade intent.                   |
| **schemas.py**         | Pydantic models for request validation.                                 |

---

## 🧠 How It Works (Simplified Flow)

1. User calls `/execute-task` → starts a background watcher.
2. `watcher.py` subscribes to Solana logs using WebSockets.
3. When a transaction is detected, it:

   - Fetches parsed transaction data.
   - Extracts token metadata & price.
   - Determines trade direction (buy/sell).

4. Sends enriched trade context to `/agent/analyze-trade`.
5. The **AI agent** analyzes the trade and returns a decision.
6. If the decision is positive → watcher triggers `/trade-execute` to copy the trade.
7. Stops after **5 successful AI trades**.

---

## 🧠 Example Trade Context

```json
{
  "type": "transferChecked",
  "program": "spl-token",
  "mint": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
  "token": "USDC",
  "name": "USD Coin",
  "amount": 5.0,
  "price_usd": 1.0,
  "direction": "buy"
}
```

---

## 🧪 Roadmap

- [ ] Add multi-wallet monitoring
- [ ] Support for DEX-based swaps
- [ ] Extend AI logic for market condition analysis
- [ ] Add user dashboard (Next.js frontend)
- [ ] Deploy on mainnet-beta

---

## 🛠️ Tech Stack

- **Python 3.10+**
- **FastAPI**
- **aiohttp**
- **solana-py**
- **LangGraph**
- **Jupiter API**

---

## 🧑‍💻 Author

**Nishant Guvvada**
Blockchain & AI Engineer
🔗 [GitHub](https://github.com/nishantguvvada) • [Gmail](nishant.guvvada@gmail.com) • [LinkedIn](https://www.linkedin.com/in/nishant-guvvada-36647289/)

---

## 🪙 License

This project is licensed under the **MIT License**.
See [LICENSE](./LICENSE) for details.

```

```
