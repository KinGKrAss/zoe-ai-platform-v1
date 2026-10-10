package com.kingkrass.zoe

import android.Manifest
import android.content.pm.PackageManager
import android.os.Bundle
import android.widget.LinearLayout
import android.widget.TextView
import androidx.activity.ComponentActivity
import androidx.activity.result.contract.ActivityResultContracts
import androidx.core.content.ContextCompat
import androidx.core.view.setPadding

class MainActivity : ComponentActivity() {
    private val permissionLauncher =
        registerForActivityResult(ActivityResultContracts.RequestMultiplePermissions()) {
            render()
        }

    private lateinit var statusText: TextView

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        statusText = TextView(this).apply {
            setPadding(32)
            textSize = 16f
        }

        setContentView(LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            addView(statusText)
        })

        requestMissingPermissions()
        render()
    }

    private fun requestMissingPermissions() {
        val requested = permissionList().filter {
            ContextCompat.checkSelfPermission(this, it) != PackageManager.PERMISSION_GRANTED
        }
        if (requested.isNotEmpty()) permissionLauncher.launch(requested.toTypedArray())
    }

    private fun permissionList(): Array<String> {
        val permissions = mutableListOf(
            Manifest.permission.RECORD_AUDIO,
            Manifest.permission.CAMERA,
            Manifest.permission.ACCESS_FINE_LOCATION,
            Manifest.permission.ACCESS_COARSE_LOCATION
        )
        if (android.os.Build.VERSION.SDK_INT >= 31) {
            permissions += Manifest.permission.BLUETOOTH_CONNECT
            permissions += Manifest.permission.BLUETOOTH_SCAN
        }
        if (android.os.Build.VERSION.SDK_INT >= 33) permissions += Manifest.permission.POST_NOTIFICATIONS
        return permissions.toTypedArray()
    }

    private fun render() {
        val capabilities = SystemCapabilityRepository(this).snapshot()
        val sessionPresent = Z1SecureStore(this).readSessionToken() != null
        statusText.text = buildString {
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
            appendLine("Z1 API: ${BuildConfig.Z1_API_BASE_URL}")
            appendLine("Session token stored: ${yesNo(sessionPresent)}")
            appendLine()
            appendLine("Z1 permissions:")
            capabilities.permissions.forEach { (name, granted) -> appendLine("  $name: ${yesNo(granted)}") }
        }
    }

    private fun yesNo(value: Boolean) = if (value) "YES" else "NO"
}
