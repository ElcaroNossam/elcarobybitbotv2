"""
Technical Indicators Library for ElCaro Trading Platform
Complete implementation of all trading indicators
"""
import math
from typing import List, Dict, Tuple, Optional, Any
from dataclasses import dataclass


@dataclass
class IndicatorResult:
    value: float
    signal: Optional[str] = None  # 'buy', 'sell', 'neutral'
    strength: float = 0.0  # 0-100


class Indicators:
    """Complete technical indicators library"""
    
    # ==================== MOVING AVERAGES ====================
    
    @staticmethod
    def sma(prices: List[float], period: int) -> List[float]:
        """Simple Moving Average"""
        if len(prices) < period:
            return [prices[-1]] * len(prices)
        
        result = [None] * (period - 1)
        for i in range(period - 1, len(prices)):
            result.append(sum(prices[i - period + 1:i + 1]) / period)
        return result
    
    @staticmethod
    def ema(prices: List[float], period: int) -> List[float]:
        """Exponential Moving Average"""
        if not prices:
            return []
        
        multiplier = 2 / (period + 1)
        ema_values = [prices[0]]
        
        for i in range(1, len(prices)):
            ema_val = (prices[i] * multiplier) + (ema_values[-1] * (1 - multiplier))
            ema_values.append(ema_val)
        
        return ema_values
    
    @staticmethod
    def wma(prices: List[float], period: int) -> List[float]:
        """Weighted Moving Average"""
        if len(prices) < period:
            return [prices[-1]] * len(prices)
        
        weights = list(range(1, period + 1))
        weight_sum = sum(weights)
        
        result = [None] * (period - 1)
        for i in range(period - 1, len(prices)):
            window = prices[i - period + 1:i + 1]
            wma_val = sum(p * w for p, w in zip(window, weights)) / weight_sum
            result.append(wma_val)
        return result
    
    @staticmethod
    def hull_ma(prices: List[float], period: int) -> List[float]:
        """Hull Moving Average - Faster and smoother"""
        half_period = period // 2
        sqrt_period = int(math.sqrt(period))
        
        wma_half = Indicators.wma(prices, half_period)
        wma_full = Indicators.wma(prices, period)
        
        # 2 * WMA(n/2) - WMA(n)
        raw = [2 * h - f if h and f else prices[i] 
               for i, (h, f) in enumerate(zip(wma_half, wma_full))]
        
        return Indicators.wma(raw, sqrt_period)
    
    @staticmethod
    def vwap(candles: List[Dict], period: int = None) -> List[float]:
        """Volume Weighted Average Price"""
        result = []
        cumulative_tpv = 0
        cumulative_volume = 0
        
        for i, c in enumerate(candles):
            typical_price = (c['high'] + c['low'] + c['close']) / 3
            cumulative_tpv += typical_price * c['volume']
            cumulative_volume += c['volume']
            
            if cumulative_volume > 0:
                result.append(cumulative_tpv / cumulative_volume)
            else:
                result.append(c['close'])
        
        return result
    
    # ==================== MOMENTUM INDICATORS ====================
    
    @staticmethod
    def rsi(prices: List[float], period: int = 14) -> List[float]:
        """Relative Strength Index"""
        if len(prices) < period + 1:
            return [50.0] * len(prices)
        
        deltas = [prices[i] - prices[i-1] for i in range(1, len(prices))]
        
        gains = [max(d, 0) for d in deltas]
        losses = [abs(min(d, 0)) for d in deltas]
        
        result = [50.0] * period
        
        avg_gain = sum(gains[:period]) / period
        avg_loss = sum(losses[:period]) / period
        
        for i in range(period, len(deltas)):
            avg_gain = (avg_gain * (period - 1) + gains[i]) / period
            avg_loss = (avg_loss * (period - 1) + losses[i]) / period
            
            if avg_loss == 0:
                result.append(100.0)
            else:
                rs = avg_gain / avg_loss
                result.append(100 - (100 / (1 + rs)))
        
        return result
    
    @staticmethod
    def stochastic(candles: List[Dict], k_period: int = 14, d_period: int = 3) -> Tuple[List[float], List[float]]:
        """Stochastic Oscillator - %K and %D"""
        if len(candles) < k_period:
            return [50.0] * len(candles), [50.0] * len(candles)
        
        k_values = []
        
        for i in range(len(candles)):
            if i < k_period - 1:
                k_values.append(50.0)
            else:
                window = candles[i - k_period + 1:i + 1]
                highest = max(c['high'] for c in window)
                lowest = min(c['low'] for c in window)
                close = candles[i]['close']
                
                if highest - lowest > 0:
                    k = 100 * (close - lowest) / (highest - lowest)
                else:
                    k = 50.0
                k_values.append(k)
        
        # %D is SMA of %K
        d_values = Indicators.sma(k_values, d_period)
        
        return k_values, d_values
    
    @staticmethod
    def macd(prices: List[float], fast: int = 12, slow: int = 26, signal: int = 9) -> Tuple[List[float], List[float], List[float]]:
        """MACD - Line, Signal, Histogram"""
        ema_fast = Indicators.ema(prices, fast)
        ema_slow = Indicators.ema(prices, slow)
        
        macd_line = [f - s for f, s in zip(ema_fast, ema_slow)]
        signal_line = Indicators.ema(macd_line, signal)
        histogram = [m - s for m, s in zip(macd_line, signal_line)]
        
        return macd_line, signal_line, histogram
    
    @staticmethod
    def cci(candles: List[Dict], period: int = 20) -> List[float]:
        """Commodity Channel Index"""
        if len(candles) < period:
            return [0.0] * len(candles)
        
        typical_prices = [(c['high'] + c['low'] + c['close']) / 3 for c in candles]
        sma_tp = Indicators.sma(typical_prices, period)
        
        result = []
        for i in range(len(candles)):
            if i < period - 1 or sma_tp[i] is None:
                result.append(0.0)
            else:
                window = typical_prices[i - period + 1:i + 1]
                mean_deviation = sum(abs(p - sma_tp[i]) for p in window) / period
                
                if mean_deviation > 0:
                    cci_val = (typical_prices[i] - sma_tp[i]) / (0.015 * mean_deviation)
                else:
                    cci_val = 0.0
                result.append(cci_val)
        
        return result
    
    @staticmethod
    def williams_r(candles: List[Dict], period: int = 14) -> List[float]:
        """Williams %R"""
        if len(candles) < period:
            return [-50.0] * len(candles)
        
        result = []
        for i in range(len(candles)):
            if i < period - 1:
                result.append(-50.0)
            else:
                window = candles[i - period + 1:i + 1]
                highest = max(c['high'] for c in window)
                lowest = min(c['low'] for c in window)
                close = candles[i]['close']
                
                if highest - lowest > 0:
                    wr = -100 * (highest - close) / (highest - lowest)
                else:
                    wr = -50.0
                result.append(wr)
        
        return result
    
    @staticmethod
    def mfi(candles: List[Dict], period: int = 14) -> List[float]:
        """Money Flow Index (Volume-weighted RSI)"""
        if len(candles) < period + 1:
            return [50.0] * len(candles)
        
        typical_prices = [(c['high'] + c['low'] + c['close']) / 3 for c in candles]
        raw_money_flow = [tp * c['volume'] for tp, c in zip(typical_prices, candles)]
        
        result = [50.0] * period
        
        for i in range(period, len(candles)):
            positive_flow = 0
            negative_flow = 0
            
            for j in range(i - period + 1, i + 1):
                if typical_prices[j] > typical_prices[j - 1]:
                    positive_flow += raw_money_flow[j]
                else:
                    negative_flow += raw_money_flow[j]
            
            if negative_flow == 0:
                result.append(100.0)
            else:
                mfi = 100 - (100 / (1 + positive_flow / negative_flow))
                result.append(mfi)
        
        return result
    
    @staticmethod
    def roc(prices: List[float], period: int = 12) -> List[float]:
        """Rate of Change"""
        result = [0.0] * period
        
        for i in range(period, len(prices)):
            if prices[i - period] != 0:
                roc_val = ((prices[i] - prices[i - period]) / prices[i - period]) * 100
            else:
                roc_val = 0.0
            result.append(roc_val)
        
        return result
    
    # ==================== VOLATILITY INDICATORS ====================
    
    @staticmethod
    def bollinger_bands(prices: List[float], period: int = 20, std_dev: float = 2.0) -> Tuple[List[float], List[float], List[float]]:
        """Bollinger Bands - Upper, Middle, Lower"""
        if len(prices) < period:
            return [prices[-1]] * len(prices), [prices[-1]] * len(prices), [prices[-1]] * len(prices)
        
        middle = Indicators.sma(prices, period)
        upper = []
        lower = []
        
        for i in range(len(prices)):
            if i < period - 1 or middle[i] is None:
                upper.append(prices[i])
                lower.append(prices[i])
            else:
                window = prices[i - period + 1:i + 1]
                std = math.sqrt(sum((p - middle[i]) ** 2 for p in window) / period)
                upper.append(middle[i] + std_dev * std)
                lower.append(middle[i] - std_dev * std)
        
        return upper, middle, lower
    
    @staticmethod
    def atr(candles: List[Dict], period: int = 14) -> List[float]:
        """Average True Range"""
        if len(candles) < 2:
            return [0.0] * len(candles)
        
        true_ranges = [candles[0]['high'] - candles[0]['low']]
        
        for i in range(1, len(candles)):
            high = candles[i]['high']
            low = candles[i]['low']
            prev_close = candles[i - 1]['close']
            
            tr = max(
                high - low,
                abs(high - prev_close),
                abs(low - prev_close)
            )
            true_ranges.append(tr)
        
        # Smoothed ATR (Wilder's method)
        atr_values = [true_ranges[0]]
        for i in range(1, len(true_ranges)):
            if i < period:
                atr_values.append(sum(true_ranges[:i+1]) / (i + 1))
            else:
                atr_val = (atr_values[-1] * (period - 1) + true_ranges[i]) / period
                atr_values.append(atr_val)
        
        return atr_values
    
    @staticmethod
    def keltner_channels(candles: List[Dict], ema_period: int = 20, atr_period: int = 10, multiplier: float = 2.0) -> Tuple[List[float], List[float], List[float]]:
        """Keltner Channels - Upper, Middle, Lower"""
        closes = [c['close'] for c in candles]
        middle = Indicators.ema(closes, ema_period)
        atr_values = Indicators.atr(candles, atr_period)
        
        upper = [m + multiplier * a for m, a in zip(middle, atr_values)]
        lower = [m - multiplier * a for m, a in zip(middle, atr_values)]
        
        return upper, middle, lower
    
    @staticmethod
    def donchian_channels(candles: List[Dict], period: int = 20) -> Tuple[List[float], List[float], List[float]]:
        """Donchian Channels - Upper, Middle, Lower"""
        upper = []
        lower = []
        middle = []
        
        for i in range(len(candles)):
            if i < period - 1:
                upper.append(candles[i]['high'])
                lower.append(candles[i]['low'])
            else:
                window = candles[i - period + 1:i + 1]
                high = max(c['high'] for c in window)
                low = min(c['low'] for c in window)
                upper.append(high)
                lower.append(low)
            
            middle.append((upper[-1] + lower[-1]) / 2)
        
        return upper, middle, lower
    
    @staticmethod
    def volatility_ratio(candles: List[Dict], period: int = 14) -> List[float]:
        """Volatility Ratio (current ATR / historical ATR)"""
        atr_values = Indicators.atr(candles, period)
        
        result = [1.0] * period
        for i in range(period, len(atr_values)):
            avg_atr = sum(atr_values[i - period:i]) / period
            if avg_atr > 0:
                result.append(atr_values[i] / avg_atr)
            else:
                result.append(1.0)
        
        return result
    
    # ==================== TREND INDICATORS ====================
    
    @staticmethod
    def adx(candles: List[Dict], period: int = 14) -> Tuple[List[float], List[float], List[float]]:
        """ADX with +DI and -DI"""
        if len(candles) < period + 1:
            return [0.0] * len(candles), [0.0] * len(candles), [0.0] * len(candles)
        
        plus_dm = []
        minus_dm = []
        tr_list = []
        
        for i in range(1, len(candles)):
            high = candles[i]['high']
            low = candles[i]['low']
            prev_high = candles[i - 1]['high']
            prev_low = candles[i - 1]['low']
            prev_close = candles[i - 1]['close']
            
            up_move = high - prev_high
            down_move = prev_low - low
            
            if up_move > down_move and up_move > 0:
                plus_dm.append(up_move)
            else:
                plus_dm.append(0)
            
            if down_move > up_move and down_move > 0:
                minus_dm.append(down_move)
            else:
                minus_dm.append(0)
            
            tr = max(high - low, abs(high - prev_close), abs(low - prev_close))
            tr_list.append(tr)
        
        # Smoothed values
        def smooth(values, period):
            result = [sum(values[:period])]
            for i in range(period, len(values)):
                result.append(result[-1] - result[-1]/period + values[i])
            return result
        
        smooth_plus_dm = smooth(plus_dm, period)
        smooth_minus_dm = smooth(minus_dm, period)
        smooth_tr = smooth(tr_list, period)
        
        # Calculate DI values
        plus_di = []
        minus_di = []
        dx_list = []
        
        for i in range(len(smooth_tr)):
            if smooth_tr[i] > 0:
                pdi = 100 * smooth_plus_dm[i] / smooth_tr[i]
                mdi = 100 * smooth_minus_dm[i] / smooth_tr[i]
            else:
                pdi = 0
                mdi = 0
            
            plus_di.append(pdi)
            minus_di.append(mdi)
            
            if pdi + mdi > 0:
                dx = 100 * abs(pdi - mdi) / (pdi + mdi)
            else:
                dx = 0
            dx_list.append(dx)
        
        # ADX is smoothed DX
        adx_values = [0.0]
        for i in range(1, len(dx_list)):
            if i < period:
                adx_values.append(sum(dx_list[:i+1]) / (i + 1))
            else:
                adx_values.append((adx_values[-1] * (period - 1) + dx_list[i]) / period)
        
        # Pad to match input length
        pad = [0.0]
        return pad + adx_values, pad + plus_di, pad + minus_di
    
    @staticmethod
    def parabolic_sar(candles: List[Dict], af_start: float = 0.02, af_max: float = 0.2) -> List[float]:
        """Parabolic SAR"""
        if len(candles) < 2:
            return [c['close'] for c in candles]
        
        sar = [candles[0]['low']]
        af = af_start
        ep = candles[0]['high']
        is_uptrend = True
        
        for i in range(1, len(candles)):
            prev_sar = sar[-1]
            
            if is_uptrend:
                new_sar = prev_sar + af * (ep - prev_sar)
                new_sar = min(new_sar, candles[i - 1]['low'], candles[i - 2]['low'] if i >= 2 else candles[i - 1]['low'])
                
                if candles[i]['low'] < new_sar:
                    is_uptrend = False
                    new_sar = ep
                    ep = candles[i]['low']
                    af = af_start
                else:
                    if candles[i]['high'] > ep:
                        ep = candles[i]['high']
                        af = min(af + af_start, af_max)
            else:
                new_sar = prev_sar + af * (ep - prev_sar)
                new_sar = max(new_sar, candles[i - 1]['high'], candles[i - 2]['high'] if i >= 2 else candles[i - 1]['high'])
                
                if candles[i]['high'] > new_sar:
                    is_uptrend = True
                    new_sar = ep
                    ep = candles[i]['high']
                    af = af_start
                else:
                    if candles[i]['low'] < ep:
                        ep = candles[i]['low']
                        af = min(af + af_start, af_max)
            
            sar.append(new_sar)
        
        return sar
    
    @staticmethod
    def supertrend(candles: List[Dict], period: int = 10, multiplier: float = 3.0) -> Tuple[List[float], List[int]]:
        """Supertrend indicator - values and direction (1=up, -1=down)"""
        atr_values = Indicators.atr(candles, period)
        
        supertrend = []
        direction = []
        
        for i in range(len(candles)):
            hl2 = (candles[i]['high'] + candles[i]['low']) / 2
            
            upper_band = hl2 + multiplier * atr_values[i]
            lower_band = hl2 - multiplier * atr_values[i]
            
            if i == 0:
                supertrend.append(lower_band)
                direction.append(1)
            else:
                prev_st = supertrend[-1]
                prev_dir = direction[-1]
                
                if prev_dir == 1:  # Was uptrend
                    if candles[i]['close'] < prev_st:
                        supertrend.append(upper_band)
                        direction.append(-1)
                    else:
                        supertrend.append(max(lower_band, prev_st))
                        direction.append(1)
                else:  # Was downtrend
                    if candles[i]['close'] > prev_st:
                        supertrend.append(lower_band)
                        direction.append(1)
                    else:
                        supertrend.append(min(upper_band, prev_st))
                        direction.append(-1)
        
        return supertrend, direction
    
    # ==================== VOLUME INDICATORS ====================
    
    @staticmethod
    def obv(candles: List[Dict]) -> List[float]:
        """On-Balance Volume"""
        if not candles:
            return []
        
        obv_values = [candles[0]['volume']]
        
        for i in range(1, len(candles)):
            if candles[i]['close'] > candles[i - 1]['close']:
                obv_values.append(obv_values[-1] + candles[i]['volume'])
            elif candles[i]['close'] < candles[i - 1]['close']:
                obv_values.append(obv_values[-1] - candles[i]['volume'])
            else:
                obv_values.append(obv_values[-1])
        
        return obv_values
    
    @staticmethod
    def volume_delta(candles: List[Dict]) -> List[float]:
        """Volume Delta (Buy volume - Sell volume approximation)"""
        result = []
        
        for c in candles:
            # Approximate buy/sell volume based on candle position
            range_size = c['high'] - c['low']
            if range_size > 0:
                buy_ratio = (c['close'] - c['low']) / range_size
            else:
                buy_ratio = 0.5
            
            buy_vol = c['volume'] * buy_ratio
            sell_vol = c['volume'] * (1 - buy_ratio)
            result.append(buy_vol - sell_vol)
        
        return result
    
    @staticmethod
    def cvd(candles: List[Dict]) -> List[float]:
        """Cumulative Volume Delta"""
        delta = Indicators.volume_delta(candles)
        
        cvd_values = [delta[0]]
        for i in range(1, len(delta)):
            cvd_values.append(cvd_values[-1] + delta[i])
        
        return cvd_values
    
    @staticmethod
    def volume_profile(candles: List[Dict], bins: int = 20) -> Dict[str, Any]:
        """Volume Profile - POC, VAH, VAL"""
        if not candles:
            return {}
        
        low = min(c['low'] for c in candles)
        high = max(c['high'] for c in candles)
        bin_size = (high - low) / bins
        
        profile = [0.0] * bins
        
        for c in candles:
            for i in range(bins):
                bin_low = low + i * bin_size
                bin_high = bin_low + bin_size
                
                if c['low'] < bin_high and c['high'] > bin_low:
                    overlap = min(c['high'], bin_high) - max(c['low'], bin_low)
                    ratio = overlap / (c['high'] - c['low']) if c['high'] > c['low'] else 1
                    profile[i] += c['volume'] * ratio
        
        # POC - Point of Control (highest volume level)
        poc_idx = profile.index(max(profile))
        poc_price = low + (poc_idx + 0.5) * bin_size
        
        # Value Area (70% of volume)
        total_vol = sum(profile)
        target_vol = total_vol * 0.7
        
        # Start from POC and expand
        val_idx = vah_idx = poc_idx
        current_vol = profile[poc_idx]
        
        while current_vol < target_vol:
            expand_down = profile[val_idx - 1] if val_idx > 0 else 0
            expand_up = profile[vah_idx + 1] if vah_idx < bins - 1 else 0
            
            if expand_down >= expand_up and val_idx > 0:
                val_idx -= 1
                current_vol += profile[val_idx]
            elif vah_idx < bins - 1:
                vah_idx += 1
                current_vol += profile[vah_idx]
            else:
                break
        
        return {
            "poc": poc_price,
            "vah": low + (vah_idx + 1) * bin_size,
            "val": low + val_idx * bin_size,
            "profile": profile,
            "bin_size": bin_size,
            "low": low
        }
    
    # ==================== FIBONACCI ====================
    
    @staticmethod
    def fibonacci_retracement(high: float, low: float) -> Dict[str, float]:
        """Fibonacci Retracement Levels"""
        diff = high - low
        return {
            "0.0": high,
            "0.236": high - diff * 0.236,
            "0.382": high - diff * 0.382,
            "0.5": high - diff * 0.5,
            "0.618": high - diff * 0.618,
            "0.786": high - diff * 0.786,
            "1.0": low,
            "1.272": low - diff * 0.272,
            "1.618": low - diff * 0.618
        }
    
    @staticmethod
    def fibonacci_extension(high: float, low: float, retracement_level: float) -> Dict[str, float]:
        """Fibonacci Extension Levels"""
        diff = high - low
        return {
            "1.0": retracement_level + diff,
            "1.272": retracement_level + diff * 1.272,
            "1.618": retracement_level + diff * 1.618,
            "2.0": retracement_level + diff * 2,
            "2.618": retracement_level + diff * 2.618
        }
    
    @staticmethod
    def pivot_points(candles: List[Dict]) -> Dict[str, float]:
        """Daily Pivot Points (Standard)"""
        if not candles:
            return {}
        
        last = candles[-1]
        high = last['high']
        low = last['low']
        close = last['close']
        
        pivot = (high + low + close) / 3
        
        return {
            "r3": high + 2 * (pivot - low),
            "r2": pivot + (high - low),
            "r1": 2 * pivot - low,
            "pivot": pivot,
            "s1": 2 * pivot - high,
            "s2": pivot - (high - low),
            "s3": low - 2 * (high - pivot)
        }
    
    # ==================== PATTERN RECOGNITION ====================
    
    @staticmethod
    def detect_divergence(prices: List[float], indicator: List[float], lookback: int = 10) -> List[Dict]:
        """Detect bullish and bearish divergences"""
        divergences = []
        
        for i in range(lookback, len(prices)):
            window_prices = prices[i - lookback:i + 1]
            window_ind = indicator[i - lookback:i + 1]
            
            # Find local lows and highs
            price_low_idx = window_prices.index(min(window_prices))
            price_high_idx = window_prices.index(max(window_prices))
            ind_low_idx = window_ind.index(min(window_ind))
            ind_high_idx = window_ind.index(max(window_ind))
            
            # Bullish divergence: lower low in price, higher low in indicator
            if price_low_idx > 0 and ind_low_idx > 0:
                if window_prices[-1] < window_prices[0] and window_ind[-1] > window_ind[0]:
                    divergences.append({
                        "index": i,
                        "type": "bullish",
                        "strength": abs(window_ind[-1] - window_ind[0])
                    })
            
            # Bearish divergence: higher high in price, lower high in indicator
            if price_high_idx > 0 and ind_high_idx > 0:
                if window_prices[-1] > window_prices[0] and window_ind[-1] < window_ind[0]:
                    divergences.append({
                        "index": i,
                        "type": "bearish",
                        "strength": abs(window_ind[-1] - window_ind[0])
                    })
        
        return divergences
    
    @staticmethod
    def detect_support_resistance(candles: List[Dict], lookback: int = 50, tolerance: float = 0.02) -> Dict[str, List[float]]:
        """Detect support and resistance levels"""
        if len(candles) < lookback:
            return {"support": [], "resistance": []}
        
        highs = [c['high'] for c in candles[-lookback:]]
        lows = [c['low'] for c in candles[-lookback:]]
        
        levels = []
        
        # Find local maxima and minima
        for i in range(2, len(highs) - 2):
            if highs[i] > highs[i-1] and highs[i] > highs[i-2] and highs[i] > highs[i+1] and highs[i] > highs[i+2]:
                levels.append(("resistance", highs[i]))
            
            if lows[i] < lows[i-1] and lows[i] < lows[i-2] and lows[i] < lows[i+1] and lows[i] < lows[i+2]:
                levels.append(("support", lows[i]))
        
        # Cluster similar levels
        current_price = candles[-1]['close']
        support = []
        resistance = []
        
        for level_type, price in levels:
            is_new = True
            target_list = support if level_type == "support" else resistance
            
            for existing in target_list:
                if abs(existing - price) / price < tolerance:
                    is_new = False
                    break
            
            if is_new:
                target_list.append(price)
        
        # Sort by distance from current price
        support.sort(key=lambda x: abs(x - current_price))
        resistance.sort(key=lambda x: abs(x - current_price))
        
        return {
            "support": support[:5],  # Top 5 levels
            "resistance": resistance[:5]
        }
    
    # ==================== ICHIMOKU ====================
    
    @staticmethod
    def ichimoku(candles: List[Dict], 
                 conversion_period: int = 9, 
                 base_period: int = 26, 
                 span_b_period: int = 52,
                 displacement: int = 26) -> Dict[str, List[float]]:
        """Ichimoku Cloud"""
        
        def donchian_mid(data: List[Dict], period: int, end_idx: int) -> float:
            start = max(0, end_idx - period + 1)
            window = data[start:end_idx + 1]
            if not window:
                return data[end_idx]['close']
            highest = max(c['high'] for c in window)
            lowest = min(c['low'] for c in window)
            return (highest + lowest) / 2
        
        tenkan_sen = []  # Conversion Line
        kijun_sen = []   # Base Line
        senkou_span_a = []  # Leading Span A
        senkou_span_b = []  # Leading Span B
        chikou_span = []    # Lagging Span
        
        for i in range(len(candles)):
            tenkan = donchian_mid(candles, conversion_period, i)
            kijun = donchian_mid(candles, base_period, i)
            
            tenkan_sen.append(tenkan)
            kijun_sen.append(kijun)
            
            # Span A and B are displaced forward
            senkou_a = (tenkan + kijun) / 2
            senkou_b = donchian_mid(candles, span_b_period, i)
            
            senkou_span_a.append(senkou_a)
            senkou_span_b.append(senkou_b)
            
            # Chikou is current close (displayed displaced backward)
            chikou_span.append(candles[i]['close'])
        
        return {
            "tenkan_sen": tenkan_sen,
            "kijun_sen": kijun_sen,
            "senkou_span_a": senkou_span_a,
            "senkou_span_b": senkou_span_b,
            "chikou_span": chikou_span
        }
    
    # ==================== COMPOSITE SIGNALS ====================
    
    @staticmethod
    def calculate_trend_strength(candles: List[Dict]) -> Dict[str, Any]:
        """Calculate overall trend strength using multiple indicators"""
        closes = [c['close'] for c in candles]
        
        # EMAs for trend direction
        ema_20 = Indicators.ema(closes, 20)
        ema_50 = Indicators.ema(closes, 50)
        ema_200 = Indicators.ema(closes, 200) if len(closes) >= 200 else Indicators.ema(closes, min(len(closes), 50))
        
        # ADX for trend strength
        adx, plus_di, minus_di = Indicators.adx(candles, 14)
        
        # RSI for momentum
        rsi = Indicators.rsi(closes, 14)
        
        # MACD for momentum confirmation
        macd_line, signal, hist = Indicators.macd(closes)
        
        current = len(candles) - 1
        
        # Score calculation
        trend_score = 0
        
        # EMA alignment
        if ema_20[-1] > ema_50[-1] > ema_200[-1]:
            trend_score += 30  # Strong uptrend alignment
        elif ema_20[-1] < ema_50[-1] < ema_200[-1]:
            trend_score -= 30  # Strong downtrend alignment
        
        # ADX strength
        if adx[-1] > 25:
            trend_score += 20 if plus_di[-1] > minus_di[-1] else -20
        
        # RSI confirmation
        if rsi[-1] > 50:
            trend_score += 15
        else:
            trend_score -= 15
        
        # MACD confirmation
        if hist[-1] > 0:
            trend_score += 15
        else:
            trend_score -= 15
        
        # Supertrend
        st, direction = Indicators.supertrend(candles)
        if direction[-1] == 1:
            trend_score += 20
        else:
            trend_score -= 20
        
        return {
            "score": max(-100, min(100, trend_score)),
            "direction": "bullish" if trend_score > 20 else "bearish" if trend_score < -20 else "neutral",
            "strength": abs(trend_score),
            "details": {
                "ema_20": ema_20[-1],
                "ema_50": ema_50[-1],
                "ema_200": ema_200[-1],
                "adx": adx[-1],
                "rsi": rsi[-1],
                "macd_hist": hist[-1],
                "supertrend_dir": direction[-1]
            }
        }

    # ==================== EXTENDED INDICATORS ====================
    
    @staticmethod
    def dema(prices: List[float], period: int) -> List[float]:
        """Double Exponential Moving Average"""
        ema1 = Indicators.ema(prices, period)
        ema2 = Indicators.ema(ema1, period)
        return [2 * e1 - e2 for e1, e2 in zip(ema1, ema2)]
    
    @staticmethod
    def tema(prices: List[float], period: int) -> List[float]:
        """Triple Exponential Moving Average"""
        ema1 = Indicators.ema(prices, period)
        ema2 = Indicators.ema(ema1, period)
        ema3 = Indicators.ema(ema2, period)
        return [3 * e1 - 3 * e2 + e3 for e1, e2, e3 in zip(ema1, ema2, ema3)]
    
    @staticmethod
    def kama(prices: List[float], period: int = 10, fast: int = 2, slow: int = 30) -> List[float]:
        """Kaufman Adaptive Moving Average"""
        if len(prices) < period + 1:
            return prices.copy()
        
        fast_sc = 2 / (fast + 1)
        slow_sc = 2 / (slow + 1)
        
        result = [prices[0]] * period
        
        for i in range(period, len(prices)):
            change = abs(prices[i] - prices[i - period])
            volatility = sum(abs(prices[j] - prices[j - 1]) for j in range(i - period + 1, i + 1))
            
            if volatility != 0:
                er = change / volatility
            else:
                er = 0
            
            sc = (er * (fast_sc - slow_sc) + slow_sc) ** 2
            kama_val = result[-1] + sc * (prices[i] - result[-1])
            result.append(kama_val)
        
        return result
    
    @staticmethod
    def zlema(prices: List[float], period: int) -> List[float]:
        """Zero Lag Exponential Moving Average"""
        lag = (period - 1) // 2
        ema_data = [prices[i] + (prices[i] - prices[i - lag]) if i >= lag else prices[i] 
                    for i in range(len(prices))]
        return Indicators.ema(ema_data, period)
    
    @staticmethod
    def t3(prices: List[float], period: int = 5, v_factor: float = 0.7) -> List[float]:
        """T3 Moving Average (Tillson)"""
        c1 = -v_factor ** 3
        c2 = 3 * v_factor ** 2 + 3 * v_factor ** 3
        c3 = -6 * v_factor ** 2 - 3 * v_factor - 3 * v_factor ** 3
        c4 = 1 + 3 * v_factor + v_factor ** 3 + 3 * v_factor ** 2
        
        e1 = Indicators.ema(prices, period)
        e2 = Indicators.ema(e1, period)
        e3 = Indicators.ema(e2, period)
        e4 = Indicators.ema(e3, period)
        e5 = Indicators.ema(e4, period)
        e6 = Indicators.ema(e5, period)
        
        return [c1 * a + c2 * b + c3 * c + c4 * d 
                for a, b, c, d in zip(e6, e5, e4, e3)]
    
    @staticmethod
    def vidya(prices: List[float], period: int = 14, alpha: float = 0.2) -> List[float]:
        """Variable Index Dynamic Average"""
        if len(prices) < period:
            return prices.copy()
        
        result = [prices[0]]
        
        for i in range(1, len(prices)):
            if i < period:
                result.append(prices[i])
                continue
            
            # Calculate CMO for dynamic factor
            ups = sum(max(0, prices[j] - prices[j-1]) for j in range(i-period+1, i+1))
            downs = sum(max(0, prices[j-1] - prices[j]) for j in range(i-period+1, i+1))
            
            if ups + downs != 0:
                cmo = abs(ups - downs) / (ups + downs)
            else:
                cmo = 0
            
            vidya_val = alpha * cmo * prices[i] + (1 - alpha * cmo) * result[-1]
            result.append(vidya_val)
        
        return result
    
    # ==================== OSCILLATORS ====================
    
    @staticmethod
    def stoch_rsi(prices: List[float], period: int = 14, k_period: int = 3, d_period: int = 3) -> Tuple[List[float], List[float]]:
        """Stochastic RSI"""
        rsi = Indicators.rsi(prices, period)
        
        k_values = []
        for i in range(len(rsi)):
            if i < period:
                k_values.append(50)
            else:
                window = rsi[i - period + 1:i + 1]
                min_rsi = min(window)
                max_rsi = max(window)
                if max_rsi - min_rsi != 0:
                    k_values.append((rsi[i] - min_rsi) / (max_rsi - min_rsi) * 100)
                else:
                    k_values.append(50)
        
        d_values = Indicators.sma(k_values, d_period)
        k_smooth = Indicators.sma(k_values, k_period)
        
        return k_smooth, d_values
    
    @staticmethod
    def ultimate_oscillator(candles: List[Dict], period1: int = 7, period2: int = 14, period3: int = 28) -> List[float]:
        """Ultimate Oscillator"""
        if len(candles) < period3 + 1:
            return [50] * len(candles)
        
        bp = []  # Buying Pressure
        tr = []  # True Range
        
        for i in range(1, len(candles)):
            close_prev = candles[i - 1]['close']
            low = min(candles[i]['low'], close_prev)
            high = max(candles[i]['high'], close_prev)
            
            bp.append(candles[i]['close'] - low)
            tr.append(high - low)
        
        result = [50]
        
        for i in range(1, len(bp)):
            if i < period3:
                result.append(50)
                continue
            
            bp1 = sum(bp[i - period1 + 1:i + 1])
            tr1 = sum(tr[i - period1 + 1:i + 1])
            bp2 = sum(bp[i - period2 + 1:i + 1])
            tr2 = sum(tr[i - period2 + 1:i + 1])
            bp3 = sum(bp[i - period3 + 1:i + 1])
            tr3 = sum(tr[i - period3 + 1:i + 1])
            
            avg1 = bp1 / tr1 if tr1 != 0 else 0
            avg2 = bp2 / tr2 if tr2 != 0 else 0
            avg3 = bp3 / tr3 if tr3 != 0 else 0
            
            uo = 100 * (4 * avg1 + 2 * avg2 + avg3) / 7
            result.append(uo)
        
        return result
    
    @staticmethod
    def awesome_oscillator(candles: List[Dict], fast: int = 5, slow: int = 34) -> List[float]:
        """Awesome Oscillator (Bill Williams)"""
        median_prices = [(c['high'] + c['low']) / 2 for c in candles]
        sma_fast = Indicators.sma(median_prices, fast)
        sma_slow = Indicators.sma(median_prices, slow)
        return [f - s if f and s else 0 for f, s in zip(sma_fast, sma_slow)]
    
    @staticmethod
    def accelerator_oscillator(candles: List[Dict], fast: int = 5, slow: int = 34) -> List[float]:
        """Accelerator Oscillator (Bill Williams)"""
        ao = Indicators.awesome_oscillator(candles, fast, slow)
        ao_sma = Indicators.sma(ao, 5)
        return [a - s if s else 0 for a, s in zip(ao, ao_sma)]
    
    @staticmethod
    def trix(prices: List[float], period: int = 15) -> List[float]:
        """TRIX - Triple Exponential Average Rate of Change"""
        ema1 = Indicators.ema(prices, period)
        ema2 = Indicators.ema(ema1, period)
        ema3 = Indicators.ema(ema2, period)
        
        result = [0]
        for i in range(1, len(ema3)):
            if ema3[i - 1] != 0:
                result.append((ema3[i] - ema3[i - 1]) / ema3[i - 1] * 10000)
            else:
                result.append(0)
        
        return result
    
    @staticmethod
    def cmo(prices: List[float], period: int = 14) -> List[float]:
        """Chande Momentum Oscillator"""
        if len(prices) < period + 1:
            return [0] * len(prices)
        
        result = [0] * period
        
        for i in range(period, len(prices)):
            ups = sum(max(0, prices[j] - prices[j - 1]) for j in range(i - period + 1, i + 1))
            downs = sum(max(0, prices[j - 1] - prices[j]) for j in range(i - period + 1, i + 1))
            
            if ups + downs != 0:
                result.append((ups - downs) / (ups + downs) * 100)
            else:
                result.append(0)
        
        return result
    
    @staticmethod
    def dpo(prices: List[float], period: int = 20) -> List[float]:
        """Detrended Price Oscillator"""
        shift = period // 2 + 1
        sma = Indicators.sma(prices, period)
        
        result = []
        for i in range(len(prices)):
            if i >= shift and sma[i - shift]:
                result.append(prices[i] - sma[i - shift])
            else:
                result.append(0)
        
        return result
    
    @staticmethod
    def ppo(prices: List[float], fast: int = 12, slow: int = 26, signal: int = 9) -> Tuple[List[float], List[float], List[float]]:
        """Percentage Price Oscillator"""
        ema_fast = Indicators.ema(prices, fast)
        ema_slow = Indicators.ema(prices, slow)
        
        ppo_line = [(f - s) / s * 100 if s != 0 else 0 for f, s in zip(ema_fast, ema_slow)]
        signal_line = Indicators.ema(ppo_line, signal)
        histogram = [p - s for p, s in zip(ppo_line, signal_line)]
        
        return ppo_line, signal_line, histogram
    
    @staticmethod
    def aroon(candles: List[Dict], period: int = 25) -> Tuple[List[float], List[float], List[float]]:
        """Aroon Indicator (Up, Down, Oscillator)"""
        aroon_up = []
        aroon_down = []
        
        for i in range(len(candles)):
            if i < period:
                aroon_up.append(50)
                aroon_down.append(50)
                continue
            
            window = candles[i - period:i + 1]
            highs = [c['high'] for c in window]
            lows = [c['low'] for c in window]
            
            days_since_high = period - highs.index(max(highs))
            days_since_low = period - lows.index(min(lows))
            
            aroon_up.append(((period - days_since_high) / period) * 100)
            aroon_down.append(((period - days_since_low) / period) * 100)
        
        oscillator = [u - d for u, d in zip(aroon_up, aroon_down)]
        
        return aroon_up, aroon_down, oscillator
    
    @staticmethod
    def chaikin_oscillator(candles: List[Dict], fast: int = 3, slow: int = 10) -> List[float]:
        """Chaikin Oscillator"""
        adl = Indicators.adl(candles)
        ema_fast = Indicators.ema(adl, fast)
        ema_slow = Indicators.ema(adl, slow)
        return [f - s for f, s in zip(ema_fast, ema_slow)]
    
    @staticmethod
    def adl(candles: List[Dict]) -> List[float]:
        """Accumulation/Distribution Line"""
        result = [0]
        
        for i, c in enumerate(candles):
            hl_range = c['high'] - c['low']
            if hl_range != 0:
                mfm = ((c['close'] - c['low']) - (c['high'] - c['close'])) / hl_range
            else:
                mfm = 0
            
            mfv = mfm * c['volume']
            
            if i == 0:
                result[0] = mfv
            else:
                result.append(result[-1] + mfv)
        
        return result
    
    @staticmethod
    def klinger_oscillator(candles: List[Dict], fast: int = 34, slow: int = 55, signal: int = 13) -> Tuple[List[float], List[float]]:
        """Klinger Volume Oscillator"""
        if len(candles) < 2:
            return [0] * len(candles), [0] * len(candles)
        
        hlc3 = [(c['high'] + c['low'] + c['close']) / 3 for c in candles]
        
        trend = [1]
        for i in range(1, len(hlc3)):
            trend.append(1 if hlc3[i] > hlc3[i - 1] else -1)
        
        dm = [candles[i]['high'] - candles[i]['low'] for i in range(len(candles))]
        cm = [dm[0]]
        for i in range(1, len(candles)):
            if trend[i] == trend[i - 1]:
                cm.append(cm[-1] + dm[i])
            else:
                cm.append(dm[i - 1] + dm[i])
        
        vf = [trend[i] * candles[i]['volume'] * abs(2 * dm[i] / cm[i] - 1) * 100 if cm[i] != 0 else 0 
              for i in range(len(candles))]
        
        kvo = [f - s for f, s in zip(Indicators.ema(vf, fast), Indicators.ema(vf, slow))]
        signal_line = Indicators.ema(kvo, signal)
        
        return kvo, signal_line
    
    @staticmethod
    def elder_ray(candles: List[Dict], period: int = 13) -> Tuple[List[float], List[float]]:
        """Elder Ray Index (Bull Power, Bear Power)"""
        closes = [c['close'] for c in candles]
        ema = Indicators.ema(closes, period)
        
        bull_power = [candles[i]['high'] - ema[i] for i in range(len(candles))]
        bear_power = [candles[i]['low'] - ema[i] for i in range(len(candles))]
        
        return bull_power, bear_power
    
    @staticmethod
    def force_index(candles: List[Dict], period: int = 13) -> List[float]:
        """Force Index"""
        if len(candles) < 2:
            return [0] * len(candles)
        
        fi = [0]
        for i in range(1, len(candles)):
            fi.append((candles[i]['close'] - candles[i - 1]['close']) * candles[i]['volume'])
        
        return Indicators.ema(fi, period)
    
    @staticmethod
    def choppiness_index(candles: List[Dict], period: int = 14) -> List[float]:
        """Choppiness Index - Measures market trendiness"""
        if len(candles) < period + 1:
            return [50] * len(candles)
        
        result = [50] * period
        
        for i in range(period, len(candles)):
            atr_sum = 0
            for j in range(i - period + 1, i + 1):
                tr = max(
                    candles[j]['high'] - candles[j]['low'],
                    abs(candles[j]['high'] - candles[j - 1]['close']),
                    abs(candles[j]['low'] - candles[j - 1]['close'])
                )
                atr_sum += tr
            
            high_max = max(c['high'] for c in candles[i - period + 1:i + 1])
            low_min = min(c['low'] for c in candles[i - period + 1:i + 1])
            
            if high_max - low_min != 0:
                ci = 100 * math.log10(atr_sum / (high_max - low_min)) / math.log10(period)
                result.append(max(0, min(100, ci)))
            else:
                result.append(50)
        
        return result
    
    @staticmethod
    def mass_index(candles: List[Dict], period: int = 25, ema_period: int = 9) -> List[float]:
        """Mass Index - Detects range expansion"""
        if len(candles) < period:
            return [0] * len(candles)
        
        hl_range = [c['high'] - c['low'] for c in candles]
        single_ema = Indicators.ema(hl_range, ema_period)
        double_ema = Indicators.ema(single_ema, ema_period)
        
        ema_ratio = [s / d if d != 0 else 1 for s, d in zip(single_ema, double_ema)]
        
        result = []
        for i in range(len(candles)):
            if i < period:
                result.append(0)
            else:
                result.append(sum(ema_ratio[i - period + 1:i + 1]))
        
        return result
    
    @staticmethod
    def vortex_indicator(candles: List[Dict], period: int = 14) -> Tuple[List[float], List[float]]:
        """Vortex Indicator (VI+ and VI-)"""
        if len(candles) < period + 1:
            return [0] * len(candles), [0] * len(candles)
        
        vm_plus = [0]
        vm_minus = [0]
        tr = [candles[0]['high'] - candles[0]['low']]
        
        for i in range(1, len(candles)):
            vm_plus.append(abs(candles[i]['high'] - candles[i - 1]['low']))
            vm_minus.append(abs(candles[i]['low'] - candles[i - 1]['high']))
            tr.append(max(
                candles[i]['high'] - candles[i]['low'],
                abs(candles[i]['high'] - candles[i - 1]['close']),
                abs(candles[i]['low'] - candles[i - 1]['close'])
            ))
        
        vi_plus = []
        vi_minus = []
        
        for i in range(len(candles)):
            if i < period:
                vi_plus.append(1)
                vi_minus.append(1)
            else:
                sum_vm_plus = sum(vm_plus[i - period + 1:i + 1])
                sum_vm_minus = sum(vm_minus[i - period + 1:i + 1])
                sum_tr = sum(tr[i - period + 1:i + 1])
                
                vi_plus.append(sum_vm_plus / sum_tr if sum_tr != 0 else 1)
                vi_minus.append(sum_vm_minus / sum_tr if sum_tr != 0 else 1)
        
        return vi_plus, vi_minus
    
    @staticmethod
    def rvi(candles: List[Dict], period: int = 10) -> Tuple[List[float], List[float]]:
        """Relative Vigor Index"""
        if len(candles) < period + 3:
            return [0] * len(candles), [0] * len(candles)
        
        close_open = [c['close'] - c['open'] for c in candles]
        high_low = [c['high'] - c['low'] for c in candles]
        
        # Symmetrically weighted moving average
        def swma(data):
            result = [0, 0, 0]
            for i in range(3, len(data)):
                result.append((data[i] + 2 * data[i-1] + 2 * data[i-2] + data[i-3]) / 6)
            return result
        
        num = swma(close_open)
        den = swma(high_low)
        
        rvi_line = []
        for i in range(len(candles)):
            if i < period:
                rvi_line.append(0)
            else:
                num_sum = sum(num[i - period + 1:i + 1])
                den_sum = sum(den[i - period + 1:i + 1])
                rvi_line.append(num_sum / den_sum if den_sum != 0 else 0)
        
        signal = swma(rvi_line)
        
        return rvi_line, signal
    
    @staticmethod
    def know_sure_thing(prices: List[float], 
                        roc1: int = 10, roc2: int = 15, roc3: int = 20, roc4: int = 30,
                        sma1: int = 10, sma2: int = 10, sma3: int = 10, sma4: int = 15,
                        signal: int = 9) -> Tuple[List[float], List[float]]:
        """Know Sure Thing (KST) Oscillator"""
        # Calculate ROCs
        def roc(data, period):
            result = [0] * period
            for i in range(period, len(data)):
                if data[i - period] != 0:
                    result.append((data[i] - data[i - period]) / data[i - period] * 100)
                else:
                    result.append(0)
            return result
        
        roc_1 = Indicators.sma(roc(prices, roc1), sma1)
        roc_2 = Indicators.sma(roc(prices, roc2), sma2)
        roc_3 = Indicators.sma(roc(prices, roc3), sma3)
        roc_4 = Indicators.sma(roc(prices, roc4), sma4)
        
        kst = [r1 + 2*r2 + 3*r3 + 4*r4 if all(x is not None for x in [r1, r2, r3, r4]) else 0
               for r1, r2, r3, r4 in zip(roc_1, roc_2, roc_3, roc_4)]
        
        signal_line = Indicators.sma(kst, signal)
        
        return kst, signal_line
    
    @staticmethod
    def connors_rsi(prices: List[float], rsi_period: int = 3, streak_period: int = 2, rank_period: int = 100) -> List[float]:
        """Connors RSI - Composite RSI"""
        # Standard RSI
        rsi = Indicators.rsi(prices, rsi_period)
        
        # Streak RSI
        streak = [0]
        for i in range(1, len(prices)):
            if prices[i] > prices[i - 1]:
                streak.append(streak[-1] + 1 if streak[-1] >= 0 else 1)
            elif prices[i] < prices[i - 1]:
                streak.append(streak[-1] - 1 if streak[-1] <= 0 else -1)
            else:
                streak.append(0)
        
        streak_rsi = Indicators.rsi([s + 100 for s in streak], streak_period)  # Offset for positive
        
        # Percent Rank
        pct_rank = []
        for i in range(len(prices)):
            if i < rank_period:
                pct_rank.append(50)
            else:
                window = prices[i - rank_period:i]
                change = prices[i] - prices[i - 1] if i > 0 else 0
                count_less = sum(1 for p in range(1, len(window)) if (window[p] - window[p-1]) < change)
                pct_rank.append(count_less / (rank_period - 1) * 100)
        
        # Combine
        crsi = [(r + s + p) / 3 for r, s, p in zip(rsi, streak_rsi, pct_rank)]
        
        return crsi
    
    @staticmethod
    def coppock_curve(prices: List[float], wma_period: int = 10, roc1: int = 14, roc2: int = 11) -> List[float]:
        """Coppock Curve - Long-term momentum"""
        roc_14 = Indicators.roc(prices, roc1)
        roc_11 = Indicators.roc(prices, roc2)
        
        combined = [r1 + r2 for r1, r2 in zip(roc_14, roc_11)]
        
        return Indicators.wma(combined, wma_period)
    
    @staticmethod
    def schaff_trend_cycle(prices: List[float], period: int = 10, fast: int = 23, slow: int = 50) -> List[float]:
        """Schaff Trend Cycle (STC)"""
        # MACD
        ema_fast = Indicators.ema(prices, fast)
        ema_slow = Indicators.ema(prices, slow)
        macd = [f - s for f, s in zip(ema_fast, ema_slow)]
        
        # Stochastic of MACD
        def stoch_smooth(data, period):
            result = []
            for i in range(len(data)):
                if i < period:
                    result.append(50)
                else:
                    window = data[i - period + 1:i + 1]
                    min_val = min(window)
                    max_val = max(window)
                    if max_val - min_val != 0:
                        result.append((data[i] - min_val) / (max_val - min_val) * 100)
                    else:
                        result.append(50)
            return result
        
        pf = stoch_smooth(macd, period)
        pf_smooth = Indicators.ema(pf, period)
        
        pff = stoch_smooth(pf_smooth, period)
        stc = Indicators.ema(pff, period)
        
        return stc
    
    @staticmethod
    def squeeze_momentum(candles: List[Dict], bb_period: int = 20, bb_mult: float = 2.0, 
                         kc_period: int = 20, kc_mult: float = 1.5) -> Tuple[List[float], List[bool]]:
        """Squeeze Momentum Indicator (TTM Squeeze)"""
        closes = [c['close'] for c in candles]
        
        # Bollinger Bands
        bb_upper, bb_middle, bb_lower = Indicators.bollinger_bands(closes, bb_period, bb_mult)
        
        # Keltner Channels  
        kc_upper, kc_middle, kc_lower = Indicators.keltner_channels(candles, kc_period, kc_period, kc_mult)
        
        # Squeeze detection (BB inside KC)
        squeeze_on = [bb_l > kc_l and bb_u < kc_u if all(x is not None for x in [bb_l, bb_u, kc_l, kc_u]) else False
                      for bb_l, bb_u, kc_l, kc_u in zip(bb_lower, bb_upper, kc_lower, kc_upper)]
        
        # Momentum
        highest = []
        lowest = []
        for i in range(len(candles)):
            start = max(0, i - kc_period + 1)
            highest.append(max(c['high'] for c in candles[start:i + 1]))
            lowest.append(min(c['low'] for c in candles[start:i + 1]))
        
        midline = [(h + l) / 2 for h, l in zip(highest, lowest)]
        sma_mid = Indicators.sma(midline, kc_period)
        
        momentum = [closes[i] - (sma_mid[i] + kc_middle[i]) / 2 if sma_mid[i] and kc_middle[i] else 0 
                   for i in range(len(candles))]
        
        return momentum, squeeze_on
    
    @staticmethod
    def percent_b(prices: List[float], period: int = 20, std_dev: float = 2.0) -> List[float]:
        """%B Indicator (Position within Bollinger Bands)"""
        upper, middle, lower = Indicators.bollinger_bands(prices, period, std_dev)
        
        result = []
        for i in range(len(prices)):
            if upper[i] and lower[i] and upper[i] != lower[i]:
                result.append((prices[i] - lower[i]) / (upper[i] - lower[i]))
            else:
                result.append(0.5)
        
        return result
    
    @staticmethod
    def bandwidth(prices: List[float], period: int = 20, std_dev: float = 2.0) -> List[float]:
        """Bollinger Bandwidth"""
        upper, middle, lower = Indicators.bollinger_bands(prices, period, std_dev)
        
        result = []
        for i in range(len(prices)):
            if middle[i] and middle[i] != 0:
                result.append((upper[i] - lower[i]) / middle[i] * 100)
            else:
                result.append(0)
        
        return result
    
    @staticmethod
    def linear_regression(prices: List[float], period: int = 14) -> Tuple[List[float], List[float], List[float]]:
        """Linear Regression (Value, Slope, R-Squared)"""
        if len(prices) < period:
            return prices.copy(), [0] * len(prices), [0] * len(prices)
        
        values = [None] * (period - 1)
        slopes = [0] * (period - 1)
        r_squared = [0] * (period - 1)
        
        for i in range(period - 1, len(prices)):
            window = prices[i - period + 1:i + 1]
            x = list(range(period))
            
            x_mean = sum(x) / period
            y_mean = sum(window) / period
            
            numerator = sum((x[j] - x_mean) * (window[j] - y_mean) for j in range(period))
            denominator = sum((x[j] - x_mean) ** 2 for j in range(period))
            
            if denominator != 0:
                slope = numerator / denominator
                intercept = y_mean - slope * x_mean
                value = intercept + slope * (period - 1)
                
                # R-squared
                ss_res = sum((window[j] - (intercept + slope * x[j])) ** 2 for j in range(period))
                ss_tot = sum((window[j] - y_mean) ** 2 for j in range(period))
                r2 = 1 - ss_res / ss_tot if ss_tot != 0 else 0
            else:
                slope = 0
                value = window[-1]
                r2 = 0
            
            values.append(value)
            slopes.append(slope)
            r_squared.append(r2)
        
        return values, slopes, r_squared
    
    @staticmethod
    def ehlers_fisher(candles: List[Dict], period: int = 10) -> Tuple[List[float], List[float]]:
        """Ehlers Fisher Transform"""
        highs = [c['high'] for c in candles]
        lows = [c['low'] for c in candles]
        
        # HL2
        hl2 = [(h + l) / 2 for h, l in zip(highs, lows)]
        
        max_high = []
        min_low = []
        for i in range(len(candles)):
            start = max(0, i - period + 1)
            max_high.append(max(hl2[start:i + 1]))
            min_low.append(min(hl2[start:i + 1]))
        
        value1 = []
        for i in range(len(candles)):
            if max_high[i] - min_low[i] != 0:
                raw = 2 * ((hl2[i] - min_low[i]) / (max_high[i] - min_low[i]) - 0.5)
            else:
                raw = 0
            
            raw = max(-0.999, min(0.999, raw))  # Bound to prevent log errors
            
            if i == 0:
                value1.append(raw)
            else:
                value1.append(0.5 * raw + 0.5 * value1[-1])
        
        fisher = []
        trigger = []
        
        for i, v in enumerate(value1):
            v = max(-0.999, min(0.999, v))
            f = 0.5 * math.log((1 + v) / (1 - v)) if 1 - v != 0 else 0
            fisher.append(f)
            trigger.append(fisher[-2] if i > 0 else 0)
        
        return fisher, trigger
    
    @staticmethod  
    def heikin_ashi(candles: List[Dict]) -> List[Dict]:
        """Heikin-Ashi Candles"""
        if not candles:
            return []
        
        ha = []
        
        for i, c in enumerate(candles):
            if i == 0:
                ha_close = (c['open'] + c['high'] + c['low'] + c['close']) / 4
                ha_open = (c['open'] + c['close']) / 2
            else:
                ha_close = (c['open'] + c['high'] + c['low'] + c['close']) / 4
                ha_open = (ha[-1]['open'] + ha[-1]['close']) / 2
            
            ha_high = max(c['high'], ha_open, ha_close)
            ha_low = min(c['low'], ha_open, ha_close)
            
            ha.append({
                'open': ha_open,
                'high': ha_high,
                'low': ha_low,
                'close': ha_close,
                'volume': c['volume']
            })
        
        return ha
    
    @staticmethod
    def fractal_indicator(candles: List[Dict], period: int = 5) -> Tuple[List[bool], List[bool]]:
        """Williams Fractal"""
        half = period // 2
        up_fractals = [False] * len(candles)
        down_fractals = [False] * len(candles)
        
        for i in range(half, len(candles) - half):
            # Up fractal
            is_up = True
            for j in range(1, half + 1):
                if candles[i]['high'] <= candles[i - j]['high'] or candles[i]['high'] <= candles[i + j]['high']:
                    is_up = False
                    break
            up_fractals[i] = is_up
            
            # Down fractal
            is_down = True
            for j in range(1, half + 1):
                if candles[i]['low'] >= candles[i - j]['low'] or candles[i]['low'] >= candles[i + j]['low']:
                    is_down = False
                    break
            down_fractals[i] = is_down
        
        return up_fractals, down_fractals
    
    @staticmethod
    def alligator(candles: List[Dict], jaw: int = 13, teeth: int = 8, lips: int = 5,
                  jaw_shift: int = 8, teeth_shift: int = 5, lips_shift: int = 3) -> Tuple[List[float], List[float], List[float]]:
        """Williams Alligator"""
        median = [(c['high'] + c['low']) / 2 for c in candles]
        
        # SMMA (Smoothed Moving Average)
        def smma(data, period):
            result = [data[0]]
            for i in range(1, len(data)):
                if i < period:
                    result.append(sum(data[:i+1]) / (i + 1))
                else:
                    result.append((result[-1] * (period - 1) + data[i]) / period)
            return result
        
        jaw_line = smma(median, jaw)
        teeth_line = smma(median, teeth)
        lips_line = smma(median, lips)
        
        # Shift forward
        jaw_shifted = [None] * jaw_shift + jaw_line[:-jaw_shift] if jaw_shift < len(jaw_line) else jaw_line
        teeth_shifted = [None] * teeth_shift + teeth_line[:-teeth_shift] if teeth_shift < len(teeth_line) else teeth_line
        lips_shifted = [None] * lips_shift + lips_line[:-lips_shift] if lips_shift < len(lips_line) else lips_line
        
        return jaw_shifted, teeth_shifted, lips_shifted
    
    @staticmethod
    def gator_oscillator(candles: List[Dict]) -> Tuple[List[float], List[float]]:
        """Gator Oscillator (based on Alligator)"""
        jaw, teeth, lips = Indicators.alligator(candles)
        
        upper = [abs(j - t) if j and t else 0 for j, t in zip(jaw, teeth)]
        lower = [-abs(t - l) if t and l else 0 for t, l in zip(teeth, lips)]
        
        return upper, lower


