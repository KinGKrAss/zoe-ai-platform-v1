package com.kingkrass.zoe

import android.os.Bundle
import android.widget.Button
import android.widget.LinearLayout
import android.widget.TextView
import androidx.activity.ComponentActivity
import androidx.core.view.setPadding

class MainActivity : ComponentActivity() {
    private lateinit var status: TextView
    private lateinit var continuityStore: Z1ContinuityStore

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        continuityStore = Z1ContinuityStore(this)

        status = TextView(this).apply {
            setPadding(32)
            textSize = 16f
        }

        val refresh = Button(this).apply {
            text = "Z1 synchronisieren"
            setOnClickListener { synchronize() }
        }

        setContentView(LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            setPadding(24)
            addView(status)
            addView(refresh)
        })

        renderCachedState()
        synchronize()
    }

    private fun renderCachedState() {
        val capabilities = SystemCapabilityRepository(this).snapshot()
        val cached = continuityStore.load()
        status.text = buildString {
            appendLine("Z1 / Zoë Android")
            appendLine()
            appendLine("Z1: authoritative state")
            appendLine("Zoë: interpretation / planning")
            appendLine("MCP: interaction")
            appendLine("Model: inference")
            appendLine()
            appendLine("Device: ${capabilities.manufacturer} ${capabilities.model}")
            appendLine("Android: ${capabilities.androidVersion} (SDK ${capabilities.sdkInt})")
            appendLine()
            appendLine("Zoë continuity cache: ${if (cached == null) "empty" else "present"}")
            cached?.let {
                appendLine("Identity: ${it.identityId}")
                appendLine("Identity version: ${it.identityVersion}")
                appendLine("Legacy hash: ${it.legacyHash}")
                appendLine("State version: ${it.stateVersion}")
                appendLine("Authorized: ${it.authorized}")
            }
            appendLine()
            appendLine("Council of 33: awaiting Z1 sync")
        }
    }

    private fun synchronize() {
        status.text = "Z1 synchronization…\n\nConnecting to ${BuildConfig.Z1_API_BASE_URL}"
        Thread {
            runCatching {
                val api = Z1ApiClient(BuildConfig.Z1_API_BASE_URL)
                val continuity = api.getContinuity()
                val council = CouncilRegistry(api).load()
                continuityStore.save(continuity)
                Pair(continuity, council)
            }.onSuccess { (continuity, council) ->
                runOnUiThread {
                    status.text = buildString {
                        appendLine("Z1 synchronization: OK")
                        appendLine()
                        appendLine("Zoë identity: ${continuity.identityId}")
                        appendLine("Identity version: ${continuity.identityVersion}")
                        appendLine("Legacy hash: ${continuity.legacyHash}")
                        appendLine("State version: ${continuity.stateVersion}")
                        appendLine("Authorized: ${continuity.authorized}")
                        appendLine()
                        appendLine("Council agents: ${council.size}/33")
                        appendLine("Council complete: ${council.size == 33}")
                        appendLine()
                        appendLine("Z1 bewahrt. Zoë interpretiert. MCP vermittelt. Das Modell rechnet.")
                    }
                }
            }.onFailure { error ->
                runOnUiThread {
                    status.text = "Z1 synchronization failed\n\n${error.message}\n\nCached state remains local and non-authoritative."
                }
            }
        }.start()
    }
}
