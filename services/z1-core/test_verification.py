from verification import CheckStatus, VerificationCheck, VerificationState, derive_verification_state


def test_all_required_checks_pass_is_verified():
    checks = [VerificationCheck("address", CheckStatus.PASS), VerificationCheck("rpc", CheckStatus.PASS)]
    result = derive_verification_state(checks)
    assert result.state is VerificationState.VERIFIED
    assert result.score == 100


def test_pending_check_prevents_green_state():
    checks = [VerificationCheck("address", CheckStatus.PASS), VerificationCheck("rpc", CheckStatus.PENDING)]
    result = derive_verification_state(checks)
    assert result.state is VerificationState.PENDING
    assert result.score == 50


def test_required_failure_is_failed():
    checks = [VerificationCheck("address", CheckStatus.PASS), VerificationCheck("rpc", CheckStatus.FAIL)]
    result = derive_verification_state(checks)
    assert result.state is VerificationState.FAILED


def test_optional_failure_does_not_block_verified_state():
    checks = [
        VerificationCheck("address", CheckStatus.PASS),
        VerificationCheck("nft", CheckStatus.FAIL, required=False),
    ]
    result = derive_verification_state(checks)
    assert result.state is VerificationState.VERIFIED
    assert result.score == 100


def test_blocked_wins_over_checks():
    checks = [VerificationCheck("address", CheckStatus.PASS)]
    result = derive_verification_state(checks, blocked=True)
    assert result.state is VerificationState.BLOCKED
    assert result.score == 0
