package com.kingkrass.zoe

import android.content.Context
import android.content.pm.PackageManager
import android.os.Build

private const val ASI_PACKAGE = "com.google.android.as"
private const val AICORE_PACKAGE = "com.google.android.aicore"
private const val PRIVATE_COMPUTE_SERVICES_PACKAGE = "com.google.android.as.oss"

class SystemCapabilityRepository(private val context: Context) {
    private val packageManager = context.packageManager

    fun snapshot(): SystemCapabilities {
        return SystemCapabilities(
            manufacturer = Build.MANUFACTURER,
            model = Build.MODEL,
            androidVersion = Build.VERSION.RELEASE ?: "unknown",
            sdkInt = Build.VERSION.SDK_INT,
            androidSystemIntelligence = installed(ASI_PACKAGE),
            aicore = installed(AICORE_PACKAGE),
            privateComputeServices = installed(PRIVATE_COMPUTE_SERVICES_PACKAGE),
            permissions = mapOf(
                "notifications" to granted("android.permission.POST_NOTIFICATIONS"),
                "microphone" to granted("android.permission.RECORD_AUDIO"),
                "camera" to granted("android.permission.CAMERA"),
                "fine_location" to granted("android.permission.ACCESS_FINE_LOCATION"),
                "coarse_location" to granted("android.permission.ACCESS_COARSE_LOCATION"),
                "bluetooth_connect" to granted("android.permission.BLUETOOTH_CONNECT"),
                "bluetooth_scan" to granted("android.permission.BLUETOOTH_SCAN")
            )
        )
    }

    private fun installed(packageName: String): Boolean = try {
        packageManager.getPackageInfo(packageName, 0)
        true
    } catch (_: PackageManager.NameNotFoundException) {
        false
    }

    private fun granted(permission: String): Boolean =
        Build.VERSION.SDK_INT < 23 ||
            context.checkSelfPermission(permission) == PackageManager.PERMISSION_GRANTED
}

data class SystemCapabilities(
    val manufacturer: String,
    val model: String,
    val androidVersion: String,
    val sdkInt: Int,
    val androidSystemIntelligence: Boolean,
    val aicore: Boolean,
    val privateComputeServices: Boolean,
    val permissions: Map<String, Boolean>
) {
    val localAiAvailable: Boolean get() = aicore

    fun toMap(): Map<String, Any> = mapOf(
        "manufacturer" to manufacturer,
        "model" to model,
        "android_version" to androidVersion,
        "sdk_int" to sdkInt,
        "android_system_intelligence" to androidSystemIntelligence,
        "aicore" to aicore,
        "private_compute_services" to privateComputeServices,
        "local_ai_available" to localAiAvailable,
        "permissions" to permissions
    )
}
