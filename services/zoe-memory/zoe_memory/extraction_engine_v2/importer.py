from __future__ import annotations

import json
from pathlib import Path

from .models import Message


def load_chatgpt_export(path: str | Path) -> list[Message]:
    """Load the common ChatGPT conversations.json export format.

    Unknown fields are ignored. Mapping remains deliberately thin: importer owns
    source normalization, extraction owns evidence decisions.
    """
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    conversations = payload if isinstance(payload, list) else payload.get("conversations", [])
    messages: list[Message] = []
    for conversation in conversations:
        conversation_id = str(conversation.get("conversation_id") or conversation.get("id") or "unknown")
        mapping = conversation.get("mapping", {})
        for node_id, node in mapping.items():
            message = node.get("message") or {}
            content = message.get("content") or {}
            parts = content.get("parts", []) if isinstance(content, dict) else []
            text = "\n".join(str(part) for part in parts if isinstance(part, str)).strip()
            if not text:
                continue
            author = message.get("author") or {}
            role = str(author.get("role") or "unknown")
            messages.append(Message(conversation_id, str(node_id), role, text))
    return messages
