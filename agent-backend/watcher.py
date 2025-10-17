import asyncio
import aiohttp # aiohttp is very efficient for persistent sessions.
from solana.rpc.async_api import AsyncClient
from solana.rpc.websocket_api import connect
from solders.pubkey import Pubkey
from websockets.exceptions import ConnectionClosedError

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

# -- TOKEN DETAILS --
async def get_token_accounts(wallet_pubkey: str):
    async with AsyncClient("https://api.devnet.solana.com") as client:
        resp = await client.get_token_accounts_by_owner(
            Pubkey.from_string(wallet_pubkey),
            program_id=Pubkey.from_string("TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA")
        )
        return [acc.pubkey for acc in resp.value]
    
async def watch_wallet_and_tokens(wallet_pubkey: str):
    token_accounts = await get_token_accounts(wallet_pubkey)
    print(f"Found {len(token_accounts)} token accounts")

    async with connect("wss://api.devnet.solana.com/") as websocket:
        # Subscribe to SOL balance changes
        await websocket.account_subscribe(Pubkey.from_string(wallet_pubkey))
        print(f"Subscribed to SOL account: {wallet_pubkey}")

        # Subscribe to all token accounts
        for token_acc in token_accounts:
            await websocket.account_subscribe(Pubkey.from_string(token_acc))
            print(f"Subscribed to token account: {token_acc}")

        async for msg in websocket:
            # Each msg is an update from one of the subscribed accounts
            if hasattr(msg, "params") and msg.params:
                account_data = msg.params.result.value.data
                owner = msg.params.result.value.owner
                print(f"📡 Update in program {owner}, base64: {account_data}")

# -- TOKEN DETAILS --

async def watch_wallet(target_wallet: str, user_pubkey: str):
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
    asyncio.run(watch_wallet(
        target_wallet="TARGET_KEY",
        user_pubkey="USER_KEY"
    ))