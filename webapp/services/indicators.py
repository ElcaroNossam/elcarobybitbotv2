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
