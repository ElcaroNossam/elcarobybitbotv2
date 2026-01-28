plugins {
    alias(libs.plugins.android.application)
    alias(libs.plugins.kotlin.android)
    alias(libs.plugins.kotlin.compose)
    alias(libs.plugins.kotlin.serialization)
    alias(libs.plugins.hilt.android)
    alias(libs.plugins.ksp)
}

android {
    namespace = "io.enliko.trading"
    compileSdk = 35

    defaultConfig {
        applicationId = "io.enliko.trading"
        minSdk = 26
        targetSdk = 35
        versionCode = 1
        versionName = "1.0.0"

        testInstrumentationRunner = "androidx.test.runner.AndroidJUnitRunner"
        
        // App name - configurable via environment for rebranding
        val appName = System.getenv("APP_NAME") ?: "Enliko"
        resValue("string", "app_name_dynamic", "$appName Trading")
        buildConfigField("String", "APP_NAME", "\"$appName\"")
        buildConfigField("String", "BASE_URL", "\"https://enliko.com\"")
        buildConfigField("String", "WS_URL", "\"wss://enliko.com\"")
    }

    signingConfigs {
        create("release") {
            storeFile = file("../keystore/enliko-release.jks")
            storePassword = "enliko2026"
            keyAlias = "enliko"
            keyPassword = "enliko2026"
        }
    }

    buildTypes {
        debug {
            buildConfigField("String", "BASE_URL", "\"https://enliko.com\"")
            buildConfigField("String", "WS_URL", "\"wss://enliko.com\"")
        }
        release {
            isMinifyEnabled = true
            isShrinkResources = true
            signingConfig = signingConfigs.getByName("release")
            proguardFiles(
                getDefaultProguardFile("proguard-android-optimize.txt"),
                "proguard-rules.pro"
            )
        }
    }
    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }
    kotlinOptions {
        jvmTarget = "17"
    }
    buildFeatures {
        compose = true
        buildConfig = true
    }
}

dependencies {
    // Core
    implementation(libs.androidx.core.ktx)
    implementation(libs.androidx.lifecycle.runtime.ktx)
    implementation(libs.androidx.lifecycle.viewmodel.compose)
    implementation(libs.androidx.activity.compose)
    implementation(libs.androidx.splashscreen)
    
    // Compose
    implementation(platform(libs.androidx.compose.bom))
    implementation(libs.androidx.ui)
    implementation(libs.androidx.ui.graphics)
    implementation(libs.androidx.ui.tooling.preview)
    implementation(libs.androidx.material3)
    implementation(libs.androidx.material.icons.extended)
    implementation(libs.androidx.navigation.compose)
    
    // Hilt DI
    implementation(libs.hilt.android)
    ksp(libs.hilt.compiler)
    implementation(libs.hilt.navigation.compose)
    
    // Security - Encrypted Storage & Biometrics
    implementation(libs.androidx.security.crypto)
    implementation(libs.androidx.biometric)
    
    // Networking
    implementation(libs.retrofit)
    implementation(libs.retrofit.kotlinx.serialization)
    implementation(libs.okhttp)
    implementation(libs.okhttp.logging)
    
    // Kotlin
    implementation(libs.kotlinx.serialization.json)
    implementation(libs.kotlinx.coroutines.android)
    
    // DataStore (for non-sensitive preferences)
    implementation(libs.androidx.datastore.preferences)
    
    // Image Loading
    implementation(libs.coil.compose)
    
    // Debug
    debugImplementation(libs.androidx.ui.tooling)
}
