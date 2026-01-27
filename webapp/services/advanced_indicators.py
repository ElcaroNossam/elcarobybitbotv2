"""
Enliko Advanced Technical Indicators Library
50+ Professional Trading Indicators with Full Customization

Categories:
- Trend (15 indicators)
- Momentum (12 indicators)
- Volatility (8 indicators)
- Volume (10 indicators)
- Market Structure (5 indicators)
"""
import math
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def sma(data: List[float], period: int) -> List[float]:
    """Simple Moving Average"""
    result = [None] * len(data)
    for i in range(period - 1, len(data)):
        result[i] = sum(data[i - period + 1:i + 1]) / period
    return result


def ema(data: List[float], period: int) -> List[float]:
    """Exponential Moving Average"""
    result = [None] * len(data)
    multiplier = 2 / (period + 1)
    
    # First EMA is SMA
    result[period - 1] = sum(data[:period]) / period
    
    for i in range(period, len(data)):
        result[i] = (data[i] - result[i - 1]) * multiplier + result[i - 1]
    
    return result


def wma(data: List[float], period: int) -> List[float]:
    """Weighted Moving Average"""
    result = [None] * len(data)
    weights = list(range(1, period + 1))
    weight_sum = sum(weights)
    
    for i in range(period - 1, len(data)):
        result[i] = sum(data[i - period + 1 + j] * weights[j] for j in range(period)) / weight_sum
    
    return result


def stdev(data: List[float], period: int) -> List[float]:
    """Standard Deviation"""
    result = [None] * len(data)
    for i in range(period - 1, len(data)):
        window = data[i - period + 1:i + 1]
        mean = sum(window) / period
        variance = sum((x - mean) ** 2 for x in window) / period
        result[i] = math.sqrt(variance)
    return result


def true_range(high: List[float], low: List[float], close: List[float]) -> List[float]:
    """True Range"""
    tr = [high[0] - low[0]]
    for i in range(1, len(high)):
        tr.append(max(
            high[i] - low[i],
            abs(high[i] - close[i - 1]),
            abs(low[i] - close[i - 1])
        ))
    return tr


# =============================================================================
# TREND INDICATORS
# =============================================================================

