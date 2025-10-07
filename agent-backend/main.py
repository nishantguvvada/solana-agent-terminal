from fastapi import FastAPI
from dotenv import load_dotenv
import uvicorn

app = FastAPI()

@app.get("/")
def default():
    return {"response": "on"}

# ON-CHAIN

@app.post("/deposit")
def deposit():
    return {"response": "deposit"}

@app.post("/execute-task")
def deposit():
    return {"response": "Deduct 1 task, trigger AI copy-trade"}

@app.get("/user-details")
def user_details():
    return {"response": "tasks remaining"}

# COPY TRADE

@app.post("/analyze-trade")
def analyze_trade():
    return {"response": "analyze_trade"}

# TRADE EXECUTION

@app.get("/trade-execute")
def trade_execute():
    return {"response": "tasks remaining"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)