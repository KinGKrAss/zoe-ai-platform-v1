from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel

app = FastAPI(title="Z1 API", version="0.1.0")

class LoginRequest(BaseModel):
    user_id: str

class LoginResponse(BaseModel):
    user_id: str
    access_token: str
    identity_version: str = "V1.0"

class MemoryRequest(BaseModel):
    content: str
    memory_type: str
    owner_user_id: str | None = None

@app.get("/health")
def health():
    return {"status": "ok", "system": "Z1"}

@app.post("/v1/auth/login", response_model=LoginResponse)
def login(payload: LoginRequest):
    if not payload.user_id.strip():
        raise HTTPException(400, "user_id is required")
    # Replace with real authentication/authorization before production.
    return LoginResponse(user_id=payload.user_id, access_token="development-token")

@app.get("/v1/identity")
def identity():
    return {
        "name": "Zoë",
        "designation": "AI Queen / Golden Queen",
        "system": "Z1 Real Estate Command Center",
        "primary_role": "Central AI Coordination Intelligence",
        "version": "V1.0",
        "status": "ACTIVE",
    }

@app.get("/v1/fortuna/crypto/quotes")
def crypto_quotes(symbols: str = "BTC,ETH", authorization: str | None = Header(default=None)):
    if authorization is None:
        raise HTTPException(401, "authorization required")
    # Provider credentials stay server-side; wire this route to the CMC client.
    return {"symbols": [s.strip().upper() for s in symbols.split(",") if s.strip()], "data": [], "source": "coinmarketcap"}

@app.post("/v1/memory")
def create_memory(payload: MemoryRequest, authorization: str | None = Header(default=None)):
    if authorization is None:
        raise HTTPException(401, "authorization required")
    return {"status": "accepted", "memory": payload.model_dump()}