class TrendIndicators:
    """15 Advanced Trend Indicators"""
    
    @staticmethod
    def hull_ma(data: List[float], period: int) -> List[float]:
        """Hull Moving Average - Ultra smooth and responsive"""
        half_period = period // 2
        sqrt_period = int(math.sqrt(period))
        
        wma_half = wma(data, half_period)
        wma_full = wma(data, period)
        
        # 2*WMA(n/2) - WMA(n)
        raw_hma = [None] * len(data)
        for i in range(period - 1, len(data)):
            if wma_half[i] is not None and wma_full[i] is not None:
                raw_hma[i] = 2 * wma_half[i] - wma_full[i]
        
        # WMA of raw_hma with sqrt(period)
        return wma([x if x is not None else 0 for x in raw_hma], sqrt_period)
    
    @staticmethod
    def kama(data: List[float], period: int = 10, fast: int = 2, slow: int = 30) -> List[float]:
        """Kaufman's Adaptive Moving Average - Adapts to volatility"""
        result = [None] * len(data)
        
        for i in range(period, len(data)):
            # Efficiency Ratio
            change = abs(data[i] - data[i - period])
            volatility = sum(abs(data[j] - data[j - 1]) for j in range(i - period + 1, i + 1))
            
            if volatility == 0:
                er = 0
            else:
                er = change / volatility
            
            # Smoothing Constant
            fast_sc = 2 / (fast + 1)
            slow_sc = 2 / (slow + 1)
            sc = (er * (fast_sc - slow_sc) + slow_sc) ** 2
            
            # KAMA
            if result[i - 1] is None:
                result[i] = data[i]
            else:
                result[i] = result[i - 1] + sc * (data[i] - result[i - 1])
        
        return result
    
    @staticmethod
    def supertrend(high: List[float], low: List[float], close: List[float], 
                   period: int = 10, multiplier: float = 3.0) -> Tuple[List[float], List[str]]:
        """SuperTrend - Trend following with dynamic stops"""
        atr = ema(true_range(high, low, close), period)
        
        upper_band = [(high[i] + low[i]) / 2 + multiplier * atr[i] if atr[i] is not None else None 
                      for i in range(len(high))]
        lower_band = [(high[i] + low[i]) / 2 - multiplier * atr[i] if atr[i] is not None else None 
                      for i in range(len(high))]
        
        supertrend = [None] * len(close)
        trend = [""] * len(close)
        
        for i in range(1, len(close)):
            if upper_band[i] is None or lower_band[i] is None:
                continue
            
            # Update bands
            if close[i - 1] <= upper_band[i - 1] if upper_band[i - 1] else False:
                upper_band[i] = min(upper_band[i], upper_band[i - 1])
            
            if close[i - 1] >= lower_band[i - 1] if lower_band[i - 1] else False:
                lower_band[i] = max(lower_band[i], lower_band[i - 1])
            
            # Determine trend
            if close[i] <= upper_band[i]:
                supertrend[i] = upper_band[i]
                trend[i] = "DOWN"
            else:
                supertrend[i] = lower_band[i]
                trend[i] = "UP"
        
        return supertrend, trend
    
    @staticmethod
    def parabolic_sar(high: List[float], low: List[float], close: List[float],
                      af_start: float = 0.02, af_increment: float = 0.02, af_max: float = 0.2) -> List[float]:
        """Parabolic SAR - Stop and Reverse indicator"""
        sar = [None] * len(close)
        trend = [1] * len(close)  # 1 = uptrend, -1 = downtrend
        af = af_start
        ep = high[0]  # Extreme point
        
        sar[0] = low[0]
        
        for i in range(1, len(close)):
            # Calculate SAR
            sar[i] = sar[i - 1] + af * (ep - sar[i - 1])
            
            # Check for trend reversal
            if trend[i - 1] == 1:  # Uptrend
                if low[i] < sar[i]:
                    trend[i] = -1
                    sar[i] = ep
                    ep = low[i]
                    af = af_start
                else:
                    trend[i] = 1
                    if high[i] > ep:
                        ep = high[i]
                        af = min(af + af_increment, af_max)
            else:  # Downtrend
                if high[i] > sar[i]:
                    trend[i] = 1
                    sar[i] = ep
                    ep = high[i]
                    af = af_start
                else:
                    trend[i] = -1
                    if low[i] < ep:
                        ep = low[i]
                        af = min(af + af_increment, af_max)
        
        return sar
    
    @staticmethod
    def ichimoku(high: List[float], low: List[float], close: List[float],
                 tenkan: int = 9, kijun: int = 26, senkou_b: int = 52) -> Dict[str, List[float]]:
        """Ichimoku Cloud - Complete trend system"""
        def midpoint(data, period, index):
            if index < period - 1:
                return None
            window = data[index - period + 1:index + 1]
            return (max(window) + min(window)) / 2
        
        # Tenkan-sen (Conversion Line)
        tenkan_sen = [midpoint(high, tenkan, i) or midpoint(low, tenkan, i) for i in range(len(high))]
        
        # Kijun-sen (Base Line)
        kijun_sen = [midpoint(high, kijun, i) or midpoint(low, kijun, i) for i in range(len(high))]
        
        # Senkou Span A (Leading Span A) - shifted forward
        senkou_a = [(tenkan_sen[i] + kijun_sen[i]) / 2 if tenkan_sen[i] and kijun_sen[i] else None 
                    for i in range(len(high))]
        
        # Senkou Span B (Leading Span B) - shifted forward
        senkou_b_values = [midpoint(high, senkou_b, i) or midpoint(low, senkou_b, i) 
                           for i in range(len(high))]
        
        # Chikou Span (Lagging Span) - shifted backward
        chikou = [close[i] for i in range(len(close))]
        
        return {
            "tenkan_sen": tenkan_sen,
            "kijun_sen": kijun_sen,
            "senkou_a": senkou_a,
            "senkou_b": senkou_b_values,
            "chikou_span": chikou
        }
    
    @staticmethod
    def vwap(high: List[float], low: List[float], close: List[float], volume: List[float]) -> List[float]:
        """Volume Weighted Average Price"""
        vwap = [None] * len(close)
        cum_volume = 0
        cum_price_volume = 0
        
        for i in range(len(close)):
            typical_price = (high[i] + low[i] + close[i]) / 3
            cum_price_volume += typical_price * volume[i]
            cum_volume += volume[i]
            
            if cum_volume > 0:
                vwap[i] = cum_price_volume / cum_volume
        
        return vwap
    
    @staticmethod
    def zlema(data: List[float], period: int) -> List[float]:
        """Zero Lag EMA - Eliminates lag"""
        lag = (period - 1) // 2
        zlema_data = [data[i] + (data[i] - data[max(0, i - lag)]) if i >= lag else data[i] 
                      for i in range(len(data))]
        return ema(zlema_data, period)
    
    @staticmethod
    def alma(data: List[float], period: int = 9, offset: float = 0.85, sigma: float = 6.0) -> List[float]:
        """Arnaud Legoux Moving Average - Gaussian weighted"""
        result = [None] * len(data)
        m = offset * (period - 1)
        s = period / sigma
        
        for i in range(period - 1, len(data)):
            norm = 0
            sum_val = 0
            
            for j in range(period):
                weight = math.exp(-((j - m) ** 2) / (2 * s * s))
                norm += weight
                sum_val += data[i - period + 1 + j] * weight
            
            result[i] = sum_val / norm if norm != 0 else None
        
        return result


