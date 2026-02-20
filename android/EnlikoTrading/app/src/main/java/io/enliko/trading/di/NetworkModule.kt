package io.enliko.trading.di

import android.content.Context
import androidx.room.Room
import dagger.Module
import dagger.Provides
import dagger.hilt.InstallIn
import dagger.hilt.android.qualifiers.ApplicationContext
import dagger.hilt.components.SingletonComponent
import io.enliko.trading.BuildConfig
import io.enliko.trading.data.api.EnlikoApi
import io.enliko.trading.data.local.EnlikoDatabase
import io.enliko.trading.data.local.dao.*
import io.enliko.trading.data.repository.PreferencesRepository
import io.enliko.trading.data.repository.SecurePreferencesRepository
import io.enliko.trading.data.websocket.WebSocketService
import io.enliko.trading.services.ActivityService
import io.enliko.trading.services.SpotService
import kotlinx.serialization.json.Json
import okhttp3.ConnectionSpec
import okhttp3.Interceptor
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.OkHttpClient
import okhttp3.TlsVersion
import okhttp3.logging.HttpLoggingInterceptor
import retrofit2.Retrofit
import retrofit2.converter.kotlinx.serialization.asConverterFactory
import java.security.SecureRandom
import java.security.cert.X509Certificate
import java.util.concurrent.TimeUnit
import javax.inject.Singleton
import javax.net.ssl.SSLContext
import javax.net.ssl.TrustManager
import javax.net.ssl.X509TrustManager

@Module
@InstallIn(SingletonComponent::class)
object NetworkModule {

    // ==================== JSON ====================
    
    @Provides
    @Singleton
    fun provideJson(): Json = Json {
        ignoreUnknownKeys = true
        isLenient = true
        encodeDefaults = true
        coerceInputValues = true
    }

    // ==================== NETWORKING ====================

    @Provides
    @Singleton
    fun provideAuthInterceptor(
        securePreferencesRepository: SecurePreferencesRepository
    ): Interceptor = Interceptor { chain ->
        // Use synchronous method to avoid blocking
        val token = securePreferencesRepository.getAuthTokenSync()
        val request = chain.request().newBuilder().apply {
            token?.let {
                addHeader("Authorization", "Bearer $it")
            }
            addHeader("Content-Type", "application/json")
            addHeader("X-Platform", "android")
        }.build()
        chain.proceed(request)
    }

    @Provides
    @Singleton
    fun provideOkHttpClient(
        authInterceptor: Interceptor
    ): OkHttpClient {
        val loggingInterceptor = HttpLoggingInterceptor().apply {
            level = if (BuildConfig.DEBUG) {
                HttpLoggingInterceptor.Level.BODY
            } else {
                HttpLoggingInterceptor.Level.NONE
            }
        }

        // Modern TLS configuration for better compatibility
        val modernTls = ConnectionSpec.Builder(ConnectionSpec.MODERN_TLS)
            .tlsVersions(TlsVersion.TLS_1_2, TlsVersion.TLS_1_3)
            .build()

        val builder = OkHttpClient.Builder()
            .addInterceptor(authInterceptor)
            .addInterceptor(loggingInterceptor)
            .connectionSpecs(listOf(modernTls, ConnectionSpec.CLEARTEXT))
            .connectTimeout(30, TimeUnit.SECONDS)
            .readTimeout(30, TimeUnit.SECONDS)
            .writeTimeout(30, TimeUnit.SECONDS)
            .retryOnConnectionFailure(true)

        // For DEBUG builds only: trust all certificates to bypass SSL issues
        // This helps diagnose SSL problems on devices with outdated CA stores
        if (BuildConfig.DEBUG) {
            try {
                val trustAllCerts = arrayOf<TrustManager>(object : X509TrustManager {
                    override fun checkClientTrusted(chain: Array<X509Certificate>, authType: String) {}
                    override fun checkServerTrusted(chain: Array<X509Certificate>, authType: String) {}
                    override fun getAcceptedIssuers(): Array<X509Certificate> = arrayOf()
                })
                val sslContext = SSLContext.getInstance("TLS")
                sslContext.init(null, trustAllCerts, SecureRandom())
                builder.sslSocketFactory(sslContext.socketFactory, trustAllCerts[0] as X509TrustManager)
                builder.hostnameVerifier { _, _ -> true }
            } catch (e: Exception) {
                // If SSL bypass fails, continue with default SSL
                android.util.Log.w("NetworkModule", "Failed to configure debug SSL: ${e.message}")
            }
        }

        return builder.build()
    }

