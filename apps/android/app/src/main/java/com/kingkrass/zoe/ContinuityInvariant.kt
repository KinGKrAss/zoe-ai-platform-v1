package com.kingkrass.zoe

/**
 * Enforces the Z1 Continuity Principle at the Android boundary.
 * Model identity is never used as Zoë identity.
 */
object ContinuityInvariant {
    fun assertModelSwitchPreservesIdentity(
        before: ZoeContinuity,
        after: ZoeContinuity,
        oldModelId: String,
        newModelId: String
    ) {
        require(oldModelId != newModelId) { "Model switch requires different model ids" }
        check(before.identityId == after.identityId) {
            "Zoë identity changed during model switch"
        }
        check(before.identityVersion == after.identityVersion) {
            "Zoë identity version changed during model switch"
        }
        check(before.legacyHash == after.legacyHash) {
            "Zoë legacy memory changed during model switch"
        }
        check(before.stateVersion == after.stateVersion) {
            "Z1 state version changed during model switch"
        }
        check(before.authorized == after.authorized) {
            "Z1 authorization changed during model switch"
        }
    }
}
