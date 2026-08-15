import pytest

from .runtime import ZoeCoreRuntime


def test_zoe_core_builds_auditable_execution_plan():
    result = ZoeCoreRuntime().run("Prüfe die Nachweise für meine Wohnung", session_id="s-1")
    assert result.intent.kind == "document_analysis"
    assert result.plan.steps[0] == "load_context"
    assert "authorize_tools" in result.plan.steps
    assert result.metadata["session_id"] == "s-1"


def test_zoe_core_rejects_empty_input():
    with pytest.raises(ValueError):
        ZoeCoreRuntime().run("   ")
