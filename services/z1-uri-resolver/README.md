# Z1 URI Resolver V1

RFC 3986-compatible URI reference resolution for the `z1` scheme.

## Base URI policy

Z1 requires an explicit, well-defined base for relative references. The resolver does not silently invent an application-dependent base. This follows RFC 3986 section 5.1's warning that relative references are only reliable when a base URI can be established.

## Resolution order

1. Embedded base supplied by the content/registry metadata.
2. Encapsulating Z1 entity context.
3. Retrieval URI when the representation was retrieved from a URI.
4. Explicit Z1 application default, only when configured and auditable.

The generic RFC 3986 algorithm is used for relative path merging and dot-segment removal. The `z1` scheme remains an opaque access protocol outside this resolver.

Examples:

- `z1://3d/assets/GAIA-000123/model.drc`
- base `z1://3d/assets/GAIA-000123/model.drc` + `./metadata.json`
- base `z1://3d/assets/GAIA-000123/model.drc` + `../textures/roof.png`
