def deposit_sol(user_pubkey: str, num_tasks: int) -> str:
    """
    Call `user_deposit` instruction in Anchor.
    """
    # TODO: Use solana-py or custom RPC client here
    print(f"[ANCHOR] Depositing for {num_tasks} tasks from {user_pubkey}")
    return "tx_signature_dummy"

def execute_anchor_task(user_pubkey: str) -> str:
    """
    Call `execute_task` instruction in Anchor.
    """
    print(f"[ANCHOR] Executing task for {user_pubkey}")
    return "tx_signature_dummy"
