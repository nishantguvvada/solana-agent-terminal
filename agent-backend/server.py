from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from anchor.client import (
    build_deposit_tx, 
    build_execute_task_tx, 
    build_initialize_global_config_tx, 
    get_user_account_data,
    get_config_account_data
)
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

class AdminInitializeConfigRequest(BaseModel):
    admin_pubkey: str
    unique_key: str
    agent_fee_lamports: int

class AdminGetConfigRequest(BaseModel):
    config_pda_pubkey: str

class DepositRequest(BaseModel):
    user_pubkey: str
    num_tasks: int

class ExecuteTaskRequest(BaseModel):
    user_pubkey: str
    target_wallet: str

class UserDetailsRequest(BaseModel):
    user_pubkey: str

class TradeAnalysisRequest(BaseModel):
    trade_data: dict
    user_pubkey: str

# Endpoints

@app.get("/")
def default():
    return {"response": "on"}

# ON-CHAIN

@app.post("/initialize-config")
async def initialize_config(request: AdminInitializeConfigRequest):
    """
    Admin creates a `GlobalConfig`. This calls the Anchor `initialize_global_config` function.
    """
    ix = await build_initialize_global_config_tx(request.admin_pubkey, request.unique_key, request.agent_fee_lamports)
    return {"ix": ix}

@app.post("/get-config")
async def get_config(request: AdminGetConfigRequest):
    """
    Admin fetches the `GlobalConfig` for the provided PDA public key.
    """

    try:
        config_data = await get_config_account_data(request.config_pda_pubkey)
        if not config_data:
            raise HTTPException(status_code=404, detail="Config account not found")
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"{e}")

    return {"response": config_data}
    

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

@app.post("/user-details")
async def user_details(request: UserDetailsRequest):
    
    try:
        user_data = await get_user_account_data(request.user_pubkey)
        if not user_data:
            return HTTPException(status_code=404, detail="User account not found")
    except Exception as e:
        return HTTPException(status_code=404, detail=f"{e}")

    return {"response": user_data}

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