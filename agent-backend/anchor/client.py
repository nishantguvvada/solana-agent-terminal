from solana.rpc.async_api import AsyncClient
from solders.pubkey import Pubkey
from models.schemas import UserAccountLayout
from anchorpy import Program, Provider, Wallet, Idl
import base64

# ----------------------------
# 1. Load Environment Variables
# ----------------------------
RPC_URL = "https://api.devnet.solana.com"  # devnet RPC
PROGRAM_ID = Pubkey.from_string("5xh8w4ihrnrzZo7F6tsdLXRpASTkdGYzfcMEja6vz7wX")  # Replace with your deployed program ID
IDL_PATH =  ".\\anchor\\idl.json"                      # Export this from Anchor build folder
SYS_PROGRAM_ID = Pubkey.from_string("11111111111111111111111111111111")

# ----------------------------
# 2. Load IDL / Program (No keypair needed anymore)
# ----------------------------
async def get_program():
    """
    Loads the Anchor program client with a dummy wallet (since backend never signs tx).
    """
    client = AsyncClient(RPC_URL)
    dummy_wallet = Wallet.local()
    provider = Provider(client, dummy_wallet)

    with open(IDL_PATH, "r") as f:
        idl = Idl.from_json(f.read())

    program = Program(idl, PROGRAM_ID, provider)
    return program

# ----------------------------
# 3. PDA Helpers
# ----------------------------
async def get_global_config_pda(admin_pubkey: str, unique_key: str):
    """Use correct PDA derivation as per your Anchor seeds """
    program = await get_program()
    pda, _ = Pubkey.find_program_address(
        [
            b"admin",
            bytes(unique_key, "utf-8"),
            bytes(Pubkey.from_string(admin_pubkey))
        ],
        program.program_id
    )
    return pda

async def get_user_account_pda(user_pubkey: str):
    """Derive user account PDA based on user's public key """
    program = await get_program()
    pda, _ = Pubkey.find_program_address(
        [
            b"user",
            bytes(Pubkey.from_string(user_pubkey))
        ],
        program.program_id
    )
    return pda

async def get_account_data(pubkey: Pubkey):
    """Fetch PDA account data based on PDA's public key"""

    client = AsyncClient(RPC_URL)
    info  = await client.get_account_info(pubkey=pubkey)
    print("INFO", info)
    account_info = info.value
    if not account_info or not account_info.data:
        print("❌ Account has no data or is uninitialized.")
        return None
    return account_info.data

def decode_user_account(data: bytes):
    """Decode raw on-chain data of UserAccount PDA"""
    obj = UserAccountLayout.parse(data)
    return {
        "user": str(Pubkey(obj.user)),
        "total_paid": obj.total_paid,
        "tasks_used": obj.tasks_used,
        "tasks_remaining": obj.tasks_remaining,
        "has_rated": bool(obj.has_rated),
    }

async def get_user_account_data(user_pubkey: str):
    user_account_pda = await get_user_account_pda(user_pubkey=user_pubkey)
    print("key", user_account_pda)
    data = await get_account_data(user_account_pda)

    if not data:
        print("No data found")
        return None

    decoded = decode_user_account(data)
    return decoded

# ----------------------------
# 4. Initialize Global Config
# ----------------------------
async def build_initialize_global_config_tx(admin_pubkey: str, unique_key: str, agent_fee_lamports: int):
    """
    Instead of calling RPC directly, build and return an unsigned transaction.
    This will be signed by the frontend admin wallet.
    """
    program = await get_program()
    global_config_pda = await get_global_config_pda(admin_pubkey=admin_pubkey, unique_key=unique_key)
    admin_publickey = Pubkey.from_string(admin_pubkey)

    ix = program.methods["initialize_global_config"].accounts(
        {
            "admin_account": admin_publickey,
            "global_config": global_config_pda,
            "system_program": SYS_PROGRAM_ID,
        }
    ).args([unique_key, agent_fee_lamports]).instruction()

    return {
        "program_id": str(ix.program_id),
        "keys": [
            {
                "pubkey": str(meta.pubkey),
                "is_signer": meta.is_signer,
                "is_writable": meta.is_writable
            }
            for meta in ix.accounts
        ],
        "data": base64.b64encode(bytes(ix.data)).decode("utf-8")
    }