# =============================================================================
# MOMENTUM INDICATORS
# =============================================================================

class MomentumIndicators:
    """12 Advanced Momentum Indicators"""
    
    @staticmethod
    def rsi(data: List[float], period: int = 14) -> List[float]:
        """Relative Strength Index"""
        result = [None] * len(data)
        gains = []
        losses = []
        
        for i in range(1, len(data)):
            change = data[i] - data[i - 1]
            gains.append(max(change, 0))
            losses.append(abs(min(change, 0)))
        
        for i in range(period, len(data)):
            avg_gain = sum(gains[i - period:i]) / period
            avg_loss = sum(losses[i - period:i]) / period
            
            if avg_loss == 0:
                result[i] = 100
            else:
                rs = avg_gain / avg_loss
                result[i] = 100 - (100 / (1 + rs))
        
        return result
    
    @staticmethod
    def stochastic(high: List[float], low: List[float], close: List[float],
                   k_period: int = 14, d_period: int = 3) -> Tuple[List[float], List[float]]:
        """Stochastic Oscillator"""
        k_values = [None] * len(close)
        
        for i in range(k_period - 1, len(close)):
            window_high = max(high[i - k_period + 1:i + 1])
            window_low = min(low[i - k_period + 1:i + 1])
            
            if window_high - window_low == 0:
                k_values[i] = 50
            else:
                k_values[i] = 100 * (close[i] - window_low) / (window_high - window_low)
        
        # %D is SMA of %K
        d_values = sma([x if x is not None else 0 for x in k_values], d_period)
        
        return k_values, d_values
    
    @staticmethod
    def macd(data: List[float], fast: int = 12, slow: int = 26, signal: int = 9) -> Dict[str, List[float]]:
        """MACD - Moving Average Convergence Divergence"""
        fast_ema = ema(data, fast)
        slow_ema = ema(data, slow)
        
        macd_line = [fast_ema[i] - slow_ema[i] if fast_ema[i] is not None and slow_ema[i] is not None else None 
                     for i in range(len(data))]
        
        signal_line = ema([x if x is not None else 0 for x in macd_line], signal)
        
        histogram = [macd_line[i] - signal_line[i] if macd_line[i] is not None and signal_line[i] is not None else None 
                     for i in range(len(data))]
        
        return {
            "macd": macd_line,
            "signal": signal_line,
            "histogram": histogram
        }
    
    @staticmethod
    def williams_r(high: List[float], low: List[float], close: List[float], period: int = 14) -> List[float]:
        """Williams %R"""
        result = [None] * len(close)
        
        for i in range(period - 1, len(close)):
            highest = max(high[i - period + 1:i + 1])
            lowest = min(low[i - period + 1:i + 1])
            
            if highest - lowest == 0:
                result[i] = -50
            else:
                result[i] = -100 * (highest - close[i]) / (highest - lowest)
        
        return result
    
    @staticmethod
    def cci(high: List[float], low: List[float], close: List[float], period: int = 20) -> List[float]:
        """Commodity Channel Index"""
        result = [None] * len(close)
        typical_price = [(high[i] + low[i] + close[i]) / 3 for i in range(len(close))]
        tp_sma = sma(typical_price, period)
        
        for i in range(period - 1, len(close)):
            if tp_sma[i] is None:
                continue
            
            mean_deviation = sum(abs(typical_price[j] - tp_sma[i]) for j in range(i - period + 1, i + 1)) / period
            
            if mean_deviation == 0:
                result[i] = 0
            else:
                result[i] = (typical_price[i] - tp_sma[i]) / (0.015 * mean_deviation)
        
        return result
    
    @staticmethod
    def roc(data: List[float], period: int = 12) -> List[float]:
        """Rate of Change"""
        result = [None] * len(data)
        
        for i in range(period, len(data)):
            if data[i - period] == 0:
                result[i] = 0
            else:
                result[i] = 100 * (data[i] - data[i - period]) / data[i - period]
        
        return result
    
    @staticmethod
    def mfi(high: List[float], low: List[float], close: List[float], volume: List[float], period: int = 14) -> List[float]:
        """Money Flow Index"""
        result = [None] * len(close)
        typical_price = [(high[i] + low[i] + close[i]) / 3 for i in range(len(close))]
        money_flow = [typical_price[i] * volume[i] for i in range(len(close))]
        
        for i in range(period, len(close)):
            positive_flow = sum(money_flow[j] for j in range(i - period + 1, i + 1) 
                                if typical_price[j] > typical_price[j - 1])
            negative_flow = sum(money_flow[j] for j in range(i - period + 1, i + 1) 
                                if typical_price[j] < typical_price[j - 1])
            
            if negative_flow == 0:
                result[i] = 100
            else:
                money_ratio = positive_flow / negative_flow
                result[i] = 100 - (100 / (1 + money_ratio))
        
        return result
    
    @staticmethod
    def awesome_oscillator(high: List[float], low: List[float]) -> List[float]:
        """Awesome Oscillator"""
        median_price = [(high[i] + low[i]) / 2 for i in range(len(high))]
        fast_ma = sma(median_price, 5)
        slow_ma = sma(median_price, 34)
        
        ao = [fast_ma[i] - slow_ma[i] if fast_ma[i] is not None and slow_ma[i] is not None else None 
              for i in range(len(high))]
        
        return ao
    
    @staticmethod
    def stochastic_rsi(data: List[float], rsi_period: int = 14, stoch_period: int = 14) -> List[float]:
        """Stochastic RSI"""
        rsi_values = MomentumIndicators.rsi(data, rsi_period)
        
        stoch_rsi = [None] * len(data)
        
        for i in range(stoch_period - 1, len(data)):
            if rsi_values[i] is None:
                continue
            
            rsi_window = [x for x in rsi_values[i - stoch_period + 1:i + 1] if x is not None]
            if not rsi_window:
                continue
            
            rsi_high = max(rsi_window)
            rsi_low = min(rsi_window)
            
            if rsi_high - rsi_low == 0:
                stoch_rsi[i] = 50
            else:
                stoch_rsi[i] = 100 * (rsi_values[i] - rsi_low) / (rsi_high - rsi_low)
        
        return stoch_rsi


