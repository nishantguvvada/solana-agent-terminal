import asyncio
import httpx
from typing import Dict

async def get_recent_trades(wallet: str) -> Dict:
    # TODO: Implement using Solana RPC or Helius API
    return {"asset": "SOL", "side": "buy", "amount": 1.2, "price": 25.5}

async def start_wallet_watcher(user_pubkey: str, target_wallet: str):
    """
    Starts tracking a wallet and triggers the AI agent whenever a new trade is detected.
    """
    max_tasks = 5  # TODO: Fetch from Anchor state if needed
    executed = 0

    while executed < max_tasks:
        trade = await get_recent_trades(target_wallet)
        if trade:
            async with httpx.AsyncClient() as client:
                res = await client.post(
                    "http://localhost:8000/agent/analyze-trade",
                    json={"trade_data": trade, "user_pubkey": user_pubkey}
                )
                decision = res.json().get("decision")

            if decision == "execute":
                print("[WATCHER] Executing trade on behalf of user...")
                # TODO: Call DEX API or Anchor execution program here

            executed += 1

        await asyncio.sleep(10)  # poll every 10s
