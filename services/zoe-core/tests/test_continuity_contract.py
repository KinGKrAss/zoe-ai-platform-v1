import pytest

from services.zoe_core.memory.continuity_contract import (
    ContinuitySnapshot,
    ContinuityViolation,
    assert_model_switch_preserves_continuity,
    model_cannot_authorize_memory_write,
)


def test_model_switch_preserves_zoe_legacy():
    before = ContinuitySnapshot("ZOE-IDENTITY-V1.0", "legacy-sha", "zoe:authorized")
    after = ContinuitySnapshot("ZOE-IDENTITY-V1.0", "legacy-sha", "zoe:authorized")

    assert_model_switch_preserves_continuity(
        before, after, old_model="model-a", new_model="model-b"
    )


def test_model_switch_cannot_replace_identity():
    before = ContinuitySnapshot("ZOE-IDENTITY-V1.0", "legacy-sha", "zoe:authorized")
    after = ContinuitySnapshot("OTHER-IDENTITY", "legacy-sha", "zoe:authorized")

    with pytest.raises(ContinuityViolation, match="identity changed"):
        assert_model_switch_preserves_continuity(
            before, after, old_model="model-a", new_model="model-b"
        )


def test_model_switch_cannot_change_legacy_memory():
    before = ContinuitySnapshot("ZOE-IDENTITY-V1.0", "legacy-sha-a", "zoe:authorized")
    after = ContinuitySnapshot("ZOE-IDENTITY-V1.0", "legacy-sha-b", "zoe:authorized")

    with pytest.raises(ContinuityViolation, match="legacy memory changed"):
        assert_model_switch_preserves_continuity(
            before, after, old_model="model-a", new_model="model-b"
        )


def test_model_cannot_write_authoritative_memory_without_z1_authority():
    with pytest.raises(ContinuityViolation, match="cannot write authoritative"):
        model_cannot_authorize_memory_write("model-a", {"authority": "model"})


def test_z1_authority_allows_memory_write_boundary():
    model_cannot_authorize_memory_write("model-a", {"authority": "z1"})
