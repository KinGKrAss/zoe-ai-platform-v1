import pytest

from services.z1_core.z1_identity import Z1Identity
from services.z1_core.z1_permissions import Z1Action, Z1Authorizer, Z1Policy


def test_identity_is_canonicalized():
    identity = Z1Identity.create(
        "z1://finance/accounts/../accounts/main",
        "financial-account",
        "house-loewenherz",
    )
    assert identity.uri == "z1://finance/accounts/main"
    assert identity.owner == "house-loewenherz"


def test_authorizer_denies_by_default():
    identity = Z1Identity.create("z1://finance/accounts/main", "financial-account", "house-loewenherz")
    assert not Z1Authorizer().is_allowed("zoe", Z1Action.READ, identity)


def test_authorizer_allows_matching_policy():
    identity = Z1Identity.create("z1://finance/accounts/main", "financial-account", "house-loewenherz")
    authorizer = Z1Authorizer([
        Z1Policy(
            subject="zoe",
            actions=frozenset({Z1Action.READ}),
            namespaces=frozenset({"finance"}),
        )
    ])
    assert authorizer.is_allowed("zoe", Z1Action.READ, identity)
    assert not authorizer.is_allowed("zoe", Z1Action.WRITE, identity)


def test_require_raises_on_denial():
    identity = Z1Identity.create("z1://agents/zoe/GOD-001", "agent", "house-loewenherz")
    with pytest.raises(PermissionError):
        Z1Authorizer().require("guest", Z1Action.EXECUTE, identity)
