async def analyze_trade_with_ai(trade_data: dict, user_pubkey: str) -> str:
    """
    LangGraph / CrewAI decision workflow.
    Analyze trade risk, similarity to user's preferences, and profitability.
    Return "execute" or "skip".
    """
    # For MVP: simple rule-based decision
    if trade_data["asset"] == "SOL" and trade_data["price"] < 30:
        return "execute"
    return "skip"
