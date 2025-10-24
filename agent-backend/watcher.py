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

async def sent_trade_to_agent(trade_data: dict):
    """
    Calls backend /agent/analyze-trade endpoint for AI analysis.
    """
    async with aiohttp.ClientSession() as session:
        async with session.post(AI_ANALYZE_ENDPOINT, json={
            "trade_data": trade_data
        }) as response:
            output = await response.json()
            print("RESPONSE:", output)
            return await response.json()
        
async def execute_trade():
    async with aiohttp.ClientSession() as session:
        async with session.get(TRADE_EXEC_ENDPOINT) as response:
            return await response.json()
        
async def get_token_metadata(mint):
    async with aiohttp.ClientSession() as session:
        async with session.get(f"https://lite-api.jup.ag/tokens/v2/search?query=usdc") as resp:
            tokens = await resp.json()
            token_details = tokens[0]
            return {
                "id": token_details.get("id", "UNKNOWN"), 
                "name": token_details.get("name", "UNKNOWN"), 
                "symbol": token_details.get("symbol", "UNKNOWN"), 
                "totalSupply": token_details.get("totalSupply", 0), 
                "liquidity": token_details.get("liquidity", 0)
            }
    return {
        "id": "UNKNOWN", 
        "name": "UNKNOWN", 
        "symbol": "UNKNOWN", 
        "totalSupply": 0, 
        "liquidity": 0
    }

async def get_token_price(symbol):
    async with aiohttp.ClientSession() as session:
        url = f"https://lite-api.jup.ag/price/v3?ids=EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"
        async with session.get(url) as resp:
            data = await resp.json()
            return data.get("EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v", {})
        
async def enrich_trade_context(tx, target_wallet):
    """Extract structured trade info from parsed transaction."""

    transaction = tx.get("transaction", {})
    message = transaction.get("message", {})
    meta = transaction.get("meta", {})

    instructions = message.get("instructions", [])

    trades = []
    for ix in instructions:
        parsed = ix.get("parsed", {})
        if not parsed:
            continue

        info = parsed.get("info", {})
        mint = info.get("mint")
        program = ix.get("program")
        tx_type = parsed.get("type")

        amount = (
            info.get("tokenAmount", {}).get("uiAmount")
            or info.get("amount")
            or info.get("uiAmountString")
        )

        if not mint:
            continue

        token_meta = await get_token_metadata(mint)
        price_info = await get_token_price(token_meta.get("id"))

        pre_balances = meta.get("preTokenBalances", [])
        print("PRE: ", pre_balances)
        post_balances = meta.get("postTokenBalances", [])
        print("POST: ", post_balances)

        direction = "unknown"
        for pre, post in zip(pre_balances, post_balances):
            owner = pre.get("owner")
            if owner == target_wallet:
                pre_amt = float(pre["uiTokenAmount"].get("uiAmount") or 0)
                post_amt = float(post["uiTokenAmount"].get("uiAmount") or 0)
                if post_amt > pre_amt:
                    direction = "buy"
                elif post_amt < pre_amt:
                    direction = "sell"
                break

        trades.append({
            "type": tx_type,
            "program": program,
            "mint": mint,
            "token": token_meta.get("symbol"),
            "name": token_meta.get("name"),
            "amount": amount,
            "price_usd": price_info.get("usdPrice"),
            "direction": direction,
        })

    return trades

async def fetch_parsed_transaction(signature: str):
    async with AsyncClient("https://api.devnet.solana.com") as client:
        resp = await client.get_transaction(signature, encoding="jsonParsed")
        return resp.value

async def process_log_notification(msg, wallet_pubkey, ai_trigger_count):
    if not hasattr(msg, "result") or not hasattr(msg.result, "value"):
        return ai_trigger_count

    value = msg.result.value
    signature = getattr(value, "signature", None)
    logs = getattr(value, "logs", [])
    err = getattr(value, "err", None)

    if err:
        print(f"Transaction failed: {signature}")
        return ai_trigger_count
    
    print(f"\nNew Transaction Detected:")
    print(f"Signature: {signature}")

    tx = await fetch_parsed_transaction(signature)
    if not tx:
        return ai_trigger_count
    
    tx_json = json.loads(tx.to_json()) if hasattr(tx, "to_json") else json.loads(tx.to_json_string())

    trade_context = await enrich_trade_context(tx_json, wallet_pubkey)
    print("Trade context:", trade_context)

    print(f"Logs:")
    for line in logs:
        print(f"   {line}")

    if any("Transfer" in line or "TransferChecked" in line for line in logs):
        print("Detected Token Transfer")

        # Send to AI agent for analysis
        trade_data = {
            "wallet": wallet_pubkey,
            "logs": logs,
            "trade_context": trade_context[0]
        }

        print(trade_data)

        ai_response = await sent_trade_to_agent(trade_data)
        print("AI JUDGEMENT: ", ai_response)
        if ai_response:
            ai_trigger_count += 1
            print(f"AI triggered {ai_trigger_count}/5 times")

    return ai_trigger_count

async def watch_wallet_and_tokens(target_wallet: str):
    """
    Watches the given wallet using Solana WebSocket RPC.
    When a new transaction is detected, the watcher sends it to our backend for AI analysis.
    """
    ai_trigger_count = 0

    async with connect("wss://api.devnet.solana.com") as websocket:
        # Subscribe to all logs mentioning target_wallet
        # "mentions" filters logs that involve a specific address
        await websocket.logs_subscribe(RpcTransactionLogsFilterMentions(Pubkey.from_string(target_wallet)))
        print(f"Watching wallet {target_wallet} for trade activity...")

        async for msg in websocket:

            try:
                if ai_trigger_count >= 5:
                    print("✅ Reached AI trigger limit (5). Stopping watcher.")
                    break

                if isinstance(msg, list):
                    for single_msg in msg:
                        ai_trigger_count = await process_log_notification(single_msg, target_wallet, ai_trigger_count)
                else:
                    ai_trigger_count = await process_log_notification(msg, target_wallet, ai_trigger_count)

            except ConnectionClosedError:
                print("Connection lost — reconnecting in 5s...")
                await asyncio.sleep(5)

            # except Exception as e:
            #     print(f"Watcher error: {e}")
            #     await asyncio.sleep(5)

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

    print(asyncio.run(watch_wallet_and_tokens("64axKE8skJrTkFrQZUUtLi4zGPg8cMasssDBh21L9bFf")))