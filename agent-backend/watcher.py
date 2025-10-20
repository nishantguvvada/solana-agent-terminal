import asyncio
import aiohttp # aiohttp is very efficient for persistent sessions.
from solana.rpc.async_api import AsyncClient
from solana.rpc.websocket_api import connect, RpcTransactionLogsFilterMentions
from solders.pubkey import Pubkey
from websockets.exceptions import ConnectionClosedError
import base64
import json

AI_ANALYZE_ENDPOINT = "http://localhost:8000/agent/analyze-trade"
TRADE_EXEC_ENDPOINT = "http://localhost:8000/trade-execute"

async def sent_trade_to_agent(trade_data: dict, user_pubkey: str):
    """
    Calls backend /agent/analyze-trade endpoint for AI analysis.
    """
    # async with aiohttp.ClientSession() as session:
    #     async with session.post(AI_ANALYZE_ENDPOINT, json={
    #         "trade_data": trade_data,
    #         "user_pubkey": user_pubkey
    #     }) as response:
    #         return await response.json()
    return {"response":"Copy"}
        
async def execute_trade():
    async with aiohttp.ClientSession() as session:
        async with session.get(TRADE_EXEC_ENDPOINT) as response:
            return await response.json()

async def process_log_notification(msg, wallet_pubkey):
    if not hasattr(msg, "result") or not hasattr(msg.result, "value"):
        return

    value = msg.result.value
    signature = getattr(value, "signature", None)
    logs = getattr(value, "logs", [])
    err = getattr(value, "err", None)

    if err:
        print(f"Transaction failed: {signature}")
        return
    
    print(f"\nNew Transaction Detected:")
    print(f"Signature: {signature}")
    print(f"Logs:")
    for line in logs:
        print(f"   {line}")

    if any("Transfer" in line or "TransferChecked" in line for line in logs):
        print("Detected Token Transfer")

        # Send to AI agent for analysis
        trade_data = {
            "wallet": wallet_pubkey,
            "signature": signature,
            "logs": logs,
        }

        print(trade_data)

async def watch_wallet_and_tokens(target_wallet: str):
    """
    Watches the given wallet using Solana WebSocket RPC.
    When a new transaction is detected, the watcher sends it to our backend for AI analysis.
    """

    async with connect("wss://api.devnet.solana.com") as websocket:
        # Subscribe to all logs mentioning target_wallet
        # "mentions" filters logs that involve a specific address
        await websocket.logs_subscribe(RpcTransactionLogsFilterMentions(Pubkey.from_string(target_wallet)))
        print(f"Watching wallet {target_wallet} for trade activity...")

        async for msg in websocket:

            try:
                if isinstance(msg, list):
                    for single_msg in msg:
                        await process_log_notification(single_msg, target_wallet)
                else:
                    await process_log_notification(msg, target_wallet)

            except ConnectionClosedError:
                print("Connection lost — reconnecting in 5s...")
                await asyncio.sleep(5)

            except Exception as e:
                print(f"Watcher error: {e}")
                await asyncio.sleep(5)

async def watch_wallet_and_sol_transfer(target_wallet: str, user_pubkey: str):
    """
    Watches the given wallet using Solana WebSocket RPC.
    When a new transaction is detected, the watcher sends it to our backend for AI analysis.
    """
    print(f"Watching wallet {target_wallet} for trade activity...")

    async with connect("wss://api.devnet.solana.com/") as websocket:

        await websocket.account_subscribe(Pubkey.from_string(target_wallet))
        print("Subscription established")

        async for msg in websocket:
            try:
                if isinstance(msg, list):
                    msg = msg[0]

                if hasattr(msg, "result") and not hasattr(msg.result, "value"):
                    print("Subscription confirmed.")
                    continue

                if hasattr(msg, "result") and hasattr(msg.result, "value"):
                    data = msg.result.value.data
                    lamports = msg.result.value.lamports
                    print(f"Account change detected for {target_wallet}")
                    print(f"Raw Data: {data}")
                    print(f"Lamports: {lamports}")

                    trade_data = {
                        "wallet": target_wallet,
                        "raw_data": str(data)
                    }

                    response = await sent_trade_to_agent(trade_data, user_pubkey)
                    print(f"AI Agent Response: {response}")

                    decision = response.get("response")
                    if decision.lower() == "copy":
                        print(f"Triggering trade execution: {decision}")
                else:
                    print(f"Ignored message type: {msg}")

            except ConnectionClosedError:
                print("Connection lost — reconnecting in 5s...")
                await asyncio.sleep(5)

            except Exception as e:
                print(f"Watcher error: {e}")
                await asyncio.sleep(5)

if __name__ == "__main__":
    # asyncio.run(watch_wallet(
    #     target_wallet="TARGET_KEY",
    #     user_pubkey="USER_KEY"
    # ))

    print(asyncio.run(watch_wallet_and_tokens("TARGET_PUBLICKEY")))