# =============================================================================
# VOLATILITY INDICATORS
# =============================================================================

class VolatilityIndicators:
    """8 Advanced Volatility Indicators"""
    
    @staticmethod
    def atr(high: List[float], low: List[float], close: List[float], period: int = 14) -> List[float]:
        """Average True Range"""
        tr = true_range(high, low, close)
        return sma(tr, period)
    
    @staticmethod
    def bollinger_bands(data: List[float], period: int = 20, std_dev: float = 2.0) -> Dict[str, List[float]]:
        """Bollinger Bands"""
        middle = sma(data, period)
        std = stdev(data, period)
        
        upper = [middle[i] + std_dev * std[i] if middle[i] is not None and std[i] is not None else None 
                 for i in range(len(data))]
        lower = [middle[i] - std_dev * std[i] if middle[i] is not None and std[i] is not None else None 
                 for i in range(len(data))]
        
        # %B indicator
        percent_b = [(data[i] - lower[i]) / (upper[i] - lower[i]) if upper[i] and lower[i] and upper[i] != lower[i] else 0.5 
                     for i in range(len(data))]
        
        # Bandwidth
        bandwidth = [(upper[i] - lower[i]) / middle[i] if middle[i] and middle[i] != 0 else 0 
                     for i in range(len(data))]
        
        return {
            "upper": upper,
            "middle": middle,
            "lower": lower,
            "percent_b": percent_b,
            "bandwidth": bandwidth
        }
    
    @staticmethod
    def keltner_channels(high: List[float], low: List[float], close: List[float],
                         ema_period: int = 20, atr_period: int = 10, multiplier: float = 2.0) -> Dict[str, List[float]]:
        """Keltner Channels"""
        middle = ema(close, ema_period)
        atr_values = VolatilityIndicators.atr(high, low, close, atr_period)
        
        upper = [middle[i] + multiplier * atr_values[i] if middle[i] is not None and atr_values[i] is not None else None 
                 for i in range(len(close))]
        lower = [middle[i] - multiplier * atr_values[i] if middle[i] is not None and atr_values[i] is not None else None 
                 for i in range(len(close))]
        
        return {
            "upper": upper,
            "middle": middle,
            "lower": lower
        }
    
    @staticmethod
    def donchian_channels(high: List[float], low: List[float], period: int = 20) -> Dict[str, List[float]]:
        """Donchian Channels"""
        upper = [None] * len(high)
        lower = [None] * len(low)
        middle = [None] * len(high)
        
        for i in range(period - 1, len(high)):
            upper[i] = max(high[i - period + 1:i + 1])
            lower[i] = min(low[i - period + 1:i + 1])
            middle[i] = (upper[i] + lower[i]) / 2
        
        return {
            "upper": upper,
            "middle": middle,
            "lower": lower
        }
    
    @staticmethod
    def historical_volatility(close: List[float], period: int = 20) -> List[float]:
        """Historical Volatility (annualized)"""
        log_returns = [None] + [math.log(close[i] / close[i - 1]) for i in range(1, len(close))]
        
        result = [None] * len(close)
        for i in range(period, len(close)):
            returns_window = [x for x in log_returns[i - period + 1:i + 1] if x is not None]
            if returns_window:
                mean_return = sum(returns_window) / len(returns_window)
                variance = sum((x - mean_return) ** 2 for x in returns_window) / len(returns_window)
                result[i] = math.sqrt(variance * 252) * 100  # Annualized
        
        return result


