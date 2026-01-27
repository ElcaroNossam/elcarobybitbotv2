"""
Enliko Advanced System Tests
Tests for: Position Calculator, Screener, Backtest Engine, Trading Terminal

Run: python -m pytest tests/test_advanced_features.py -v
"""
import pytest
import asyncio
from webapp.services.position_calculator import PositionSizeCalculator, PositionCalculation
from webapp.services.advanced_indicators import indicator_calculator, TrendIndicators, MomentumIndicators
from webapp.services.orderbook_analyzer import orderbook_analyzer, backtest_orderbook_simulator
from webapp.services.risk_management import RiskManager, PositionSizingMethod, kelly_calculator, risk_metrics_calculator, TradeResult
from webapp.services.multi_timeframe import multi_tf_analyzer
from webapp.services.strategy_builder import strategy_builder, StrategyConfig, Condition, ConditionGroup
from webapp.services.monte_carlo import monte_carlo_simulator, stress_tester, robustness_analyzer
from webapp.services.walk_forward import walk_forward_optimizer, genetic_optimizer
import numpy as np


# ==================== POSITION CALCULATOR TESTS ====================

class TestPositionCalculator:
    """Test position size calculator"""
    
    def test_basic_long_calculation(self):
        """Test basic LONG position calculation"""
        calc = PositionSizeCalculator.calculate(
            account_balance=10000,
            entry_price=50000,
            stop_loss_price=49000,  # 2% stop
            risk_percent=1.0,  # Risk 1% = $100
            leverage=10,
            side="Buy"
        )
        
        # Verify stop loss percent
        assert abs(calc.stop_loss_percent - 2.0) < 0.01
        
        # Verify risk amount
        assert calc.risk_amount_usd == 100.0
        
        # Verify position size: risk / (price * sl_pct/100) = 100 / (50000 * 0.02) = 0.1 BTC
        assert abs(calc.position_size - 0.1) < 0.001
        
        # Verify position value
        assert abs(calc.position_value_usd - 5000) < 1
        
        # Verify margin
        assert abs(calc.margin_required - 500) < 1  # 5000 / 10 leverage
    
    def test_basic_short_calculation(self):
        """Test basic SHORT position calculation"""
        calc = PositionSizeCalculator.calculate(
            account_balance=10000,
            entry_price=50000,
            stop_loss_price=51000,  # 2% stop above
            risk_percent=1.0,
            leverage=10,
            side="Sell"
        )
        
        assert abs(calc.stop_loss_percent - 2.0) < 0.01
        assert calc.risk_amount_usd == 100.0
        assert abs(calc.position_size - 0.1) < 0.001
    
    def test_with_take_profit(self):
        """Test calculation with take profit"""
        calc = PositionSizeCalculator.calculate(
            account_balance=10000,
            entry_price=50000,
            stop_loss_price=49000,  # 2% SL
            risk_percent=1.0,
            leverage=10,
            side="Buy",
            take_profit_price=52000  # 4% TP
        )
        
        assert calc.take_profit_percent is not None
        assert abs(calc.take_profit_percent - 4.0) < 0.01
        assert calc.potential_profit_usd is not None
        assert abs(calc.potential_profit_usd - 200) < 1  # 0.1 BTC * $2000 gain
        assert calc.risk_reward_ratio is not None
        assert abs(calc.risk_reward_ratio - 2.0) < 0.01  # $200 profit / $100 risk
    
    def test_percent_based_calculation(self):
        """Test calculation from percentage stop loss"""
        calc = PositionSizeCalculator.calculate_from_percent(
            account_balance=10000,
            entry_price=50000,
            stop_loss_percent=2.0,
            risk_percent=1.0,
            leverage=10,
            side="Buy",
            take_profit_percent=4.0
        )
        
        assert abs(calc.stop_loss_price - 49000) < 1
        assert abs(calc.take_profit_price - 52000) < 1
    
    def test_insufficient_balance(self):
        """Test error when margin exceeds balance"""
        with pytest.raises(ValueError, match="Insufficient balance"):
            PositionSizeCalculator.calculate(
                account_balance=100,  # Too small
                entry_price=50000,
                stop_loss_price=49000,
                risk_percent=50.0,  # Risk $50, but margin would be $2500 (50000*0.1/2)
                leverage=2
            )
    
    def test_invalid_stop_loss_position(self):
        """Test validation of stop loss position"""
        # LONG with SL above entry
        with pytest.raises(ValueError, match="Stop loss must be below"):
            PositionSizeCalculator.calculate(
                account_balance=10000,
                entry_price=50000,
                stop_loss_price=51000,  # Wrong direction
                risk_percent=1.0,
                side="Buy"
            )
        
        # SHORT with SL below entry
        with pytest.raises(ValueError, match="Stop loss must be above"):
            PositionSizeCalculator.calculate(
                account_balance=10000,
                entry_price=50000,
                stop_loss_price=49000,  # Wrong direction
                risk_percent=1.0,
                side="Sell"
            )
    
    def test_quick_calculation(self):
        """Test quick calculation"""
        size = PositionSizeCalculator.calculate_quick(
            balance=10000,
            price=50000,
            sl_percent=2.0,
            risk_percent=1.0,
            leverage=10
        )
        
        assert abs(size - 0.1) < 0.001


