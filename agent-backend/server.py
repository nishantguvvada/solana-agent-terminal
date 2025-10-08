from fastapi import FastAPI, BackgroundTasks, HTTPException
from pydantic import BaseModel
from anchor.client import build_deposit_tx
from dotenv import load_dotenv
import uvicorn

app = FastAPI(title="Solana Agent Terminal Backend")

# Request Models

class DepositRequest(BaseModel):
    user_pubkey: str
    num_tasks: int

class ExecuteTaskRequest(BaseModel):
    user_pubkey: str
    target_wallet: str

class TradeAnalysisRequest(BaseModel):
    trade_data: dict
    user_pubkey: str

# Endpoints

@app.get("/")
def default():
    return {"response": "on"}

# ON-CHAIN

@app.post("/deposit")
async def deposit(request: DepositRequest):
    """
    User pays SOL to buy tasks. This calls the Anchor `user_deposit` function.
    """
    serialized_tx = await build_deposit_tx(request.user_pubkey, request.num_tasks)
    return {"response": {"transaction": serialized_tx}}

@app.post("/execute-task")
async def execute_task(request: ExecuteTaskRequest, background_tasks: BackgroundTasks):
    """
    Starts the copy-trade watcher.
    The watcher listens for trades from `target_wallet` and triggers AI agent analysis.
    """
    return {"response": "Deduct 1 task, trigger AI copy-trade"}

@app.get("/user-details")
def user_details():
    return {"response": "tasks remaining"}

# COPY TRADE

@app.post("/agent/analyze-trade")
def analyze_trade(request: TradeAnalysisRequest):
    """
    INTERNAL endpoint: Called by watcher when a trade is detected.
    Runs AI agent workflow (LangGraph / CrewAI) and returns decision.
    """
    return {"response": "analyze trade"}

# TRADE EXECUTION

@app.get("/trade-execute")
def trade_execute():
    return {"response": "trade execution"}


if __name__ == "__main__":
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)