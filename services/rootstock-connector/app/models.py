from decimal import Decimal
from pydantic import BaseModel, ConfigDict, Field


class WalletBalance(BaseModel):
    model_config = ConfigDict(frozen=True)

    address: str
    balance_wei: int = Field(ge=0)
    balance_rbtc: Decimal
    block_number: int = Field(ge=0)
    chain_id: int = Field(ge=1)


class RpcError(BaseModel):
    code: int
    message: str


class RpcResponse(BaseModel):
    jsonrpc: str
    id: int | str
    result: object | None = None
    error: RpcError | None = None