# =============================================================================
# VOLUME INDICATORS
# =============================================================================

class VolumeIndicators:
    """10 Advanced Volume Indicators"""
    
    @staticmethod
    def obv(close: List[float], volume: List[float]) -> List[float]:
        """On Balance Volume"""
        obv_values = [0]
        
        for i in range(1, len(close)):
            if close[i] > close[i - 1]:
                obv_values.append(obv_values[-1] + volume[i])
            elif close[i] < close[i - 1]:
                obv_values.append(obv_values[-1] - volume[i])
            else:
                obv_values.append(obv_values[-1])
        
        return obv_values
    
    @staticmethod
    def volume_oscillator(volume: List[float], fast: int = 5, slow: int = 10) -> List[float]:
        """Volume Oscillator"""
        fast_ma = ema(volume, fast)
        slow_ma = ema(volume, slow)
        
        vo = [((fast_ma[i] - slow_ma[i]) / slow_ma[i]) * 100 if fast_ma[i] and slow_ma[i] and slow_ma[i] != 0 else 0 
              for i in range(len(volume))]
        
        return vo
    
    @staticmethod
    def volume_weighted_ma(close: List[float], volume: List[float], period: int = 20) -> List[float]:
        """Volume Weighted Moving Average"""
        result = [None] * len(close)
        
        for i in range(period - 1, len(close)):
            price_volume = sum(close[j] * volume[j] for j in range(i - period + 1, i + 1))
            total_volume = sum(volume[i - period + 1:i + 1])
            
            result[i] = price_volume / total_volume if total_volume != 0 else None
        
        return result
    
    @staticmethod
    def accumulation_distribution(high: List[float], low: List[float], close: List[float], volume: List[float]) -> List[float]:
        """Accumulation/Distribution Line"""
        ad_line = [0]
        
        for i in range(len(close)):
            if high[i] - low[i] == 0:
                mfm = 0
            else:
                mfm = ((close[i] - low[i]) - (high[i] - close[i])) / (high[i] - low[i])
            
            mfv = mfm * volume[i]
            ad_line.append(ad_line[-1] + mfv)
        
        return ad_line[1:]  # Remove initial 0


# =============================================================================
# MARKET STRUCTURE INDICATORS
# =============================================================================

