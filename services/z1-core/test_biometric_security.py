from biometric_security import (
    BiometricDecision,
    BiometricModality,
    BiometricPolicy,
    BiometricPolicyEngine,
    BiometricPurpose,
    BiometricRequest,
)


def enabled_policy() -> BiometricPolicy:
    return BiometricPolicy(
        enabled=True,
        allowed_modalities=frozenset({BiometricModality.FINGERPRINT}),
        allowed_purposes=frozenset({BiometricPurpose.AUTHENTICATION}),
    )


def request(*, consent: bool = True) -> BiometricRequest:
    return BiometricRequest(
        actor_id="user-1",
        modality=BiometricModality.FINGERPRINT,
        purpose=BiometricPurpose.AUTHENTICATION,
        consent_granted=consent,
    )


def test_default_policy_denies_biometric_access() -> None:
    assert BiometricPolicyEngine().evaluate(request()) is BiometricDecision.DENY


def test_allowed_request_requires_consent() -> None:
    engine = BiometricPolicyEngine(enabled_policy())
    assert engine.evaluate(request(consent=False)) is BiometricDecision.DENY
    assert engine.evaluate(request(consent=True)) is BiometricDecision.ALLOW


def test_unapproved_modality_is_denied() -> None:
    engine = BiometricPolicyEngine(enabled_policy())
    denied = BiometricRequest(
        actor_id="user-1",
        modality=BiometricModality.FACE,
        purpose=BiometricPurpose.AUTHENTICATION,
        consent_granted=True,
    )
    assert engine.evaluate(denied) is BiometricDecision.DENY


def test_raw_biometric_samples_are_never_allowed() -> None:
    try:
        BiometricPolicy(raw_samples_allowed=True)
        raise AssertionError("expected raw sample policy to be rejected")
    except ValueError as exc:
        assert "raw biometric samples" in str(exc)
