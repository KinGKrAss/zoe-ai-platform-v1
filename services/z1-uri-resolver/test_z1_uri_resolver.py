from z1_uri_resolver import Z1URIError, is_z1, normalize, resolve


def test_resolve_relative_asset():
    assert resolve("../textures/roof.png", "z1://3d/assets/GAIA-000123/model.drc") == "z1://3d/assets/GAIA-000123/../textures/roof.png"


def test_resolve_child_asset():
    assert resolve("./metadata.json", "z1://3d/assets/GAIA-000123/model.drc") == "z1://3d/assets/GAIA-000123/metadata.json"


def test_z1_scheme_detection():
    assert is_z1("z1://3d/assets/GAIA-000123/model.drc")
    assert not is_z1("https://example.com/model.drc")


def test_reject_cross_scheme_base():
    try:
        resolve("model.drc", "https://example.com/assets/")
    except Z1URIError:
        pass
    else:
        raise AssertionError("cross-scheme base must be rejected")
