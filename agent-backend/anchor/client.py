from solana.rpc.async_api import AsyncClient
from solders.pubkey import Pubkey
from solders.hash import Hash
from solders.message import Message
from solders.signature import Signature
from solders.transaction import VersionedTransaction, Transaction
from anchorpy import Program, Provider, Wallet, Idl
from base64 import b64encode
import base64

# ----------------------------
# 1. Load Environment Variables
# ----------------------------
RPC_URL = "https://api.devnet.solana.com"  # devnet RPC
PROGRAM_ID = Pubkey.from_string("9Bdw4evvdApf2Deb15LRVM5jyxn1CARxAL4Zakqgo8N1")  # Replace with your deployed program ID
IDL_PATH = ".\\anchor\\idl.json"                      # Export this from Anchor build folder
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
async def get_global_config_pda(admin_pubkey: str):
    """Use correct PDA derivation as per your Anchor seeds """
    program = await get_program()
    pda, _ = Pubkey.find_program_address(
        [bytes(Pubkey.from_string(admin_pubkey))],
        program.program_id
    )
    return pda

async def get_user_account_pda(user_pubkey: str):
    """Derive user account PDA based on user's public key """
    program = await get_program()
    pda, _ = Pubkey.find_program_address(
        [bytes(Pubkey.from_string(user_pubkey))],
        program.program_id
    )
    return pda

async def get_account_data(pubkey: Pubkey):
    """Fetch PDA account data based on PDA's public key"""

    client = AsyncClient(RPC_URL)
    account_info = await client.get_account_info(pubkey=pubkey)
    if account_info.value:
        return account_info.value.data
    return None


# ----------------------------
# 4. Initialize Global Config
# ----------------------------
async def build_initialize_global_config_tx(admin_pubkey: str, agent_fee_lamports: int):
    """
    Instead of calling RPC directly, build and return an unsigned transaction.
    This will be signed by the frontend admin wallet.
    """
    program = await get_program()
    global_config_pda = await get_global_config_pda(admin_pubkey)
    admin = Pubkey.from_string(admin_pubkey)

    ix = program.methods["initialize_global_config"].accounts(
        {
            "admin_account": Pubkey.from_string(admin_pubkey),
            "global_config": global_config_pda,
            "system_program": SYS_PROGRAM_ID,
        }
    ).args([agent_fee_lamports]).instruction()

    client = program.provider.connection
    blockhash_resp = await client.get_latest_blockhash()
    blockhash = blockhash_resp.value.blockhash

    message = Message.new_with_blockhash(
        [ix],  # list of instructions
        admin,   # fee payer
        blockhash
    )

    versioned_tx = VersionedTransaction.populate(message, [])
    tx_bytes = bytes(versioned_tx)

    return base64.b64encode(tx_bytes).decode("utf-8")

# ----------------------------
# 6. User Deposit
# ----------------------------
async def build_deposit_tx(user_pubkey: str, admin_pubkey: str, num_tasks: int):
    """Build an unsigned deposit transaction for the frontend to sign."""
    program = await get_program()
    global_config_pda = await get_global_config_pda(admin_pubkey)
    user_account_pda = await get_user_account_pda(user_pubkey)
    admin_publickey = Pubkey.from_string(admin_pubkey)
    user_publickey = Pubkey.from_string(user_pubkey)

    ix = program.methods["user_deposit"].accounts(
        {
            "global_config": global_config_pda,
            "user_account": user_account_pda,
            "admin_account": admin_publickey,
            "user": user_publickey,
            "system_program": SYS_PROGRAM_ID,
        }
    ).args([num_tasks]).instruction()

    client = program.provider.connection
    blockhash_resp = await client.get_latest_blockhash()
    blockhash = blockhash_resp.value.blockhash

    message = Message.new_with_blockhash(
        [ix],  # list of instructions
        user_publickey,   # fee payer
        blockhash
    )

    versioned_tx = VersionedTransaction.populate(message, [])
    tx_bytes = bytes(versioned_tx)

    return base64.b64encode(tx_bytes).decode("utf-8")

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

    client = program.provider.connection
    blockhash_resp = await client.get_latest_blockhash()
    blockhash = blockhash_resp.value.blockhash

    message = Message.new_with_blockhash(
        [ix],  # list of instructions
        user_publickey,   # fee payer
        blockhash
    )

    placeholder = Signature.default()
    versioned_tx = VersionedTransaction.populate(message, [placeholder])

    tx_bytes = bytes(versioned_tx)

    return base64.b64encode(tx_bytes).decode("utf-8")

# ----------------------------
# 8. Withdraw (Admin only)
# ----------------------------
async def build_withdraw_tx(admin_pubkey: str):
    """Same unsigned transaction pattern for withdraw """

    program = await get_program()
    global_config_pda = await get_global_config_pda(admin_pubkey)
    admin_publickey = Pubkey.from_string(admin_pubkey)

    ix = program.methods["withdraw"].accounts(
        {
            "global_config": global_config_pda,
            "admin_account": admin_publickey,
        }
    ).instruction()

    client = program.provider.connection
    blockhash_resp = await client.get_latest_blockhash()
    blockhash = blockhash_resp.value.blockhash

    message = Message.new_with_blockhash(
        [ix],  # list of instructions
        admin_publickey,   # fee payer
        blockhash
    )

    versioned_tx = VersionedTransaction.populate(message, [])
    tx_bytes = bytes(versioned_tx)

    return base64.b64encode(tx_bytes).decode("utf-8")

# ----------------------------
# 9. Example Usage
# ----------------------------
if __name__ == "__main__":
    import asyncio

    async def main():
        # This is just an example. Normally, these functions are imported into FastAPI endpoints.
        program = await get_program()
        print("Program", program.program_id)

        global_config_pda = await get_global_config_pda("64axKE8skJrTkFrQZUUtLi4zGPg8cMasssDBh21L9bFf")
        print("Global Config", global_config_pda)

        user_account_pda = await get_user_account_pda("7Y7c2jpw5BSbXzuEfRZwy9rQNSWyYzR2SanAX7ms4Ctb")
        print("User Account", user_account_pda)

        # info = await get_account_data(global_config_pda)
        # print("Global Config Data", info)

        # tx = await build_initialize_global_config_tx("7Y7c2jpw5BSbXzuEfRZwy9rQNSWyYzR2SanAX7ms4Ctb", 10000000)
        # print("TX", tx)

        # tx = await build_deposit_tx("7Y7c2jpw5BSbXzuEfRZwy9rQNSWyYzR2SanAX7ms4Ctb", "64axKE8skJrTkFrQZUUtLi4zGPg8cMasssDBh21L9bFf", 5)
        # print("TX", tx)

        tx = await build_execute_task_tx("7Y7c2jpw5BSbXzuEfRZwy9rQNSWyYzR2SanAX7ms4Ctb")
        print("TX", tx)

        # tx = await build_withdraw_tx("64axKE8skJrTkFrQZUUtLi4zGPg8cMasssDBh21L9bFf")
        # print("TX", tx)


    asyncio.run(main())