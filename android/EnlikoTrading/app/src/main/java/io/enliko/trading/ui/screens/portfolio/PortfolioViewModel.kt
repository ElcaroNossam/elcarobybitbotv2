package io.enliko.trading.ui.screens.portfolio

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import dagger.hilt.android.lifecycle.HiltViewModel
import io.enliko.trading.data.api.BalanceData
import io.enliko.trading.data.api.EnlikoApi
import io.enliko.trading.data.api.PositionData
import io.enliko.trading.data.api.TradeStatsData
import io.enliko.trading.data.models.*
import io.enliko.trading.data.repository.PreferencesRepository
import kotlinx.coroutines.flow.*
import kotlinx.coroutines.launch
import java.time.LocalDate
import java.time.ZoneOffset
import java.time.format.DateTimeFormatter
import javax.inject.Inject

enum class PortfolioTab {
    OVERVIEW, SPOT, FUTURES
}

enum class PeriodFilter(val value: String, val label: String) {
    DAY_1("1d", "24h"),
    WEEK_1("1w", "7D"),
    MONTH_1("1m", "30D"),
    MONTH_3("3m", "90D"),
    YEAR_1("1y", "1Y"),
    CUSTOM("custom", "Custom")
}

data class PortfolioUiState(
    val isLoading: Boolean = true,
    val balance: BalanceData? = null,
    val positions: List<PositionData> = emptyList(),
    val stats: TradeStatsData? = null,
    val error: String? = null,
    val accountType: String = "demo",
    val exchange: String = "bybit",
    // New portfolio state
    val selectedTab: PortfolioTab = PortfolioTab.OVERVIEW,
    val selectedPeriod: PeriodFilter = PeriodFilter.WEEK_1,
    val portfolioSummary: PortfolioSummary? = null,
    val spotPortfolio: SpotPortfolio? = null,
    val futuresPortfolio: FuturesPortfolio? = null,
    val candles: List<CandleCluster> = emptyList(),
    val selectedCandle: CandleCluster? = null,
    val showCandleDetail: Boolean = false,
    // Custom date range
    val customStartDate: LocalDate? = null,
    val customEndDate: LocalDate? = null,
    val showDatePicker: Boolean = false
)

