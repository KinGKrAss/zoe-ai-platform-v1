from __future__ import annotations

import base64
import hashlib
import time
from pathlib import Path

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from app.tokenomics import TokenomicsManager


YAML_TEMPLATE = """version: \"1.0.0\"
token:
  name: \"Preussen Point\"
  symbol: \"PPT\"
  decimals: 18
  initial_supply_wei: \"0\"
collateral:
  reserve_currency: \"EUR\"
  reserve_unit: \"cent\"
  min_collateral_ratio_e18: \"1000000000000000000\"
  target_collateral_ratio_e18: \"{target_ratio}\"
limits:
  max_daily_mint_bps: 200
  max_daily_redeem_outflow_bps: 1000
fees:
  mint_fee_bps: 10
  redeem_fee_bps: 20
  allocation_bps:
    safety_reserve: 7000
    operations: 2000
    ecosystem: 1000
risk_controls:
  peg_deviation_threshold_bps: 200
  reserve_staleness_max_seconds: 3600
  oracle_staleness_max_seconds: 300
  circuit_breaker_enabled: true
  guarded_redeem_mode_enabled: true
api:
  require_jwt: true
  require_idempotency_on_write: true
  rate_limit:
    write_per_minute: 60
governance:
  timelock_seconds: 86400
  emergency_pause_allowed: true
"""


def write_signed_bundle(tmp_path: Path, private_key: Ed25519PrivateKey, *, target_ratio: str) -> tuple[Path, Path, Path, Path]:
    config_path = tmp_path / "parameters-v1.0.yaml"
    sha_path = tmp_path / "parameters-v1.0.sha256"
    signature_path = tmp_path / "parameters-v1.0.sig"
    public_key_path = tmp_path / "parameters-v1.0.pub"

    payload = YAML_TEMPLATE.format(target_ratio=target_ratio).encode("utf-8")
    config_path.write_bytes(payload)

    sha_path.write_text(f"{hashlib.sha256(payload).hexdigest()}  parameters-v1.0.yaml\n", encoding="utf-8")

    signature = private_key.sign(payload)
    signature_path.write_text(base64.b64encode(signature).decode("utf-8") + "\n", encoding="utf-8")

    public_key = private_key.public_key().public_bytes_raw()
    public_key_path.write_text(base64.b64encode(public_key).decode("utf-8") + "\n", encoding="utf-8")

    return config_path, sha_path, signature_path, public_key_path


def test_tokenomics_hot_reload_and_last_known_good_fallback(tmp_path: Path):
    private_key = Ed25519PrivateKey.generate()
    config_path, sha_path, sig_path, pub_path = write_signed_bundle(
        tmp_path, private_key, target_ratio="1050000000000000000"
    )

    manager = TokenomicsManager(
        config_path=config_path,
        sha256_path=sha_path,
        signature_path=sig_path,
        public_key_path=pub_path,
        enforce_integrity=True,
    )
    manager.load_initial()
    manager.start_watcher(poll_interval_seconds=0.05, debounce_seconds=0.05)

    write_signed_bundle(tmp_path, private_key, target_ratio="1100000000000000000")
    for _ in range(40):
        if manager.current().raw.collateral.target_collateral_ratio_e18 == "1100000000000000000":
            break
        time.sleep(0.05)

    assert manager.current().raw.collateral.target_collateral_ratio_e18 == "1100000000000000000"

    config_path.write_text("version: 1\n", encoding="utf-8")
    for _ in range(40):
        events = manager.audit_events()
        if any(event["event"] == "tokenomics_reload_failed" for event in events):
            break
        time.sleep(0.05)

    assert manager.current().raw.collateral.target_collateral_ratio_e18 == "1100000000000000000"
    assert any(event["event"] == "tokenomics_reload_failed" for event in manager.audit_events())

    manager.close()