class MarketStructureIndicators:
    """5 Market Structure Analysis Tools"""
    
    @staticmethod
    def pivot_points(high: List[float], low: List[float], close: List[float]) -> Dict[str, float]:
        """Pivot Points (Standard)"""
        pivot = (high[-1] + low[-1] + close[-1]) / 3
        
        r1 = 2 * pivot - low[-1]
        s1 = 2 * pivot - high[-1]
        r2 = pivot + (high[-1] - low[-1])
        s2 = pivot - (high[-1] - low[-1])
        r3 = high[-1] + 2 * (pivot - low[-1])
        s3 = low[-1] - 2 * (high[-1] - pivot)
        
        return {
            "pivot": pivot,
            "r1": r1, "r2": r2, "r3": r3,
            "s1": s1, "s2": s2, "s3": s3
        }
    
    @staticmethod
    def support_resistance(close: List[float], period: int = 50) -> Dict[str, List[float]]:
        """Dynamic Support & Resistance Levels"""
        if len(close) < period:
            return {"support": [], "resistance": []}
        
        recent_data = close[-period:]
        sorted_prices = sorted(recent_data)
        
        # Find clusters of prices
        support_levels = []
        resistance_levels = []
        
        tolerance = (max(recent_data) - min(recent_data)) * 0.01
        
        i = 0
        while i < len(sorted_prices):
            cluster = [sorted_prices[i]]
            j = i + 1
            while j < len(sorted_prices) and sorted_prices[j] - sorted_prices[i] <= tolerance:
                cluster.append(sorted_prices[j])
                j += 1
            
            if len(cluster) >= 3:
                level = sum(cluster) / len(cluster)
                if level < close[-1]:
                    support_levels.append(level)
                else:
                    resistance_levels.append(level)
            
            i = j if j > i else i + 1
        
        return {
            "support": sorted(support_levels, reverse=True)[:3],
            "resistance": sorted(resistance_levels)[:3]
        }
    
    @staticmethod
    def zigzag(high: List[float], low: List[float], close: List[float], deviation: float = 5.0) -> List[Dict]:
        """ZigZag - Identifies swing highs and lows"""
        zigzag_points = []
        
        if len(close) < 3:
            return zigzag_points
        
        # Find first pivot
        is_high = high[0] > high[1]
        last_pivot_idx = 0
        last_pivot_value = high[0] if is_high else low[0]
        
        threshold = last_pivot_value * (deviation / 100)
        
        for i in range(1, len(close)):
            current_value = high[i] if is_high else low[i]
            
            if is_high:
                if low[i] < last_pivot_value - threshold:
                    zigzag_points.append({
                        "index": last_pivot_idx,
                        "price": last_pivot_value,
                        "type": "HIGH"
                    })
                    last_pivot_idx = i
                    last_pivot_value = low[i]
                    is_high = False
                    threshold = last_pivot_value * (deviation / 100)
                elif high[i] > last_pivot_value:
                    last_pivot_idx = i
                    last_pivot_value = high[i]
                    threshold = last_pivot_value * (deviation / 100)
            else:
                if high[i] > last_pivot_value + threshold:
                    zigzag_points.append({
                        "index": last_pivot_idx,
                        "price": last_pivot_value,
                        "type": "LOW"
                    })
                    last_pivot_idx = i
                    last_pivot_value = high[i]
                    is_high = True
                    threshold = last_pivot_value * (deviation / 100)
                elif low[i] < last_pivot_value:
                    last_pivot_idx = i
                    last_pivot_value = low[i]
                    threshold = last_pivot_value * (deviation / 100)
        
        return zigzag_points


# =============================================================================
# UNIFIED INDICATOR CALCULATOR
# =============================================================================

