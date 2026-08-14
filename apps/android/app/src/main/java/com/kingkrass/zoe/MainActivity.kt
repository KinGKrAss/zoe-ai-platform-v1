package com.kingkrass.zoe

import android.os.Bundle
import android.widget.LinearLayout
import android.widget.TextView
import androidx.activity.ComponentActivity
import androidx.core.view.setPadding

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        val capabilities = SystemCapabilityRepository(this).snapshot()
        val text = TextView(this).apply {
            setPadding(32)
            textSize = 16f
            text = buildString {
                appendLine("Zoë / Z1 – Android System Adapter")
                appendLine()
                appendLine("Device: ${capabilities.manufacturer} ${capabilities.model}")
                appendLine("Android: ${capabilities.androidVersion} (SDK ${capabilities.sdkInt})")
                appendLine()
                appendLine("Android System Intelligence: ${yesNo(capabilities.androidSystemIntelligence)}")
                appendLine("AICore: ${yesNo(capabilities.aicore)}")
                appendLine("Private Compute Services: ${yesNo(capabilities.privateComputeServices)}")
                appendLine("Local AI available: ${yesNo(capabilities.localAiAvailable)}")
                appendLine()
                appendLine("Z1 permissions:")
                capabilities.permissions.forEach { (name, granted) ->
                    appendLine("  $name: ${yesNo(granted)}")
                }
            }
        }

        setContentView(LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            addView(text)
        })
    }

    private fun yesNo(value: Boolean) = if (value) "YES" else "NO"
}
