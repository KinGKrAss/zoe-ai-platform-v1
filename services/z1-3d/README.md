# Z1 3D Asset Adapter V1

Adapter boundary for 3D asset metadata and Draco-compressed geometry in the Z1 platform.

## Scope

V1 intentionally stays small:

- define a stable 3D asset contract
- validate asset metadata
- expose a renderer-neutral asset descriptor
- identify Draco geometry without coupling Z1 Core to a browser renderer
- keep the adapter usable by GAIA, Web, Android, and future 3D services

## Non-goals

- mesh encoding/decoding inside Z1 Core
- rendering
- binary asset storage
- database persistence
- automatic downloading of remote assets

## Asset contract

Required fields:

- `asset_id`: stable Z1 asset identifier
- `source_uri`: location of the geometry asset
- `format`: `draco`, `glb`, `gltf`, or `obj`
- `version`: adapter contract version

Optional fields include `content_hash`, `size_bytes`, `vertex_count`, `face_count`, and arbitrary metadata.

The adapter should be treated as a permissioned tool boundary. Reading metadata is safe; fetching, replacing, or deleting binary assets belongs to a higher-level tool with explicit authorization and audit logging.

## Suggested flow

`GAIA asset -> Z1 3D Asset Adapter -> renderer/storage adapter -> Web/Android`

For Draco assets, decoding should happen in the client/runtime layer (for example WASM in the web client), not in Z1 Core.
