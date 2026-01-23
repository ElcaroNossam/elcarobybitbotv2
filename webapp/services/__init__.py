"""
Lyxen WebApp Services
Professional trading services for backtesting, optimization, and paper trading.

Uses lazy imports to avoid circular dependencies.
"""

# Lazy loading to avoid circular imports
def __getattr__(name):
    """Lazy load modules on first access"""
    
    # Backtest Engine V2
    if name in ("ProBacktestEngine", "BacktestConfig", "BacktestMetrics", 
                "MarketReplayEngine", "DataFetcher", "MetricsCalculator", 
                "PositionSizer", "RegimeDetector"):
        from webapp.services import backtest_engine_pro
        return getattr(backtest_engine_pro, name)
    
    # Strategy Optimizer
    if name in ("StrategyOptimizer", "OptimizationResult", "OptimizationConfig"):
        from webapp.services import strategy_optimizer
        return getattr(strategy_optimizer, name)
    
    # AI Strategy Generator
    if name in ("AIStrategyGenerator", "GeneratedStrategy", "ai_strategy_generator"):
        from webapp.services import ai_strategy_generator
        return getattr(ai_strategy_generator, name)
    
    # Signal Scanner
    if name in ("SignalScanner", "Signal", "SignalType", "SignalStrength", 
                "ScannerConfig", "signal_scanner"):
        from webapp.services import signal_scanner
        return getattr(signal_scanner, name)
    
    # Paper Trading
    if name in ("PaperTradingSession", "PaperTradingManager", "PaperOrder", 
                "PaperPosition", "PaperTrade", "SessionMetrics", "paper_trading_manager"):
        from webapp.services import paper_trading
        return getattr(paper_trading, name)
    
    # Indicators
    if name in ("IndicatorCalculator", "Indicators"):
        from webapp.services import indicators
        return getattr(indicators, name)
    
    # Legacy Backtest Engine
    if name in ("RealBacktestEngine",):
        from webapp.services import backtest_engine
        return getattr(backtest_engine, name)
    
    raise AttributeError(f"module 'webapp.services' has no attribute '{name}'")


__all__ = [
    # Backtest Engine V2
    "ProBacktestEngine",
    "BacktestConfig",
    "BacktestMetrics",
    "MarketReplayEngine",
    "DataFetcher",
    "MetricsCalculator",
    "PositionSizer",
    "RegimeDetector",
    
    # Strategy Optimizer
    "StrategyOptimizer",
    "OptimizationResult",
    "OptimizationConfig",
    
    # AI Strategy Generator
    "AIStrategyGenerator",
    "GeneratedStrategy",
    "ai_strategy_generator",
    
    # Signal Scanner
    "SignalScanner",
    "Signal",
    "SignalType",
    "SignalStrength",
    "ScannerConfig",
    "signal_scanner",
    
    # Paper Trading
    "PaperTradingSession",
    "PaperTradingManager",
    "PaperOrder",
    "PaperPosition",
    "PaperTrade",
    "SessionMetrics",
    "paper_trading_manager",
    
    # Indicators
    "IndicatorCalculator",
    
    # Legacy
    "RealBacktestEngine"
]
