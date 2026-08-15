import pytest

from .runtime import Z1CoreRuntime
from .z1_identity import Z1Identity
from .z1_permissions import Z1Action, Z1Authorizer, Z1Policy


def test_runtime_enforces_identity_and_policy():
    identity = Z1Identity.create(
        "z1://finance/accounts/main",
        "financial-account",
        "house-loewenherz",
    )
    authorizer = Z1Authorizer(
        [
            Z1Policy(
                subject="zoe",
                actions=frozenset({Z1Action.READ, Z1Action.WRITE}),
                namespaces=frozenset({"finance"}),
            )
        ]
    )
    runtime = Z1CoreRuntime(authorizer)
    runtime.register(identity, {"balance": 100}, subject="zoe")
    assert runtime.read(identity.uri, subject="zoe").value["balance"] == 100
    assert runtime.write(identity.uri, {"balance": 125}, subject="zoe").value["balance"] == 125


def test_runtime_denies_unprivileged_subject():
    identity = Z1Identity.create("z1://finance/accounts/main", "financial-account", "house-loewenherz")
    runtime = Z1CoreRuntime()
    with pytest.raises(PermissionError):
        runtime.register(identity, {}, subject="guest")