# Utility functions
def normalize_indicator(values: List[float], min_val: float = 0, max_val: float = 100) -> List[float]:
    """Normalize indicator values to a specific range"""
    if not values:
        return []
    
    v_min = min(values)
    v_max = max(values)
    
    if v_max == v_min:
        return [(min_val + max_val) / 2] * len(values)
    
    return [min_val + (v - v_min) / (v_max - v_min) * (max_val - min_val) for v in values]


class IndicatorCalculator:
    """
    Universal indicator calculator wrapper.
    Provides a unified interface for calculating any indicator.
    """
    
    def __init__(self):
        self.indicators = Indicators()
    
    def calculate(self, indicator_type: str, candles: List[Dict], **params) -> Any:
        """
        Calculate any indicator by type name.
        
        Args:
            indicator_type: Name of the indicator (e.g., 'rsi', 'macd', 'bollinger_bands')
            candles: List of OHLCV candles
            **params: Indicator-specific parameters
        
        Returns:
            Indicator values (format depends on indicator type)
        """
        closes = [c.get('close', 0) for c in candles]
        highs = [c.get('high', 0) for c in candles]
        lows = [c.get('low', 0) for c in candles]
        volumes = [c.get('volume', 0) for c in candles]
        
        # Moving Averages
        if indicator_type == 'sma':
            return Indicators.sma(closes, params.get('period', 20))
        
        elif indicator_type == 'ema':
            return Indicators.ema(closes, params.get('period', 20))
        
        elif indicator_type == 'wma':
            return Indicators.wma(closes, params.get('period', 20))
        
        elif indicator_type == 'hull_ma':
            return Indicators.hull_ma(closes, params.get('period', 20))
        
        elif indicator_type == 'vwap':
            return Indicators.vwap(candles, params.get('period'))
        
        # Momentum Indicators
        elif indicator_type == 'rsi':
            return Indicators.rsi(closes, params.get('period', 14))
        
        elif indicator_type == 'stochastic':
            k, d = Indicators.stochastic(
                candles, 
                params.get('k_period', 14),
                params.get('d_period', 3)
            )
            return {'k': k, 'd': d, 'stoch_k': k, 'stoch_d': d}
        
        elif indicator_type == 'macd':
            macd, signal, hist = Indicators.macd(
                closes,
                params.get('fast', 12),
                params.get('slow', 26),
                params.get('signal', 9)
            )
            return {'macd': macd, 'signal': signal, 'histogram': hist, 'macd_signal': signal}
        
        elif indicator_type == 'roc':
            return Indicators.roc(closes, params.get('period', 10))
        
        elif indicator_type == 'cci':
            return Indicators.cci(candles, params.get('period', 20))
        
        elif indicator_type == 'williams_r':
            return Indicators.williams_r(candles, params.get('period', 14))
        
        elif indicator_type == 'mfi':
            return Indicators.mfi(candles, params.get('period', 14))
        
        # Volatility Indicators
        elif indicator_type == 'bollinger_bands':
            upper, middle, lower = Indicators.bollinger_bands(
                closes,
                params.get('period', 20),
                params.get('std_dev', 2.0)
            )
            return {'upper': upper, 'middle': middle, 'lower': lower, 
                    'bb_upper': upper, 'bb_lower': lower, 'bb_middle': middle}
        
        elif indicator_type == 'atr':
            return Indicators.atr(candles, params.get('period', 14))
        
        elif indicator_type == 'keltner_channels':
            upper, middle, lower = Indicators.keltner_channels(
                candles,
                params.get('ema_period', 20),
                params.get('atr_period', 10),
                params.get('multiplier', 2.0)
            )
            return {'upper': upper, 'middle': middle, 'lower': lower}
        
        elif indicator_type == 'donchian_channels':
            upper, middle, lower = Indicators.donchian_channels(
                candles,
                params.get('period', 20)
            )
            return {'upper': upper, 'middle': middle, 'lower': lower}
        
        # Trend Indicators
        elif indicator_type == 'adx':
            adx, plus_di, minus_di = Indicators.adx(candles, params.get('period', 14))
            return adx
        
        elif indicator_type == 'adx_full':
            adx, plus_di, minus_di = Indicators.adx(candles, params.get('period', 14))
            return {'adx': adx, 'plus_di': plus_di, 'minus_di': minus_di}
        
        elif indicator_type == 'parabolic_sar':
            return Indicators.parabolic_sar(
                candles,
                params.get('af_start', 0.02),
                params.get('af_max', 0.2)
            )
        
        elif indicator_type == 'supertrend':
            value, direction = Indicators.supertrend(
                candles,
                params.get('period', 10),
                params.get('multiplier', 3.0)
            )
            return {'value': value, 'direction': direction, 
                    'supertrend': value, 'supertrend_dir': direction}
        
        # Volume Indicators
        elif indicator_type == 'obv':
            return Indicators.obv(candles)
        
        elif indicator_type == 'volume_sma':
            return Indicators.sma(volumes, params.get('period', 20))
        
        elif indicator_type == 'cvd':
            return Indicators.cvd(candles)
        
        elif indicator_type == 'volume_profile':
            return Indicators.volume_profile(candles, params.get('bins', 24))
        
        # Support/Resistance
        elif indicator_type == 'pivot_points':
            return Indicators.pivot_points(candles)
        
        elif indicator_type == 'fibonacci':
            # Calculate fibonacci from recent high/low
            lookback = params.get('lookback', 100)
            recent = candles[-lookback:] if len(candles) >= lookback else candles
            high = max(c.get('high', 0) for c in recent)
            low = min(c.get('low', float('inf')) for c in recent)
            return Indicators.fibonacci_retracement(high, low)
        
        elif indicator_type == 'support_resistance':
            return Indicators.detect_support_resistance(
                candles, 
                params.get('lookback', 50),
                params.get('tolerance', 0.02)
            )
        
        # Ichimoku
        elif indicator_type == 'ichimoku':
            tenkan, kijun, senkou_a, senkou_b, chikou = Indicators.ichimoku(
                candles,
                params.get('tenkan', 9),
                params.get('kijun', 26),
                params.get('senkou', 52)
            )
            return {
                'tenkan': tenkan, 'kijun': kijun,
                'senkou_a': senkou_a, 'senkou_b': senkou_b,
                'chikou': chikou
            }
        
        # Divergence
        elif indicator_type == 'divergence':
            return Indicators.detect_divergence(
                closes,
                Indicators.rsi(closes, 14),
                params.get('lookback', 20)
            )
        
        # Trend Strength
        elif indicator_type == 'trend_strength':
            return Indicators.calculate_trend_strength(candles)
        
        # ==================== EXTENDED MOVING AVERAGES ====================
        
        elif indicator_type == 'dema':
            return Indicators.dema(closes, params.get('period', 20))
        
        elif indicator_type == 'tema':
            return Indicators.tema(closes, params.get('period', 20))
        
        elif indicator_type == 'kama':
            return Indicators.kama(closes, params.get('period', 10), 
                                  params.get('fast', 2), params.get('slow', 30))
        
        elif indicator_type == 'zlema':
            return Indicators.zlema(closes, params.get('period', 20))
        
        elif indicator_type == 't3':
            return Indicators.t3(closes, params.get('period', 5), params.get('v_factor', 0.7))
        
        elif indicator_type == 'vidya':
            return Indicators.vidya(closes, params.get('period', 14), params.get('alpha', 0.2))
        
        # ==================== EXTENDED OSCILLATORS ====================
        
        elif indicator_type == 'stoch_rsi':
            k, d = Indicators.stoch_rsi(closes, params.get('period', 14),
                                       params.get('k_period', 3), params.get('d_period', 3))
            return {'k': k, 'd': d, 'stoch_rsi_k': k, 'stoch_rsi_d': d}
        
        elif indicator_type == 'ultimate_oscillator':
            return Indicators.ultimate_oscillator(candles, params.get('period1', 7),
                                                  params.get('period2', 14), params.get('period3', 28))
        
        elif indicator_type == 'awesome_oscillator':
            return Indicators.awesome_oscillator(candles, params.get('fast', 5), params.get('slow', 34))
        
        elif indicator_type == 'accelerator_oscillator':
            return Indicators.accelerator_oscillator(candles, params.get('fast', 5), params.get('slow', 34))
        
        elif indicator_type == 'trix':
            return Indicators.trix(closes, params.get('period', 15))
        
        elif indicator_type == 'cmo':
            return Indicators.cmo(closes, params.get('period', 14))
        
        elif indicator_type == 'dpo':
            return Indicators.dpo(closes, params.get('period', 20))
        
        elif indicator_type == 'ppo':
            ppo, signal, hist = Indicators.ppo(closes, params.get('fast', 12),
                                              params.get('slow', 26), params.get('signal', 9))
            return {'ppo': ppo, 'signal': signal, 'histogram': hist}
        
        elif indicator_type == 'aroon':
            up, down, osc = Indicators.aroon(candles, params.get('period', 25))
            return {'aroon_up': up, 'aroon_down': down, 'aroon_osc': osc}
        
        elif indicator_type == 'chaikin_oscillator':
            return Indicators.chaikin_oscillator(candles, params.get('fast', 3), params.get('slow', 10))
        
        elif indicator_type == 'klinger_oscillator':
            kvo, signal = Indicators.klinger_oscillator(candles, params.get('fast', 34),
                                                        params.get('slow', 55), params.get('signal', 13))
            return {'kvo': kvo, 'signal': signal}
        
        elif indicator_type == 'elder_ray':
            bull, bear = Indicators.elder_ray(candles, params.get('period', 13))
            return {'bull_power': bull, 'bear_power': bear}
        
        elif indicator_type == 'force_index':
            return Indicators.force_index(candles, params.get('period', 13))
        
        elif indicator_type == 'choppiness_index':
            return Indicators.choppiness_index(candles, params.get('period', 14))
        
        elif indicator_type == 'mass_index':
            return Indicators.mass_index(candles, params.get('period', 25), params.get('ema_period', 9))
        
        elif indicator_type == 'vortex':
            vi_plus, vi_minus = Indicators.vortex_indicator(candles, params.get('period', 14))
            return {'vi_plus': vi_plus, 'vi_minus': vi_minus}
        
        elif indicator_type == 'rvi':
            rvi, signal = Indicators.rvi(candles, params.get('period', 10))
            return {'rvi': rvi, 'signal': signal}
        
        elif indicator_type == 'kst':
            kst, signal = Indicators.know_sure_thing(closes)
            return {'kst': kst, 'signal': signal}
        
        elif indicator_type == 'connors_rsi':
            return Indicators.connors_rsi(closes, params.get('rsi_period', 3),
                                         params.get('streak_period', 2), params.get('rank_period', 100))
        
        elif indicator_type == 'coppock_curve':
            return Indicators.coppock_curve(closes, params.get('wma_period', 10),
                                           params.get('roc1', 14), params.get('roc2', 11))
        
        elif indicator_type == 'schaff_trend_cycle':
            return Indicators.schaff_trend_cycle(closes, params.get('period', 10),
                                                params.get('fast', 23), params.get('slow', 50))
        
        elif indicator_type == 'squeeze_momentum':
            momentum, squeeze_on = Indicators.squeeze_momentum(candles, params.get('bb_period', 20),
                                                               params.get('bb_mult', 2.0),
                                                               params.get('kc_period', 20),
                                                               params.get('kc_mult', 1.5))
            return {'momentum': momentum, 'squeeze_on': squeeze_on}
        
        elif indicator_type == 'percent_b':
            return Indicators.percent_b(closes, params.get('period', 20), params.get('std_dev', 2.0))
        
        elif indicator_type == 'bandwidth':
            return Indicators.bandwidth(closes, params.get('period', 20), params.get('std_dev', 2.0))
        
        elif indicator_type == 'linear_regression':
            values, slopes, r_squared = Indicators.linear_regression(closes, params.get('period', 14))
            return {'value': values, 'slope': slopes, 'r_squared': r_squared}
        
        elif indicator_type == 'ehlers_fisher':
            fisher, trigger = Indicators.ehlers_fisher(candles, params.get('period', 10))
            return {'fisher': fisher, 'trigger': trigger}
        
        elif indicator_type == 'heikin_ashi':
            return Indicators.heikin_ashi(candles)
        
        elif indicator_type == 'fractal':
            up, down = Indicators.fractal_indicator(candles, params.get('period', 5))
            return {'up_fractals': up, 'down_fractals': down}
        
        elif indicator_type == 'alligator':
            jaw, teeth, lips = Indicators.alligator(candles)
            return {'jaw': jaw, 'teeth': teeth, 'lips': lips}
        
        elif indicator_type == 'gator':
            upper, lower = Indicators.gator_oscillator(candles)
            return {'upper': upper, 'lower': lower}
        
        elif indicator_type == 'adl':
            return Indicators.adl(candles)
        
        else:
            raise ValueError(f"Unknown indicator type: {indicator_type}")
    
    def calculate_multiple(self, indicator_configs: List[Dict], candles: List[Dict]) -> Dict[str, Any]:
        """
        Calculate multiple indicators at once.
        
        Args:
            indicator_configs: List of {'type': str, 'params': dict, 'alias': str}
            candles: OHLCV candles
        
        Returns:
            Dict mapping aliases to indicator values
        """
        results = {}
        
        for config in indicator_configs:
            ind_type = config.get('type')
            params = config.get('params', {})
            alias = config.get('alias', ind_type)
            
            try:
                result = self.calculate(ind_type, candles, **params)
                results[alias] = result
            except Exception as e:
                results[alias] = None
        
        return results
    
    def get_available_indicators(self) -> List[str]:
        """Get list of all available indicator types with categories"""
        return {
            'moving_averages': [
                'sma', 'ema', 'wma', 'hull_ma', 'vwap', 
                'dema', 'tema', 'kama', 'zlema', 't3', 'vidya'
            ],
            'oscillators': [
                'rsi', 'stochastic', 'stoch_rsi', 'macd', 'roc', 'cci', 
                'williams_r', 'mfi', 'cmo', 'dpo', 'ppo', 'trix',
                'ultimate_oscillator', 'awesome_oscillator', 'accelerator_oscillator',
                'connors_rsi', 'coppock_curve', 'schaff_trend_cycle', 'rvi'
            ],
            'volatility': [
                'bollinger_bands', 'atr', 'keltner_channels', 'donchian_channels',
                'percent_b', 'bandwidth', 'choppiness_index', 'mass_index',
                'squeeze_momentum'
            ],
            'trend': [
                'adx', 'adx_full', 'parabolic_sar', 'supertrend',
                'aroon', 'vortex', 'linear_regression', 'trend_strength'
            ],
            'volume': [
                'obv', 'volume_sma', 'cvd', 'volume_profile', 'adl',
                'chaikin_oscillator', 'klinger_oscillator', 'force_index'
            ],
            'bill_williams': [
                'alligator', 'gator', 'awesome_oscillator', 
                'accelerator_oscillator', 'fractal'
            ],
            'support_resistance': [
                'pivot_points', 'fibonacci', 'support_resistance'
            ],
            'ichimoku_cloud': [
                'ichimoku'
            ],
            'transforms': [
                'ehlers_fisher', 'heikin_ashi'
            ],
            'composite': [
                'elder_ray', 'kst', 'divergence'
            ]
        }
    
    def get_indicator_info(self, indicator_type: str) -> Dict:
        """Get detailed information about an indicator"""
        info_db = {
            # Moving Averages
            'sma': {
                'name': 'Simple Moving Average',
                'category': 'moving_averages',
                'params': {'period': {'type': 'int', 'default': 20, 'min': 1, 'max': 500}},
                'output': 'single',
                'description': 'Average of closing prices over N periods'
            },
            'ema': {
                'name': 'Exponential Moving Average',
                'category': 'moving_averages',
                'params': {'period': {'type': 'int', 'default': 20, 'min': 1, 'max': 500}},
                'output': 'single',
                'description': 'Weighted average giving more weight to recent prices'
            },
            'wma': {
                'name': 'Weighted Moving Average',
                'category': 'moving_averages',
                'params': {'period': {'type': 'int', 'default': 20, 'min': 1, 'max': 500}},
                'output': 'single',
                'description': 'Linear weighted average of prices'
            },
            'hull_ma': {
                'name': 'Hull Moving Average',
                'category': 'moving_averages',
                'params': {'period': {'type': 'int', 'default': 20, 'min': 1, 'max': 500}},
                'output': 'single',
                'description': 'Faster MA with reduced lag by Alan Hull'
            },
            'dema': {
                'name': 'Double EMA',
                'category': 'moving_averages',
                'params': {'period': {'type': 'int', 'default': 20, 'min': 1, 'max': 500}},
                'output': 'single',
                'description': 'Double exponential smoothing for less lag'
            },
            'tema': {
                'name': 'Triple EMA',
                'category': 'moving_averages',
                'params': {'period': {'type': 'int', 'default': 20, 'min': 1, 'max': 500}},
                'output': 'single',
                'description': 'Triple exponential smoothing for minimal lag'
            },
            'kama': {
                'name': 'Kaufman Adaptive MA',
                'category': 'moving_averages',
                'params': {
                    'period': {'type': 'int', 'default': 10, 'min': 2, 'max': 100},
                    'fast': {'type': 'int', 'default': 2, 'min': 1, 'max': 10},
                    'slow': {'type': 'int', 'default': 30, 'min': 10, 'max': 100}
                },
                'output': 'single',
                'description': 'Adapts to market volatility automatically'
            },
            'zlema': {
                'name': 'Zero Lag EMA',
                'category': 'moving_averages',
                'params': {'period': {'type': 'int', 'default': 20, 'min': 1, 'max': 500}},
                'output': 'single',
                'description': 'EMA with lag removed using momentum'
            },
            't3': {
                'name': 'Tillson T3',
                'category': 'moving_averages',
                'params': {
                    'period': {'type': 'int', 'default': 5, 'min': 1, 'max': 100},
                    'v_factor': {'type': 'float', 'default': 0.7, 'min': 0, 'max': 1}
                },
                'output': 'single',
                'description': 'Smooth moving average with minimal lag'
            },
            'vidya': {
                'name': 'Variable Index Dynamic Average',
                'category': 'moving_averages',
                'params': {
                    'period': {'type': 'int', 'default': 14, 'min': 2, 'max': 100},
                    'alpha': {'type': 'float', 'default': 0.2, 'min': 0.01, 'max': 1}
                },
                'output': 'single',
                'description': 'Volatility-adjusted moving average'
            },
            
            # Oscillators
            'rsi': {
                'name': 'Relative Strength Index',
                'category': 'oscillators',
                'params': {'period': {'type': 'int', 'default': 14, 'min': 2, 'max': 100}},
                'output': 'single',
                'range': [0, 100],
                'description': 'Measures overbought/oversold conditions'
            },
            'stochastic': {
                'name': 'Stochastic Oscillator',
                'category': 'oscillators',
                'params': {
                    'k_period': {'type': 'int', 'default': 14, 'min': 1, 'max': 100},
                    'd_period': {'type': 'int', 'default': 3, 'min': 1, 'max': 50}
                },
                'output': {'k': 'line', 'd': 'line'},
                'range': [0, 100],
                'description': 'Momentum indicator comparing close to high-low range'
            },
            'stoch_rsi': {
                'name': 'Stochastic RSI',
                'category': 'oscillators',
                'params': {
                    'period': {'type': 'int', 'default': 14, 'min': 2, 'max': 100},
                    'k_period': {'type': 'int', 'default': 3, 'min': 1, 'max': 50},
                    'd_period': {'type': 'int', 'default': 3, 'min': 1, 'max': 50}
                },
                'output': {'k': 'line', 'd': 'line'},
                'range': [0, 100],
                'description': 'Stochastic applied to RSI for extreme readings'
            },
            'macd': {
                'name': 'MACD',
                'category': 'oscillators',
                'params': {
                    'fast': {'type': 'int', 'default': 12, 'min': 1, 'max': 100},
                    'slow': {'type': 'int', 'default': 26, 'min': 1, 'max': 200},
                    'signal': {'type': 'int', 'default': 9, 'min': 1, 'max': 50}
                },
                'output': {'macd': 'line', 'signal': 'line', 'histogram': 'histogram'},
                'description': 'Moving Average Convergence Divergence'
            },
            'cmo': {
                'name': 'Chande Momentum Oscillator',
                'category': 'oscillators',
                'params': {'period': {'type': 'int', 'default': 14, 'min': 2, 'max': 100}},
                'output': 'single',
                'range': [-100, 100],
                'description': 'Measures momentum using up/down sum ratio'
            },
            'ultimate_oscillator': {
                'name': 'Ultimate Oscillator',
                'category': 'oscillators',
                'params': {
                    'period1': {'type': 'int', 'default': 7, 'min': 1, 'max': 50},
                    'period2': {'type': 'int', 'default': 14, 'min': 1, 'max': 100},
                    'period3': {'type': 'int', 'default': 28, 'min': 1, 'max': 200}
                },
                'output': 'single',
                'range': [0, 100],
                'description': 'Multi-timeframe momentum oscillator by Larry Williams'
            },
            'awesome_oscillator': {
                'name': 'Awesome Oscillator',
                'category': 'oscillators',
                'params': {
                    'fast': {'type': 'int', 'default': 5, 'min': 1, 'max': 50},
                    'slow': {'type': 'int', 'default': 34, 'min': 5, 'max': 100}
                },
                'output': 'histogram',
                'description': 'Bill Williams momentum indicator'
            },
            
            # Volatility
            'bollinger_bands': {
                'name': 'Bollinger Bands',
                'category': 'volatility',
                'params': {
                    'period': {'type': 'int', 'default': 20, 'min': 2, 'max': 100},
                    'std_dev': {'type': 'float', 'default': 2.0, 'min': 0.5, 'max': 5}
                },
                'output': {'upper': 'line', 'middle': 'line', 'lower': 'line'},
                'description': 'Volatility bands around moving average'
            },
            'atr': {
                'name': 'Average True Range',
                'category': 'volatility',
                'params': {'period': {'type': 'int', 'default': 14, 'min': 1, 'max': 100}},
                'output': 'single',
                'description': 'Measures market volatility'
            },
            'squeeze_momentum': {
                'name': 'TTM Squeeze',
                'category': 'volatility',
                'params': {
                    'bb_period': {'type': 'int', 'default': 20, 'min': 5, 'max': 100},
                    'bb_mult': {'type': 'float', 'default': 2.0, 'min': 1, 'max': 4},
                    'kc_period': {'type': 'int', 'default': 20, 'min': 5, 'max': 100},
                    'kc_mult': {'type': 'float', 'default': 1.5, 'min': 0.5, 'max': 3}
                },
                'output': {'momentum': 'histogram', 'squeeze_on': 'dots'},
                'description': 'Volatility squeeze followed by breakout momentum'
            },
            'choppiness_index': {
                'name': 'Choppiness Index',
                'category': 'volatility',
                'params': {'period': {'type': 'int', 'default': 14, 'min': 1, 'max': 100}},
                'output': 'single',
                'range': [0, 100],
                'description': 'Measures market trendiness vs choppiness'
            },
            
            # Trend
            'adx': {
                'name': 'Average Directional Index',
                'category': 'trend',
                'params': {'period': {'type': 'int', 'default': 14, 'min': 1, 'max': 100}},
                'output': 'single',
                'range': [0, 100],
                'description': 'Measures trend strength'
            },
            'supertrend': {
                'name': 'Supertrend',
                'category': 'trend',
                'params': {
                    'period': {'type': 'int', 'default': 10, 'min': 1, 'max': 100},
                    'multiplier': {'type': 'float', 'default': 3.0, 'min': 0.5, 'max': 10}
                },
                'output': {'value': 'line', 'direction': 'signals'},
                'description': 'Trend-following indicator with buy/sell signals'
            },
            'aroon': {
                'name': 'Aroon',
                'category': 'trend',
                'params': {'period': {'type': 'int', 'default': 25, 'min': 1, 'max': 100}},
                'output': {'aroon_up': 'line', 'aroon_down': 'line', 'aroon_osc': 'line'},
                'range': [0, 100],
                'description': 'Identifies trend changes and strength'
            },
            'vortex': {
                'name': 'Vortex Indicator',
                'category': 'trend',
                'params': {'period': {'type': 'int', 'default': 14, 'min': 1, 'max': 100}},
                'output': {'vi_plus': 'line', 'vi_minus': 'line'},
                'description': 'Trend direction via positive/negative movement'
            },
            
            # Volume
            'obv': {
                'name': 'On Balance Volume',
                'category': 'volume',
                'params': {},
                'output': 'single',
                'description': 'Cumulative volume flow indicator'
            },
            'klinger_oscillator': {
                'name': 'Klinger Volume Oscillator',
                'category': 'volume',
                'params': {
                    'fast': {'type': 'int', 'default': 34, 'min': 1, 'max': 100},
                    'slow': {'type': 'int', 'default': 55, 'min': 1, 'max': 200},
                    'signal': {'type': 'int', 'default': 13, 'min': 1, 'max': 50}
                },
                'output': {'kvo': 'line', 'signal': 'line'},
                'description': 'Volume-based trend indicator'
            },
            
            # Bill Williams
            'alligator': {
                'name': 'Williams Alligator',
                'category': 'bill_williams',
                'params': {},
                'output': {'jaw': 'line', 'teeth': 'line', 'lips': 'line'},
                'description': 'Trend indicator with 3 smoothed MAs'
            },
            'fractal': {
                'name': 'Williams Fractal',
                'category': 'bill_williams',
                'params': {'period': {'type': 'int', 'default': 5, 'min': 3, 'max': 21}},
                'output': {'up_fractals': 'arrows', 'down_fractals': 'arrows'},
                'description': 'Identifies reversal points'
            },
            
            # Ichimoku
            'ichimoku': {
                'name': 'Ichimoku Cloud',
                'category': 'ichimoku_cloud',
                'params': {
                    'tenkan': {'type': 'int', 'default': 9, 'min': 1, 'max': 50},
                    'kijun': {'type': 'int', 'default': 26, 'min': 1, 'max': 100},
                    'senkou': {'type': 'int', 'default': 52, 'min': 1, 'max': 200}
                },
                'output': {'tenkan': 'line', 'kijun': 'line', 'senkou_a': 'cloud', 
                          'senkou_b': 'cloud', 'chikou': 'line'},
                'description': 'Complete trading system with cloud visualization'
            },
            
            # Transforms
            'ehlers_fisher': {
                'name': 'Ehlers Fisher Transform',
                'category': 'transforms',
                'params': {'period': {'type': 'int', 'default': 10, 'min': 2, 'max': 100}},
                'output': {'fisher': 'line', 'trigger': 'line'},
                'description': 'Transforms prices to Gaussian distribution'
            },
            'heikin_ashi': {
                'name': 'Heikin-Ashi',
                'category': 'transforms',
                'params': {},
                'output': 'candles',
                'description': 'Modified candlesticks for trend visualization'
            }
        }
        
        return info_db.get(indicator_type, {
            'name': indicator_type.replace('_', ' ').title(),
            'category': 'other',
            'params': {},
            'output': 'single',
            'description': 'No description available'
        })
