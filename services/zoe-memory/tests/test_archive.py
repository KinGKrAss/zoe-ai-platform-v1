import json

from zoe_memory.archive import load_chatgpt_archive, sha256_bytes


def test_sha256_is_stable() -> None:
    assert sha256_bytes(b"hello") == (
        "2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824"
    )


def test_load_chatgpt_archive_preserves_source_identity(tmp_path) -> None:
    export = [
        {
            "conversation_id": "conv-1",
            "mapping": {
                "msg-1": {
                    "message": {
                        "author": {"role": "user"},
                        "content": {"parts": ["Mein Portfolio beträgt 16,4 Mrd. EUR."]},
                        "create_time": 1786550400,
                    }
                },
                "msg-empty": {"message": None},
            },
        }
    ]
    path = tmp_path / "conversations.json"
    path.write_text(json.dumps(export), encoding="utf-8")

    source_hash, items = load_chatgpt_archive(path)

    assert len(source_hash) == 64
    assert len(items) == 1
    assert items[0]["conversation_ref"] == "conv-1"
    assert items[0]["message_ref"] == "msg-1"
    assert items[0]["role"] == "user"
    assert "16,4 Mrd. EUR" in items[0]["content"]
    assert items[0]["source_locator"] == {
        "conversation_id": "conv-1",
        "message_id": "msg-1",
    }
