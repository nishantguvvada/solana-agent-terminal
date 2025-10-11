from pydantic import BaseModel
from borsh_construct import CStruct, U64, U8, Bool

class GlobalConfig(BaseModel):
    admin: str
    unique_key: str
    agent_fee_lamports: int

class UserAccount(BaseModel):
    user: str
    total_paid: int
    tasks_used: int
    tasks_remaining: int
    has_rated: bool

UserAccountLayout = CStruct(
    "user" / U8[32],
    "total_paid" / U64,
    "tasks_used" / U8,
    "tasks_remaining" / U8,
    "has_rated" / Bool,
)