package com.kingkrass.zoe

import java.io.IOException
import java.net.HttpURLConnection
import java.net.URL
import java.util.concurrent.Executors

class Z1ApiClient {
    private val executor = Executors.newCachedThreadPool()

    fun getSystemStatus(
        sessionToken: String,
        onResult: (Result<String>) -> Unit
    ) {
        executor.execute {
            onResult(runCatching { get("/v1/system/status", sessionToken) })
        }
    }

    private fun get(path: String, token: String): String {
        val base = BuildConfig.Z1_API_BASE_URL.trimEnd('/')
        require(base.startsWith("https://")) { "Z1_API_BASE_URL must use HTTPS" }

        val connection = (URL("$base$path").openConnection() as HttpURLConnection).apply {
            requestMethod = "GET"
            connectTimeout = 10_000
            readTimeout = 10_000
            setRequestProperty("Accept", "application/json")
            setRequestProperty("Authorization", "Bearer $token")
        }

        try {
            val status = connection.responseCode
            val stream = if (status in 200..299) connection.inputStream else connection.errorStream
            val body = stream?.bufferedReader()?.use { it.readText() }.orEmpty()
            if (status !in 200..299) {
                throw IOException("Z1 API returned HTTP $status: $body")
            }
            return body
        } finally {
            connection.disconnect()
        }
    }
}
