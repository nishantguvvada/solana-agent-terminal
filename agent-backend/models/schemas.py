from construct import Struct, Int64ul, Int32ul, Int8ul, Flag, Bytes

GlobalConfigLayout = Struct(
    "discriminator" / Bytes(8),
    "admin" / Bytes(32),
    "unique_key_len" / Int32ul,
    "unique_key" / Bytes(lambda ctx: ctx.unique_key_len),
    "agent_fee_lamports" / Int64ul
)

UserAccountLayout = Struct(
    "discriminator" / Bytes(8),
    "user" / Bytes(32),
    "total_paid" / Int64ul,
    "tasks_used" / Int8ul,
    "tasks_remaining" / Int8ul,
    "has_rated" / Flag,
)