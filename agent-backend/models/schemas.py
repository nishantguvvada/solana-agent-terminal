from pydantic import BaseModel

class GlobalConfig(BaseModel):
    admin: str
    agent_fee_lamports: int

class UserAccount(BaseModel):
    user: str
    total_paid: int
    tasks_used: int
    tasks_remaining: int
    has_rated: bool