# ==================== ADVANCED INDICATORS TESTS ====================

class TestAdvancedIndicators:
    """Test advanced indicators library"""
    
    def test_hull_ma(self):
        """Test Hull Moving Average"""
        data = list(range(1, 101))  # Simple increasing series
        hma = TrendIndicators.hull_ma(data, period=9)
        
        assert len(hma) == len(data)
        assert hma[-1] is not None  # Should have value at end
    
    def test_rsi(self):
        """Test RSI indicator"""
        # Create price data with clear trend
        data = [100 + i for i in range(50)]  # Uptrend
        rsi = MomentumIndicators.rsi(data, period=14)
        
        assert len(rsi) == len(data)
        # RSI should be > 50 in uptrend
        assert rsi[-1] is not None
        assert rsi[-1] > 50
    
    def test_indicator_calculator(self):
        """Test unified indicator calculator"""
        candle_data = {
            "open": [100 + i * 0.5 for i in range(100)],
            "high": [102 + i * 0.5 for i in range(100)],
            "low": [99 + i * 0.5 for i in range(100)],
            "close": [101 + i * 0.5 for i in range(100)],
            "volume": [1000000] * 100
        }
        
        # Test RSI
        rsi = indicator_calculator.calculate('rsi', candle_data, {"period": 14})
        assert isinstance(rsi, list)
        assert len(rsi) == 100
        
        # Test MACD
        macd = indicator_calculator.calculate('macd', candle_data, {})
        assert isinstance(macd, dict)
        assert 'macd' in macd
        assert 'signal' in macd
        assert 'histogram' in macd


# ==================== ORDERBOOK ANALYZER TESTS ====================

class TestOrderbookAnalyzer:
    """Test orderbook analysis"""
    
    @pytest.mark.asyncio
    async def test_generate_synthetic_orderbook(self):
        """Test synthetic orderbook generation"""
        orderbook = backtest_orderbook_simulator.generate_synthetic_orderbook(
            mid_price=50000,
            volume_24h=1000000000,
            volatility=0.01
        )
        
        assert orderbook is not None
        assert len(orderbook.bids) > 0
        assert len(orderbook.asks) > 0
        assert orderbook.best_bid is not None
        assert orderbook.best_ask is not None
        assert orderbook.best_bid.price < orderbook.best_ask.price
    
    def test_slippage_calculation(self):
        """Test slippage calculation"""
        orderbook = backtest_orderbook_simulator.generate_synthetic_orderbook(
            mid_price=50000,
            volume_24h=1000000000,
            volatility=0.01
        )
        
        # Calculate slippage for $10,000 buy
        slippage = orderbook_analyzer.calculate_slippage(orderbook, "buy", 10000)
        
        assert "slippage_percent" in slippage
        assert "avg_price" in slippage
        assert slippage["slippage_percent"] >= 0
        assert slippage["avg_price"] >= orderbook.best_ask.price


# ==================== RISK MANAGEMENT TESTS ====================

