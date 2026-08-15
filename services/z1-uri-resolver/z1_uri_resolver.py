"""Z1 URI Resolver V1.

Implements the generic URI-reference resolution model from RFC 3986 while
keeping the ``z1`` scheme opaque to generic parsing. Resolution uses an
explicit base URI supplied by the Z1 Registry/context layer.
"""
from __future__ import annotations

from dataclasses import dataclass
from urllib.parse import urljoin, urlparse


class Z1URIError(ValueError):
    """Raised for invalid or unsupported Z1 URI operations."""


@dataclass(frozen=True)
class Z1URI:
    scheme: str
    authority: str
    path: str
    query: str
    fragment: str

    @property
    def absolute(self) -> bool:
        return bool(self.scheme)

    def as_string(self) -> str:
        authority = f"//{self.authority}" if self.authority else ""
        query = f"?{self.query}" if self.query else ""
        fragment = f"#{self.fragment}" if self.fragment else ""
        return f"{self.scheme}:{authority}{self.path}{query}{fragment}"


def parse(uri: str) -> Z1URI:
    if not isinstance(uri, str) or not uri:
        raise Z1URIError("URI must be a non-empty string")
    p = urlparse(uri)
    return Z1URI(p.scheme.lower(), p.netloc, p.path, p.query, p.fragment)


def normalize(uri: str) -> str:
    """Normalize an absolute URI using RFC 3986-style generic rules.

    The resolver intentionally does not invent scheme-specific semantics for
    z1://. Paths are normalized by RFC-compatible relative resolution against
    a root Z1 base.
    """
    parsed = parse(uri)
    if parsed.scheme != "z1":
        raise Z1URIError("Z1 resolver accepts only the z1 scheme")
    if not parsed.absolute:
        raise Z1URIError("Z1 URI must be absolute")
    # urljoin performs RFC 3986-style dot-segment removal for hierarchical URIs.
    normalized = urljoin("z1://z1/", uri)
    return normalized


def resolve(reference: str, base: str) -> str:
    """Resolve a URI reference against a Z1 base URI.

    RFC 3986 §5.1 requires a well-defined base URI for reliable relative
    references. Z1 therefore requires an explicit base for relative refs.
    """
    if not isinstance(reference, str) or not reference:
        raise Z1URIError("Reference must be a non-empty string")
    b = parse(base)
    if b.scheme != "z1":
        raise Z1URIError("Base URI must use the z1 scheme")
    result = urljoin(base, reference)
    r = parse(result)
    if r.scheme != "z1":
        raise Z1URIError("Resolved URI escaped the z1 scheme")
    return result


def is_z1(uri: str) -> bool:
    try:
        return parse(uri).scheme == "z1"
    except Z1URIError:
        return False
