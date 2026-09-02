plugins {
    id("com.android.application")
    id("org.jetbrains.kotlin.android")
}

android {
    namespace = "com.kingkrass.zoe"
    compileSdk = 35

    defaultConfig {
        applicationId = "com.kingkrass.zoe"
        minSdk = 26
        targetSdk = 35
        versionCode = 1
        versionName = "0.2.0"
        val z1ApiUrl = providers.gradleProperty("z1ApiUrl").orElse("http://10.0.2.2:8000").get()
        buildConfigField("String", "Z1_API_BASE_URL", "\"$z1ApiUrl\"")
    }

    buildFeatures { buildConfig = true }

    kotlinOptions { jvmTarget = "17" }
}

dependencies {
    implementation("androidx.core:core-ktx:1.15.0")
    implementation("androidx.activity:activity-ktx:1.10.0")
    implementation("androidx.lifecycle:lifecycle-runtime-ktx:2.8.7")
}
