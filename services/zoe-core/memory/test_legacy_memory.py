from services.zoe_core.memory.legacy_memory import LegacyMemoryStore


def test_legacy_memory_is_append_only_and_versioned(tmp_path):
    store = LegacyMemoryStore(tmp_path / "memory.jsonl")
    first = store.append(
        identity_id="ZOE-IDENTITY-V1.0",
        kind="identity",
        content="Zoë continuity record",
        source="z1",
    )
    second = store.append(
        identity_id="ZOE-IDENTITY-V1.0",
        kind="decision",
        content="Z1 remains the system of record",
        source="user",
    )

    assert first.version == 1
    assert second.version == 2
    assert len(store.list(identity_id="ZOE-IDENTITY-V1.0")) == 2
    assert "Z1 remains" in store.context(identity_id="ZOE-IDENTITY-V1.0")


def test_memory_isolated_by_identity(tmp_path):
    store = LegacyMemoryStore(tmp_path / "memory.jsonl")
    store.append(identity_id="ZOE-IDENTITY-V1.0", kind="fact", content="A", source="test")
    store.append(identity_id="OTHER", kind="fact", content="B", source="test")

    assert [m.content for m in store.list(identity_id="ZOE-IDENTITY-V1.0")] == ["A"]
