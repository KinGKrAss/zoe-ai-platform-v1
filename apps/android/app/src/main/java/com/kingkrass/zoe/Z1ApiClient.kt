package com.kingkrass.zoe

import org.json.JSONArray
import org.json.JSONObject
import java.net.HttpURLConnection
import java.net.URL

/** Thin transport client. Z1 remains authoritative; this client only reads state. */
class Z1ApiClient(private val baseUrl: String, private val bearerToken: String? = null) {
    fun getContinuity(): ZoeContinuity = get("/api/v1/z1/continuity/zoe").let(ZoeContinuity::fromJson)
    fun getCouncil(): List<CouncilAgent> = get("/api/v1/z1/council").let(CouncilAgent::fromJsonArray)
    fun health(): Boolean = runCatching { get("/health"); true }.getOrDefault(false)

    private fun get(path: String): String {
        require(baseUrl.isNotBlank()) { "Z1_API_BASE_URL is not configured" }
        val connection = (URL(baseUrl.trimEnd('/') + path).openConnection() as HttpURLConnection).apply {
            requestMethod = "GET"
            connectTimeout = 10_000
            readTimeout = 20_000
            setRequestProperty("Accept", "application/json")
            bearerToken?.takeIf { it.isNotBlank() }?.let { setRequestProperty("Authorization", "Bearer $it") }
        }
        return connection.use { conn ->
            val body = (if (conn.responseCode in 200..299) conn.inputStream else conn.errorStream)
                ?.bufferedReader()?.use { it.readText() }.orEmpty()
            if (conn.responseCode !in 200..299) error("Z1 API ${conn.responseCode}: ${body.take(500)}")
            body
        }
    }
}

data class ZoeContinuity(
    val identityId: String,
    val identityVersion: String,
    val legacyHash: String,
    val stateVersion: String,
    val authorized: Boolean
) {
    companion object {
        fun fromJson(raw: String): ZoeContinuity {
            val o = JSONObject(raw).optJSONObject("data") ?: JSONObject(raw)
            return ZoeContinuity(
                o.optString("identity_id"), o.optString("identity_version"),
                o.optString("legacy_hash"), o.optString("state_version"),
                o.optBoolean("authorized", false)
            )
        }
    }
}

data class CouncilAgent(
    val agentCode: String,
    val name: String,
    val domain: String,
    val title: String,
    val version: String,
    val active: Boolean
) {
    companion object {
        fun fromJsonArray(raw: String): List<CouncilAgent> {
            val root = JSONObject(raw)
            val array = root.optJSONArray("data") ?: root.optJSONArray("agents") ?: JSONArray()
            return buildList {
                for (i in 0 until array.length()) {
                    val o = array.optJSONObject(i) ?: continue
                    add(CouncilAgent(
                        o.optString("agent_code"), o.optString("name"),
                        o.optString("domain"), o.optString("title"),
                        o.optString("version"), o.optBoolean("is_active", true)
                    ))
                }
            }
        }
    }
}
