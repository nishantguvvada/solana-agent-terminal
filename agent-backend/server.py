from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from anchor.client import build_deposit_tx, build_execute_task_tx
from dotenv import load_dotenv
import uvicorn
import os

load_dotenv()

app = FastAPI(title="Solana Agent Terminal Backend")

origins = [
    os.getenv("FRONTEND_URL") or "http://localhost:5173"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

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
    ix = await build_execute_task_tx(request.user_pubkey)
    return {"ix": ix}

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