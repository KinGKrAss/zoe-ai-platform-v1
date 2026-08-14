from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class Principal:
    sub: str
    role: str
    scopes: frozenset[str]
    device_id: str | None = None


ROLE_SCOPES: dict[str, frozenset[str]] = {
    "OPERATOR": frozenset({"READ", "ANALYZE"}),
    "ANALYST": frozenset({"READ", "ANALYZE", "WRITE_NOTES"}),
    "ADMIN": frozenset({"READ", "ANALYZE", "WRITE", "ADMIN"}),
    "KI-SYSTEM": frozenset({"ZOEREAD", "ZOEANALYZE", "ZOEWRITEMEMORY"}),
}


def authorize(principal: Principal, required_scopes: set[str]) -> None:
    missing = required_scopes - principal.scopes
    if missing:
        raise PermissionError(f"missing scopes: {sorted(missing)}")


def principal_from_claims(claims: dict[str, Any]) -> Principal:
    role = str(claims.get("role", ""))
    if role not in ROLE_SCOPES:
        raise PermissionError("unknown role")
    scopes = frozenset(str(s) for s in claims.get("scopes", []))
    effective = scopes & ROLE_SCOPES[role]
    return Principal(
        sub=str(claims["sub"]),
        role=role,
        scopes=effective,
        device_id=claims.get("device_id"),
    )