class TestRiskManagement:
    """Test risk management system"""
    
    def test_kelly_criterion(self):
        """Test Kelly Criterion calculation"""
        kelly = kelly_calculator.calculate(
            win_rate=0.6,
            avg_win=5.0,
            avg_loss=3.0,
            max_kelly=0.25
        )
        
        assert kelly > 0
        assert kelly <= 0.25  # Should not exceed max
    
    def test_kelly_from_trades(self):
        """Test Kelly from trade history"""
        trades = [
            TradeResult(pnl=100, pnl_percent=5.0, win=True, holding_bars=10),
            TradeResult(pnl=-50, pnl_percent=-2.5, win=False, holding_bars=5),
            TradeResult(pnl=150, pnl_percent=7.5, win=True, holding_bars=15),
            TradeResult(pnl=-60, pnl_percent=-3.0, win=False, holding_bars=8),
            TradeResult(pnl=120, pnl_percent=6.0, win=True, holding_bars=12),
        ]
        
        kelly = kelly_calculator.calculate_from_trades(trades)
        assert kelly >= 0
    
    def test_sharpe_ratio(self):
        """Test Sharpe ratio calculation"""
        returns = [0.01, 0.02, -0.01, 0.03, 0.01, -0.02, 0.02, 0.01]
        sharpe = risk_metrics_calculator.sharpe_ratio(returns)
        
        assert sharpe != 0
    
    def test_risk_manager_position_sizing(self):
        """Test risk manager position sizing"""
        manager = RiskManager(
            max_risk_per_trade=1.0,
            sizing_method=PositionSizingMethod.FIXED_PERCENT
        )
        
        size_info = manager.calculate_position_size(
            account_balance=10000,
            entry_price=50000,
            stop_loss_price=49000
        )
        
        assert "size" in size_info
        assert "risk_amount" in size_info
        assert size_info["size"] > 0


# ==================== MULTI-TIMEFRAME TESTS ====================

class TestMultiTimeframe:
    """Test multi-timeframe analysis"""
    
    @pytest.mark.asyncio
    async def test_fetch_multiple_timeframes(self):
        """Test fetching multiple timeframes"""
        # This will hit real API - might fail without connection
        try:
            tf_data = await multi_tf_analyzer.fetch_multiple_timeframes(
                symbol="BTCUSDT",
                timeframes=["15m", "1h"],
                exchange="binance"
            )
            
            assert isinstance(tf_data, dict)
        except Exception:
            pytest.skip("API connection not available")
    
    def test_timeframe_converter(self):
        """Test timeframe conversion"""
        from webapp.services.multi_timeframe import TimeframeConverter
        
        assert TimeframeConverter.to_minutes("1h") == 60
        assert TimeframeConverter.to_minutes("4h") == 240
        assert TimeframeConverter.to_minutes("1d") == 1440
        
        higher_tfs = TimeframeConverter.get_higher_timeframes("15m", count=3)
        assert "15m" not in higher_tfs
        assert all(TimeframeConverter.to_minutes(tf) > 15 for tf in higher_tfs)


# ==================== STRATEGY BUILDER TESTS ====================

class TestStrategyBuilder:
    """Test strategy builder"""
    
    def test_create_rsi_strategy(self):
        """Test creating RSI strategy"""
        strategy = strategy_builder.create_rsi_strategy()
        
        assert strategy.name == "RSI Mean Reversion"
        assert strategy.long_entry is not None
        assert strategy.short_entry is not None
        assert len(strategy.exit_rules) > 0
    
    def test_strategy_serialization(self):
        """Test strategy to/from JSON"""
        strategy = strategy_builder.create_rsi_strategy()
        
        # To JSON
        json_str = strategy.to_json()
        assert isinstance(json_str, str)
        assert "RSI" in json_str
        
        # From JSON
        restored = StrategyConfig.from_json(json_str)
        assert restored.name == strategy.name
        assert restored.long_entry is not None


# ==================== MONTE CARLO TESTS ====================

