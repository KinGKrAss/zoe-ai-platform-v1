from runtime import RuntimeStatus, Z1Runtime, can_mark_verified


def test_runtime_starts_ready():
    runtime = Z1Runtime()
    runtime.register("z1-core")
    runtime.register("memory-core")
    runtime.start()
    assert runtime.status() == RuntimeStatus.READY


def test_runtime_requires_components():
    runtime = Z1Runtime()
    try:
        runtime.start()
    except RuntimeError:
        pass
    else:
        raise AssertionError("runtime must fail closed without components")


def test_verification_requires_evidence_and_authorization():
    assert can_mark_verified(evidence_verified=True, authorized_actor=True)
    assert not can_mark_verified(evidence_verified=False, authorized_actor=True)
    assert not can_mark_verified(evidence_verified=True, authorized_actor=False)