@HiltViewModel
class PortfolioViewModel @Inject constructor(
    private val api: EnlikoApi,
    private val preferencesRepository: PreferencesRepository
) : ViewModel() {

    private val _uiState = MutableStateFlow(PortfolioUiState())
    val uiState: StateFlow<PortfolioUiState> = _uiState.asStateFlow()

    init {
        viewModelScope.launch {
            combine(
                preferencesRepository.accountType,
                preferencesRepository.exchange
            ) { accountType, exchange ->
                Pair(accountType, exchange)
            }.collect { (accountType, exchange) ->
                _uiState.update { it.copy(accountType = accountType, exchange = exchange) }
                refresh()
            }
        }
    }

    fun selectTab(tab: PortfolioTab) {
        _uiState.update { it.copy(selectedTab = tab) }
        when (tab) {
            PortfolioTab.SPOT -> loadSpotPortfolio()
            PortfolioTab.FUTURES -> loadFuturesPortfolio()
            else -> refresh()
        }
    }

    fun selectPeriod(period: PeriodFilter) {
        if (period == PeriodFilter.CUSTOM) {
            _uiState.update { it.copy(showDatePicker = true) }
        } else {
            _uiState.update { it.copy(selectedPeriod = period, showDatePicker = false) }
            loadPortfolioSummary()
        }
    }

    fun setCustomDateRange(start: LocalDate, end: LocalDate) {
        _uiState.update { 
            it.copy(
                customStartDate = start,
                customEndDate = end,
                selectedPeriod = PeriodFilter.CUSTOM,
                showDatePicker = false
            )
        }
        loadPortfolioSummary()
    }

    fun dismissDatePicker() {
        _uiState.update { it.copy(showDatePicker = false) }
    }

    fun selectCandle(candle: CandleCluster) {
        _uiState.update { it.copy(selectedCandle = candle, showCandleDetail = true) }
    }

    fun dismissCandleDetail() {
        _uiState.update { it.copy(showCandleDetail = false, selectedCandle = null) }
    }

    fun refresh() {
        viewModelScope.launch {
            _uiState.update { it.copy(isLoading = true, error = null) }
            try {
                val accountType = _uiState.value.accountType
                
                // Fetch balance and positions (existing)
                val balanceResult = api.getBalance(accountType = accountType)
                val positionsResult = api.getPositions(accountType = accountType)
                val statsResult = api.getTradeStats(accountType = accountType)
                
                _uiState.update { state ->
                    state.copy(
                        isLoading = false,
                        balance = balanceResult.body()?.data,
                        positions = positionsResult.body()?.data ?: emptyList(),
                        stats = statsResult.body()?.data
                    )
                }
                
                // Load portfolio summary
                loadPortfolioSummary()
            } catch (e: Exception) {
                _uiState.update { 
                    it.copy(isLoading = false, error = e.message) 
                }
            }
        }
    }

    private fun loadPortfolioSummary() {
        viewModelScope.launch {
            try {
                val state = _uiState.value
                val customStart = if (state.selectedPeriod == PeriodFilter.CUSTOM && state.customStartDate != null) {
                    state.customStartDate.atStartOfDay().toInstant(ZoneOffset.UTC).toString()
                } else null
                val customEnd = if (state.selectedPeriod == PeriodFilter.CUSTOM && state.customEndDate != null) {
                    state.customEndDate.atStartOfDay().toInstant(ZoneOffset.UTC).toString()
                } else null
                
                val result = api.getPortfolioSummary(
                    accountType = state.accountType,
                    period = state.selectedPeriod.value,
                    customStart = customStart,
                    customEnd = customEnd
                )
                
                result.body()?.let { summary ->
                    _uiState.update { 
                        it.copy(
                            portfolioSummary = summary,
                            spotPortfolio = summary.spot,
                            futuresPortfolio = summary.futures,
                            candles = summary.candles
                        ) 
                    }
                }
            } catch (e: Exception) {
                // Silent fail for summary, main data already loaded
            }
        }
    }

    private fun loadSpotPortfolio() {
        viewModelScope.launch {
            try {
                val result = api.getSpotPortfolio(_uiState.value.accountType)
                result.body()?.let { spot ->
                    _uiState.update { it.copy(spotPortfolio = spot) }
                }
            } catch (e: Exception) {
                // Silent fail
            }
        }
    }

    private fun loadFuturesPortfolio() {
        viewModelScope.launch {
            try {
                val result = api.getFuturesPortfolio(_uiState.value.accountType)
                result.body()?.let { futures ->
                    _uiState.update { it.copy(futuresPortfolio = futures) }
                }
            } catch (e: Exception) {
                // Silent fail
            }
        }
    }

    fun switchAccountType(accountType: String) {
        viewModelScope.launch {
            preferencesRepository.saveAccountType(accountType)
            try {
                api.switchAccountType(mapOf("account_type" to accountType))
            } catch (e: Exception) {
                // Local save already done
            }
        }
    }

    fun closePosition(symbol: String, side: String) {
        viewModelScope.launch {
            try {
                val request = io.enliko.trading.data.api.ClosePositionRequest(
                    symbol = symbol,
                    side = side,
                    accountType = _uiState.value.accountType
                )
                api.closePosition(request)
                refresh()
            } catch (e: Exception) {
                _uiState.update { it.copy(error = e.message) }
            }
        }
    }

    fun closeAllPositions() {
        viewModelScope.launch {
            try {
                api.closeAllPositions(_uiState.value.accountType)
                refresh()
            } catch (e: Exception) {
                _uiState.update { it.copy(error = e.message) }
            }
        }
    }
}