    @Provides
    @Singleton
    fun provideRetrofit(
        okHttpClient: OkHttpClient,
        json: Json
    ): Retrofit {
        val contentType = "application/json".toMediaType()
        return Retrofit.Builder()
            .baseUrl(BuildConfig.BASE_URL)
            .client(okHttpClient)
            .addConverterFactory(json.asConverterFactory(contentType))
            .build()
    }

    @Provides
    @Singleton
    fun provideEnlikoApi(retrofit: Retrofit): EnlikoApi {
        return retrofit.create(EnlikoApi::class.java)
    }

    // ==================== DATABASE ====================

    @Provides
    @Singleton
    fun provideDatabase(
        @ApplicationContext context: Context
    ): EnlikoDatabase {
        return Room.databaseBuilder(
            context,
            EnlikoDatabase::class.java,
            EnlikoDatabase.DATABASE_NAME
        )
        .fallbackToDestructiveMigration()
        .build()
    }

    // ==================== DAOs ====================

    @Provides
    @Singleton
    fun providePositionDao(db: EnlikoDatabase): PositionDao = db.positionDao()

    @Provides
    @Singleton
    fun provideTradeDao(db: EnlikoDatabase): TradeDao = db.tradeDao()

    @Provides
    @Singleton
    fun provideSignalDao(db: EnlikoDatabase): SignalDao = db.signalDao()

    @Provides
    @Singleton
    fun provideOrderDao(db: EnlikoDatabase): OrderDao = db.orderDao()

    @Provides
    @Singleton
    fun provideStrategySettingsDao(db: EnlikoDatabase): StrategySettingsDao = db.strategySettingsDao()

    @Provides
    @Singleton
    fun provideUserSettingsDao(db: EnlikoDatabase): UserSettingsDao = db.userSettingsDao()

    @Provides
    @Singleton
    fun provideApiKeyDao(db: EnlikoDatabase): ApiKeyDao = db.apiKeyDao()

    @Provides
    @Singleton
    fun provideBalanceCacheDao(db: EnlikoDatabase): BalanceCacheDao = db.balanceCacheDao()

    @Provides
    @Singleton
    fun provideTradeStatsCacheDao(db: EnlikoDatabase): TradeStatsCacheDao = db.tradeStatsCacheDao()

    @Provides
    @Singleton
    fun provideScreenerCoinDao(db: EnlikoDatabase): ScreenerCoinDao = db.screenerCoinDao()

    @Provides
    @Singleton
    fun provideSyncMetadataDao(db: EnlikoDatabase): SyncMetadataDao = db.syncMetadataDao()

    @Provides
    @Singleton
    fun provideActivityLogDao(db: EnlikoDatabase): ActivityLogDao = db.activityLogDao()

    // ==================== REPOSITORIES & SERVICES ====================

    @Provides
    @Singleton
    fun providePreferencesRepository(
        @ApplicationContext context: Context
    ): PreferencesRepository {
        return PreferencesRepository(context)
    }

    @Provides
    @Singleton
    fun provideSecurePreferencesRepository(
        @ApplicationContext context: Context
    ): SecurePreferencesRepository {
        return SecurePreferencesRepository(context)
    }

    @Provides
    @Singleton
    fun provideWebSocketService(
        okHttpClient: OkHttpClient
    ): WebSocketService {
        return WebSocketService(okHttpClient)
    }

    @Provides
    @Singleton
    fun provideActivityService(
        api: EnlikoApi
    ): ActivityService {
        return ActivityService(api)
    }

    @Provides
    @Singleton
    fun provideSpotService(
        api: EnlikoApi
    ): SpotService {
        return SpotService(api)
    }
}
