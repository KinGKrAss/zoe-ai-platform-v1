from .models import Claim


def verify_schema(claim: Claim) -> tuple[bool, list[str]]:
    reasons: list[str] = []
    if claim.wallet is None and claim.source == "rootstock":
        reasons.append("rootstock claim requires wallet data")
    if claim.wallet is not None and not claim.wallet.address.startswith("0x"):
        reasons.append("wallet address must be hexadecimal EVM address")
    return not reasons, reasons
