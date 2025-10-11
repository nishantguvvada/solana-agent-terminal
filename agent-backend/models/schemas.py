from pydantic import BaseModel
from construct import Struct, Int64ul, Int8ul, Flag, Bytes

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

UserAccountLayout = Struct(
    "discriminator" / Bytes(8),
    "user" / Bytes(32),
    "total_paid" / Int64ul,
    "tasks_used" / Int8ul,
    "tasks_remaining" / Int8ul,
    "has_rated" / Flag,
)