"""Z1 URI V1 parser and canonicalizer.

The module deliberately separates URI identity from resource resolution.
It uses Python's standard URI parser for generic syntax and implements the
Z1-specific scheme/namespace contract.
"""

from __future__ import annotations

from dataclasses import dataclass
from urllib.parse import urljoin, urlsplit, urlunsplit


class Z1URIError(ValueError):
    """Raised when a Z1 URI violates the Z1 URI V1 contract."""


@dataclass(frozen=True)
class Z1URI:
    scheme: str
    namespace: str
    path: str
    query: str = ""
    fragment: str = ""

    def __post_init__(self) -> None:
        if self.scheme != "z1":
            raise Z1URIError("Z1 URI scheme must be 'z1'")
        if not self.namespace:
            raise Z1URIError("Z1 URI requires a namespace")
        if not self.path.startswith("/"):
            raise Z1URIError("Z1 URI path must be absolute")
        if self.namespace.lower() != self.namespace:
            raise Z1URIError("Z1 namespace must be lowercase")

    @property
    def authority(self) -> str:
        return self.namespace

    @property
    def uri(self) -> str:
        return urlunsplit((self.scheme, self.namespace, self.path, self.query, self.fragment))

    def canonical(self) -> "Z1URI":
        return parse_z1_uri(self.uri)



def _remove_dot_segments(path: str) -> str:
    """RFC 3986 Section 5.2.4 dot-segment removal."""
    output: list[str] = []
    input_buffer = path

    while input_buffer:
        if input_buffer.startswith("../"):
            input_buffer = input_buffer[3:]
        elif input_buffer.startswith("./"):
            input_buffer = input_buffer[2:]
        elif input_buffer.startswith("/./"):
            input_buffer = "/" + input_buffer[3:]
        elif input_buffer == "/.":
            input_buffer = "/"
        elif input_buffer.startswith("/../"):
            input_buffer = "/" + input_buffer[4:]
            if output:
                output.pop()
        elif input_buffer == "/..":
            input_buffer = "/"
            if output:
                output.pop()
        elif input_buffer in (".", ".."):
            input_buffer = ""
        else:
            if input_buffer.startswith("/"):
                slash = input_buffer.find("/", 1)
            else:
                slash = input_buffer.find("/")
            if slash == -1:
                segment = input_buffer
                input_buffer = ""
            else:
                segment = input_buffer[:slash]
                input_buffer = input_buffer[slash:]
            output.append(segment)

    result = "".join(output)
    if not result.startswith("/"):
        result = "/" + result
    return result


def parse_z1_uri(value: str) -> Z1URI:
    """Parse and canonicalize an absolute Z1 URI."""
    if not isinstance(value, str) or not value:
        raise Z1URIError("URI must be a non-empty string")

    parts = urlsplit(value)
    if parts.scheme != "z1":
        raise Z1URIError("URI must use the z1 scheme")
    if not parts.netloc:
        raise Z1URIError("Z1 URI must use an authority/namespace")
    if ":" in parts.netloc or "@" in parts.netloc:
        raise Z1URIError("userinfo and port are not permitted in a Z1 namespace")
    if not parts.path.startswith("/"):
        raise Z1URIError("Z1 URI path must be absolute")

    namespace = parts.netloc
    path = _remove_dot_segments(parts.path)
    return Z1URI("z1", namespace, path, parts.query, parts.fragment)


def resolve_z1_reference(reference: str, base: str) -> Z1URI:
    """Resolve a Z1 relative reference using RFC 3986 reference semantics."""
    base_uri = parse_z1_uri(base)
    if not reference:
        return base_uri

    # urljoin applies the generic RFC 3986 reference resolution algorithm.
    resolved = urljoin(base_uri.uri, reference)
    return parse_z1_uri(resolved)


class Z1Resolver:
    """Abstract resolver contract; concrete backends register handlers."""

    def resolve(self, uri: Z1URI):
        raise NotImplementedError
