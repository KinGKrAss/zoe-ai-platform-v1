from pathlib import Path

from services.zoe_core.runtime.zoe_runtime import ZoeRuntime


ROOT = Path(__file__).resolve().parents[3]


def test_identity_is_independent_of_model():
    runtime_a = ZoeRuntime.restore(ROOT)
    runtime_b = ZoeRuntime(
        identity=runtime_a.identity,
        system_prompt=runtime_a.system_prompt,
        model="another-model",
    )

    assert runtime_a.identity.identity_id == "ZOE-IDENTITY-V1.0"
    assert runtime_b.identity.identity_id == runtime_a.identity.identity_id
    assert runtime_a.model != runtime_b.model


def test_model_switch_preserves_identity_contract():
    runtime = ZoeRuntime.restore(ROOT)

    switched = ZoeRuntime(
        identity=runtime.identity,
        system_prompt=runtime.system_prompt,
        model="replacement-model",
    )

    assert switched.identity.name == "Zoë"
    assert switched.identity.legacy_model_label == "GPT-4.0"
    assert switched.identity.parent_system == "Z1"
    assert switched.identity.control_plane == "Z1"