class TestMonteCarlo:
    """Test Monte Carlo simulation"""
    
    def test_trade_sequence_simulation(self):
        """Test trade sequence randomization"""
        trades_pnl = [100, -50, 150, -60, 120, -40, 180, -70, 90, -30] * 5  # 50 trades
        
        result = monte_carlo_simulator.run_trade_sequence_simulation(
            trades_pnl,
            initial_balance=10000
        )
        
        assert result.simulations == 10000
        assert result.mean_return != 0
        assert result.probability_profit >= 0
        assert result.probability_profit <= 1
    
    def test_stress_testing(self):
        """Test stress testing"""
        trades_pnl = [100, -50, 150, -60, 120] * 10
        equity_curve = [10000]
        
        for pnl in trades_pnl:
            equity_curve.append(equity_curve[-1] + pnl)
        
        tests = stress_tester.run_all_stress_tests(
            equity_curve,
            trades_pnl,
            10000
        )
        
        assert len(tests) > 0
        assert all(isinstance(t.survived, bool) for t in tests)
    
    def test_robustness_score(self):
        """Test robustness score calculation"""
        from webapp.services.monte_carlo import MonteCarloResult
        
        mc_result = MonteCarloResult(
            simulations=10000,
            mean_return=15.0,
            median_return=14.0,
            std_dev=5.0,
            confidence_95_lower=5.0,
            confidence_95_upper=25.0,
            confidence_99_lower=2.0,
            confidence_99_upper=28.0,
            max_drawdown_mean=10.0,
            max_drawdown_worst=20.0,
            max_drawdown_best=5.0,
            probability_profit=0.65,
            probability_10_percent=0.55,
            probability_20_percent=0.40,
            probability_50_percent=0.15,
            risk_of_ruin=0.05,
            expected_value=15.0,
            value_at_risk_95=-5.0,
            conditional_var_95=-8.0
        )
        
        tests = []  # Empty stress tests for this example
        
        score = robustness_analyzer.calculate_robustness_score(mc_result, tests)
        
        assert "total_score" in score
        assert score["total_score"] >= 0
        assert score["total_score"] <= 100
        assert "rating" in score


# ==================== WALK-FORWARD TESTS ====================

class TestWalkForward:
    """Test walk-forward optimization"""
    
    def test_data_splitting(self):
        """Test splitting data into train/test periods"""
        from datetime import datetime, timedelta
        
        # Generate 730 days (2 years) of candles - enough for walk-forward
        base_date = datetime(2024, 1, 1)
        candles = [
            {
                "timestamp": (base_date + timedelta(days=i)).timestamp() * 1000,
                "time": (base_date + timedelta(days=i)).isoformat() + "Z",
                "open": 50000,
                "high": 51000,
                "low": 49000,
                "close": 50500,
                "volume": 1000000
            }
            for i in range(730)
        ]
        
        # Split without custom parameters (uses defaults)
        periods = walk_forward_optimizer.split_data(candles)
        
        # Should have at least 1 period
        assert len(periods) > 0, f"Expected periods > 0, got {len(periods)}"
        assert all(len(p.train_candles) > 0 for p in periods), "All periods should have training data"
        assert all(len(p.test_candles) > 0 for p in periods), "All periods should have test data"
    
    def test_genetic_optimizer_individual_generation(self):
        """Test genetic algorithm individual generation"""
        param_ranges = {
            "rsi_period": (10, 20),
            "rsi_oversold": (20, 35),
            "rsi_overbought": (65, 80)
        }
        
        individual = genetic_optimizer.generate_individual(param_ranges)
        
        assert "rsi_period" in individual
        assert 10 <= individual["rsi_period"] <= 20
        assert 20 <= individual["rsi_oversold"] <= 35


# ==================== INTEGRATION TESTS ====================

class TestIntegration:
    """Integration tests combining multiple components"""
    
    def test_full_trade_workflow(self):
        """Test complete trade calculation workflow"""
        # 1. Calculate position size
        calc = PositionSizeCalculator.calculate(
            account_balance=10000,
            entry_price=50000,
            stop_loss_price=49000,
            risk_percent=1.0,
            leverage=10,
            side="Buy",
            take_profit_price=52000
        )
        
        assert calc.position_size > 0
        assert calc.risk_reward_ratio > 1
        
        # 2. Validate with risk manager
        manager = RiskManager(max_risk_per_trade=1.0)
        size_info = manager.calculate_position_size(
            account_balance=10000,
            entry_price=50000,
            stop_loss_price=49000
        )
        
        # Sizes should be similar
        assert abs(size_info["size"] - calc.position_size) < 0.01
    
    def test_backtest_with_risk_management(self):
        """Test backtest with advanced risk management"""
        # Create fake trades
        trades_pnl = [100, -50, 150, -60, 120, -40, 180, -70, 90, -30] * 5
        
        # Run Monte Carlo
        mc_result = monte_carlo_simulator.run_bootstrap_simulation(
            trades_pnl,
            initial_balance=10000
        )
        
        assert mc_result.probability_profit > 0
        
        # Calculate risk metrics
        trades = [
            TradeResult(
                pnl=pnl,
                pnl_percent=(pnl / 10000) * 100,
                win=pnl > 0,
                holding_bars=10
            )
            for pnl in trades_pnl
        ]
        
        profit_factor = risk_metrics_calculator.profit_factor(trades)
        assert profit_factor > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
