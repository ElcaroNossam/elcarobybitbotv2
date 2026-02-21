package io.enliko.trading.data.api

import android.util.Log
import kotlinx.serialization.json.Json
import okhttp3.ConnectionSpec
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.OkHttpClient
import okhttp3.TlsVersion
import okhttp3.logging.HttpLoggingInterceptor
import retrofit2.Retrofit
import retrofit2.converter.kotlinx.serialization.asConverterFactory
import java.util.concurrent.TimeUnit

/**
 * Singleton RetrofitClient for non-Hilt components
 * (e.g., BacktestViewModel)
 */
object RetrofitClient {
    
    private const val BASE_URL = "https://enliko.com"
    
    private val json = Json {
        ignoreUnknownKeys = true
        isLenient = true
        encodeDefaults = true
        coerceInputValues = true
    }
    
    private val loggingInterceptor = HttpLoggingInterceptor().apply {
        level = HttpLoggingInterceptor.Level.BODY
    }
    
    private val modernTls = ConnectionSpec.Builder(ConnectionSpec.MODERN_TLS)
        .tlsVersions(TlsVersion.TLS_1_2, TlsVersion.TLS_1_3)
        .build()
    
    private val okHttpClient: OkHttpClient by lazy {
        OkHttpClient.Builder()
            .addInterceptor(loggingInterceptor)
            .connectionSpecs(listOf(modernTls, ConnectionSpec.CLEARTEXT))
            .connectTimeout(30, TimeUnit.SECONDS)
            .readTimeout(60, TimeUnit.SECONDS)
            .writeTimeout(30, TimeUnit.SECONDS)
            .retryOnConnectionFailure(true)
            .build()
    }
    
    private val retrofit: Retrofit by lazy {
        Retrofit.Builder()
            .baseUrl(BASE_URL)
            .client(okHttpClient)
            .addConverterFactory(json.asConverterFactory("application/json".toMediaType()))
            .build()
    }
    
    val api: EnlikoApi by lazy {
        retrofit.create(EnlikoApi::class.java)
    }
}
