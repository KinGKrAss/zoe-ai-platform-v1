package com.kingkrass.zoe

import android.content.Context

/**
 * Local cache only. It is never authoritative: Z1 owns identity, legacy and state.
 */
class Z1ContinuityStore(context: Context) {
    private val prefs = context.getSharedPreferences("z1_continuity_cache", Context.MODE_PRIVATE)

    fun save(value: ZoeContinuity) {
        prefs.edit()
            .putString("identity_id", value.identityId)
            .putString("identity_version", value.identityVersion)
            .putString("legacy_hash", value.legacyHash)
            .putString("state_version", value.stateVersion)
            .putBoolean("authorized", value.authorized)
            .apply()
    }

    fun load(): ZoeContinuity? {
        val id = prefs.getString("identity_id", null) ?: return null
        return ZoeContinuity(
            id,
            prefs.getString("identity_version", "") ?: "",
            prefs.getString("legacy_hash", "") ?: "",
            prefs.getString("state_version", "") ?: "",
            prefs.getBoolean("authorized", false)
        )
    }
}
