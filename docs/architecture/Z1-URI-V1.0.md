# Z1 URI V1.0

**Status:** Draft implementation specification
**Scheme:** `z1`
**Normative base:** RFC 3986 (URI: Generic Syntax)

## 1. Purpose

Z1 URI provides stable identifiers for resources managed by System Z1. A Z1 URI identifies a resource; it does not itself prescribe how that resource is retrieved.

The generic URI syntax, reference resolution, normalization principles, and security considerations are based on RFC 3986. Z1 defines the scheme-specific semantics and resolver contract.

## 2. Syntax

The canonical absolute form is:

```text
z1://<namespace>/<path>
```

Examples:

```text
z1://3d/assets/GAIA-000123/model.drc
z1://ppt/token/PPT
z1://finance/accounts/main
z1://memory/zoe/entries/123
z1://documents/contracts/2026/001
z1://agents/zoe/GOD-001
```

`z1` is the scheme. The authority is the Z1 namespace. The path identifies the resource within that namespace.

## 3. RFC 3986 alignment

Z1 implementations MUST preserve the generic URI model of RFC 3986, including:

- Section 3: URI components and generic syntax
- Section 3.1: scheme
- Section 3.3: path
- Section 4.2: relative references
- Section 5.1: base URI establishment
- Section 5.2: relative reference resolution
- Section 5.2.4: removal of dot segments
- Section 6: normalization and comparison
- Section 7: security considerations

Z1 does not redefine RFC 3986 parsing rules. It adds scheme-specific semantics on top of them.

## 4. Identity versus resolution

A Z1 URI is an identifier. Resolution is a separate operation:

```text
URI
 -> parser
 -> canonicalizer
 -> resolver
 -> resource registry
 -> backend adapter
 -> resource
```

A resolver MAY map a URI to a database object, local file, API resource, blockchain object, document, agent, or another registered Z1 resource.

The URI MUST remain stable when the backing implementation changes, provided the resource identity itself has not changed.

## 5. Canonicalization

Before lookup, an absolute Z1 URI SHOULD be canonicalized.

Canonicalization MUST:

1. preserve the `z1` scheme;
2. normalize the namespace according to the registered namespace policy;
3. remove dot segments from the path according to RFC 3986 Section 5.2.4;
4. preserve percent-encoded octets unless a Z1 namespace explicitly defines a safe normalization rule;
5. avoid filesystem-specific interpretation of the URI;
6. produce a deterministic string for equivalent Z1 identifiers.

Implementations MUST NOT resolve `..` by directly manipulating a local filesystem path.

## 6. Relative references

Relative references are permitted only when a base Z1 URI is available. Resolution MUST follow RFC 3986 Section 5.2.

Example:

```text
base: z1://documents/contracts/2026/001/
ref:  ../2025/002
result: z1://documents/contracts/2025/002
```

## 7. Resolver contract

The resolver layer is deliberately independent from URI parsing.

A resolver receives a canonical Z1 URI and returns a registered resource reference. It MUST NOT silently reinterpret an unknown namespace as a local filesystem path or network endpoint.

Conceptual interface:

```text
resolve(uri: Z1URI) -> ResourceReference
```

The resource reference SHOULD expose at least:

- canonical URI
- namespace
- resource type
- resource identifier/path
- backend identifier
- version, where applicable
- metadata
- authorization requirements

## 8. Security

Z1 resolvers MUST treat URIs as untrusted input.

In particular:

- reject unsupported schemes;
- validate namespace boundaries;
- prevent path traversal after dot-segment normalization;
- do not automatically execute URI contents;
- do not treat a Z1 path as an operating-system path;
- apply authorization independently of URI parsing;
- avoid leaking backend credentials through URI components;
- prevent ambiguous canonical forms where security-sensitive identity checks are performed.

RFC 3986 Section 7 remains normative security guidance.

## 9. Initial namespaces

V1 reserves the following namespaces for Z1 modules:

| Namespace | Intended domain |
|---|---|
| `3d` | 3D assets and models |
| `ppt` | Preußen Point resources |
| `finance` | financial resources |
| `memory` | Z1/Zoë memory |
| `documents` | documents and contracts |
| `agents` | Zoë and agent resources |

Additional namespaces MUST be registered before production use.

## 10. Non-goals

Z1 URI V1 does not define:

- a transport protocol;
- an HTTP-like access mechanism;
- a database schema for every resource type;
- authentication itself;
- authorization policy itself;
- a blockchain protocol;
- a filesystem mapping.

Those concerns belong to resolver and adapter layers.

## 11. Reference

RFC 3986: *Uniform Resource Identifier (URI): Generic Syntax*, RFC Editor:
https://www.rfc-editor.org/info/rfc3986/