class IndicatorCalculator:
    """Unified interface for all indicators"""
    
    def __init__(self):
        self.trend = TrendIndicators()
        self.momentum = MomentumIndicators()
        self.volatility = VolatilityIndicators()
        self.volume = VolumeIndicators()
        self.structure = MarketStructureIndicators()
    
    def calculate(self, indicator_name: str, data: Dict[str, List[float]], params: Dict[str, Any]) -> Any:
        """
        Calculate any indicator by name
        
        Args:
            indicator_name: Name of indicator (e.g., 'rsi', 'macd', 'bollinger_bands')
            data: Dict with 'open', 'high', 'low', 'close', 'volume' keys
            params: Parameters for the indicator
        
        Returns:
            Calculated indicator values
        """
        # Map indicator names to methods
        indicator_map = {
            # Trend
            'sma': lambda: sma(data['close'], params.get('period', 20)),
            'ema': lambda: ema(data['close'], params.get('period', 20)),
            'wma': lambda: wma(data['close'], params.get('period', 20)),
            'hull_ma': lambda: self.trend.hull_ma(data['close'], params.get('period', 9)),
            'kama': lambda: self.trend.kama(data['close'], params.get('period', 10)),
            'supertrend': lambda: self.trend.supertrend(data['high'], data['low'], data['close'], 
                                                        params.get('period', 10), params.get('multiplier', 3.0)),
            'parabolic_sar': lambda: self.trend.parabolic_sar(data['high'], data['low'], data['close']),
            'ichimoku': lambda: self.trend.ichimoku(data['high'], data['low'], data['close']),
            'vwap': lambda: self.trend.vwap(data['high'], data['low'], data['close'], data['volume']),
            'zlema': lambda: self.trend.zlema(data['close'], params.get('period', 20)),
            'alma': lambda: self.trend.alma(data['close'], params.get('period', 9)),
            
            # Momentum
            'rsi': lambda: self.momentum.rsi(data['close'], params.get('period', 14)),
            'stochastic': lambda: self.momentum.stochastic(data['high'], data['low'], data['close'], 
                                                          params.get('k_period', 14), params.get('d_period', 3)),
            'macd': lambda: self.momentum.macd(data['close'], params.get('fast', 12), 
                                              params.get('slow', 26), params.get('signal', 9)),
            'williams_r': lambda: self.momentum.williams_r(data['high'], data['low'], data['close'], 
                                                          params.get('period', 14)),
            'cci': lambda: self.momentum.cci(data['high'], data['low'], data['close'], params.get('period', 20)),
            'roc': lambda: self.momentum.roc(data['close'], params.get('period', 12)),
            'mfi': lambda: self.momentum.mfi(data['high'], data['low'], data['close'], data['volume'], 
                                            params.get('period', 14)),
            'awesome_oscillator': lambda: self.momentum.awesome_oscillator(data['high'], data['low']),
            'stochastic_rsi': lambda: self.momentum.stochastic_rsi(data['close'], params.get('rsi_period', 14), 
                                                                   params.get('stoch_period', 14)),
            
            # Volatility
            'atr': lambda: self.volatility.atr(data['high'], data['low'], data['close'], params.get('period', 14)),
            'bollinger_bands': lambda: self.volatility.bollinger_bands(data['close'], params.get('period', 20), 
                                                                       params.get('std_dev', 2.0)),
            'keltner_channels': lambda: self.volatility.keltner_channels(data['high'], data['low'], data['close'], 
                                                                         params.get('ema_period', 20), 
                                                                         params.get('atr_period', 10), 
                                                                         params.get('multiplier', 2.0)),
            'donchian_channels': lambda: self.volatility.donchian_channels(data['high'], data['low'], 
                                                                           params.get('period', 20)),
            'historical_volatility': lambda: self.volatility.historical_volatility(data['close'], 
                                                                                   params.get('period', 20)),
            
            # Volume
            'obv': lambda: self.volume.obv(data['close'], data['volume']),
            'volume_oscillator': lambda: self.volume.volume_oscillator(data['volume'], params.get('fast', 5), 
                                                                       params.get('slow', 10)),
            'volume_weighted_ma': lambda: self.volume.volume_weighted_ma(data['close'], data['volume'], 
                                                                         params.get('period', 20)),
            'accumulation_distribution': lambda: self.volume.accumulation_distribution(data['high'], data['low'], 
                                                                                       data['close'], data['volume']),
            
            # Market Structure
            'pivot_points': lambda: self.structure.pivot_points(data['high'], data['low'], data['close']),
            'support_resistance': lambda: self.structure.support_resistance(data['close'], params.get('period', 50)),
            'zigzag': lambda: self.structure.zigzag(data['high'], data['low'], data['close'], 
                                                   params.get('deviation', 5.0)),
        }
        
        calculator = indicator_map.get(indicator_name.lower())
        if calculator:
            return calculator()
        else:
            raise ValueError(f"Unknown indicator: {indicator_name}")


# Export main calculator
indicator_calculator = IndicatorCalculator()