# ----------------------------
# 6. User Deposit
# ----------------------------
async def build_deposit_tx(global_config_pda: str, user_pubkey: str, admin_pubkey: str, num_tasks: int):
    """Build an unsigned deposit transaction for the frontend to sign."""
    program = await get_program()
    global_config_pda = Pubkey.from_string(global_config_pda)
    user_publickey = Pubkey.from_string(user_pubkey)
    user_account_pda = await get_user_account_pda(user_pubkey)
    admin_publickey = Pubkey.from_string(admin_pubkey)


    ix = program.methods["user_deposit"].accounts(
        {
            "global_config": global_config_pda,
            "user_account": user_account_pda,
            "admin_account": admin_publickey,
            "user": user_publickey,
            "system_program": SYS_PROGRAM_ID,
        }
    ).args([num_tasks]).instruction()

    return  {
        "program_id": str(ix.program_id),
        "keys": [
            {
                "pubkey": str(meta.pubkey),
                "is_signer": meta.is_signer,
                "is_writable": meta.is_writable,
            }
            for meta in ix.accounts
        ],
        "data": base64.b64encode(bytes(ix.data)).decode("utf-8"),
    }

# ----------------------------
# 6. Build Execute Task Transaction
# ----------------------------
async def build_execute_task_tx(user_pubkey: str):
    """
    Prepare unsigned transaction to call `execute_task` instruction.
    """
    program = await get_program()
    user_publickey = Pubkey.from_string(user_pubkey)
    user_account_pda = await get_user_account_pda(user_pubkey)

    ix = program.methods["execute_task"].accounts(
        {
            "user_account": user_account_pda,
            "user": user_publickey,
            "system_program": SYS_PROGRAM_ID,
        }
    ).instruction()

    return  {
        "program_id": str(ix.program_id),
        "keys": [
            {
                "pubkey": str(meta.pubkey),
                "is_signer": meta.is_signer,
                "is_writable": meta.is_writable,
            }
            for meta in ix.accounts
        ],
        "data": base64.b64encode(bytes(ix.data)).decode("utf-8"),
    }

# ----------------------------
# 8. Withdraw (Admin only)
# ----------------------------
async def build_withdraw_tx(global_config_pda: str, admin_pubkey: str):
    """Same unsigned transaction pattern for withdraw """

    program = await get_program()
    global_config_pda = Pubkey.from_string(global_config_pda)
    admin_publickey = Pubkey.from_string(admin_pubkey)

    ix = program.methods["withdraw"].accounts(
        {
            "global_config": global_config_pda,
            "admin_account": admin_publickey,
        }
    ).instruction()

    return  {
        "program_id": str(ix.program_id),
        "keys": [
            {
                "pubkey": str(meta.pubkey),
                "is_signer": meta.is_signer,
                "is_writable": meta.is_writable,
            }
            for meta in ix.accounts
        ],
        "data": base64.b64encode(bytes(ix.data)).decode("utf-8"),
    }


# ----------------------------
# 9. Example Usage
# ----------------------------
if __name__ == "__main__":
    import asyncio

    async def main():
        # This is just an example. Normally, these functions are imported into FastAPI endpoints.
        program = await get_program()
        print("Program", program.program_id)

        global_config_pda = await get_global_config_pda("64axKE8skJrTkFrQZUUtLi4zGPg8cMasssDBh21L9bFf", "qwerty")
        print("Global Config", global_config_pda)

        user_account_pda = await get_user_account_pda("64axKE8skJrTkFrQZUUtLi4zGPg8cMasssDBh21L9bFf")
        print("User Account", user_account_pda)

        # info = await get_account_data(global_config_pda)
        # print("Global Config Data", info)

        # tx = await build_initialize_global_config_tx("7Y7c2jpw5BSbXzuEfRZwy9rQNSWyYzR2SanAX7ms4Ctb", "querty", 100)
        # print("TX", tx)

        # tx = await build_deposit_tx("DHRhJYTX62RysH7hSCWxKexPqAPB8XxMgaxfsgxyQDKL","7Y7c2jpw5BSbXzuEfRZwy9rQNSWyYzR2SanAX7ms4Ctb", "7Y7c2jpw5BSbXzuEfRZwy9rQNSWyYzR2SanAX7ms4Ctb", 5)
        # print("TX", tx)

        # tx = await build_execute_task_tx("7Y7c2jpw5BSbXzuEfRZwy9rQNSWyYzR2SanAX7ms4Ctb")
        # print("TX", tx)

        # tx = await build_withdraw_tx("AYsRc15PgqNv9ZP3MsfKKny6MGQWSas3gpURWfM4NJ4c","64axKE8skJrTkFrQZUUtLi4zGPg8cMasssDBh21L9bFf")
        # print("TX", tx)

        tx = await get_user_account_data("64axKE8skJrTkFrQZUUtLi4zGPg8cMasssDBh21L9bFf")
        print("TX", tx)


    asyncio.run(main())