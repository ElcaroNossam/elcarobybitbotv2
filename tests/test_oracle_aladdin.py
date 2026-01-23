"""
Oracle System Tests - Audit Level 100k+
========================================

Comprehensive test suite for Oracle + Aladdin Engine
Based on BlackRock Aladdin's quality standards.
"""

import pytest
import sys
import os
import asyncio
from dataclasses import asdict

# Add project to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestAladdinEngine:
    """Test Aladdin Engine core functionality"""
    
    def test_import(self):
        """Test that Aladdin engine can be imported"""
        from oracle.aladdin_engine import (
            AladdinEngine,
            run_aladdin_analysis,
            RiskFactorCategory,
            AladdinRiskReport,
            MonteCarloResult,
            ESGScore,
            DrawdownAnalysis,
            StressScenario,
            HISTORICAL_STRESS_SCENARIOS
        )
        assert AladdinEngine is not None
        assert run_aladdin_analysis is not None
    
    def test_risk_factors_creation(self):
        """Test that risk factors are created properly"""
        from oracle.aladdin_engine import create_crypto_risk_factors, RiskFactorCategory
        
        factors = create_crypto_risk_factors()
        
        # Should have 100+ factors
        assert len(factors) >= 100
        
        # Check all categories are represented
        categories = set(f.category for f in factors)
        expected = {
            RiskFactorCategory.MARKET,
            RiskFactorCategory.LIQUIDITY,
            RiskFactorCategory.TECHNOLOGY,
            RiskFactorCategory.CONCENTRATION,
            RiskFactorCategory.OPERATIONAL,
            RiskFactorCategory.REGULATORY,
            RiskFactorCategory.MACRO,
            RiskFactorCategory.SENTIMENT,
        }
        assert expected.issubset(categories)
        
        # Each factor should have required fields
        for factor in factors:
            assert factor.id is not None
            assert factor.name is not None
            assert factor.category is not None
            assert 0 <= factor.weight <= 10
    
    def test_stress_scenarios(self):
        """Test historical stress scenarios"""
        from oracle.aladdin_engine import HISTORICAL_STRESS_SCENARIOS
        
        assert len(HISTORICAL_STRESS_SCENARIOS) >= 8
        
        # Check required scenarios
        scenario_names = [s.name for s in HISTORICAL_STRESS_SCENARIOS]
        assert "COVID Crash (March 2020)" in scenario_names
        assert "Terra/Luna Collapse" in scenario_names
        assert "FTX Collapse" in scenario_names
    
    def test_monte_carlo_simulation(self):
        """Test Monte Carlo simulation"""
        from oracle.aladdin_engine import AladdinEngine
        
        engine = AladdinEngine(monte_carlo_simulations=1000)
        result = engine._run_monte_carlo(
            volatility_pct=50,
            expected_return=0.1,
            btc_correlation=0.7
        )
        
        assert result.simulations == 1000
        assert result.var_95 < 0  # VaR should be negative
        assert result.cvar_95 < result.var_95  # CVaR worse than VaR
        assert 0 <= result.probability_of_loss <= 1
    
    def test_esg_scoring(self):
        """Test ESG scoring"""
        from oracle.aladdin_engine import AladdinEngine
        
        engine = AladdinEngine()
        esg = engine._calculate_esg(
            tokenomics={"team_allocation_pct": 5, "community_allocation_pct": 60, "consensus_mechanism": "pos"},
            team={"team_public": True, "governance_type": "dao", "social_followers": 100000},
            security={"audit_count": 3}
        )
        
        assert 0 <= esg.environmental_score <= 100
        assert 0 <= esg.social_score <= 100
        assert 0 <= esg.governance_score <= 100
        assert esg.esg_rating in ["AAA", "AA", "A", "BBB", "BB", "B", "CCC"]
    
    def test_full_analysis(self):
        """Test full Aladdin analysis"""
        from oracle.aladdin_engine import run_aladdin_analysis
        
        report = run_aladdin_analysis(
            tokenomics={
                "name": "Test Token",
                "team_allocation_pct": 10,
                "vesting_period_months": 24,
            },
            market={
                "volatility_30d": 60,
                "volume_24h_usd": 10_000_000,
                "liquidity_score": 70,
            },
            security={
                "audit_count": 2,
                "critical_issues": 0,
                "security_score": 80,
            },
            team={
                "team_public": True,
                "governance_type": "multisig",
            },
            project_type="defi"
        )
        
        assert 0 <= report.composite_risk_score <= 100
        assert report.risk_rating in ["AAA", "AA", "A", "BBB", "BB", "B", "CCC", "CC", "C", "D"]
        assert report.investment_recommendation in ["STRONG_BUY", "BUY", "HOLD", "REDUCE", "AVOID"]
        assert 0 <= report.position_sizing_suggestion <= 10
        assert report.factors_analyzed >= 100
        assert report.simulations_run >= 1000


class TestOracleCore:
    """Test Oracle core functionality"""
    
    def test_import(self):
        """Test Oracle core imports"""
        from oracle.core import (
            Oracle,
            OracleReport,
            RiskMetrics,
            RiskLevel,
            TokenomicsData,
            MarketData,
            SecurityData,
            TeamData
        )
        assert Oracle is not None
        assert OracleReport is not None
    
    def test_risk_metrics_fields(self):
        """Test RiskMetrics has all Aladdin fields"""
        from oracle.core import RiskMetrics
        
        metrics = RiskMetrics()
        
        # Basic scores
        assert hasattr(metrics, "tokenomics_score")
        assert hasattr(metrics, "market_score")
        assert hasattr(metrics, "security_score")
        assert hasattr(metrics, "overall_score")
        
        # Aladdin-specific fields
        assert hasattr(metrics, "var_95")
        assert hasattr(metrics, "var_99")
        assert hasattr(metrics, "cvar_95")
        assert hasattr(metrics, "cvar_99")
        assert hasattr(metrics, "stress_test_results")
        assert hasattr(metrics, "worst_case_scenario")
        assert hasattr(metrics, "esg_score")
        assert hasattr(metrics, "esg_rating")
        assert hasattr(metrics, "risk_rating")
        assert hasattr(metrics, "factors_analyzed")
        assert hasattr(metrics, "simulations_run")
        assert hasattr(metrics, "max_drawdown_pct")
        assert hasattr(metrics, "recovery_probability")
        assert hasattr(metrics, "position_size_pct")
    
    def test_oracle_initialization(self):
        """Test Oracle initialization"""
        from oracle.core import Oracle
        
        oracle = Oracle()
        assert oracle is not None
        assert oracle.cache_dir.exists()


class TestRiskEngine:
    """Test Risk Engine"""
    
    def test_import(self):
        """Test risk engine imports"""
        from oracle.risk_engine import RiskEngine, StressTestResult
        assert RiskEngine is not None
    
    def test_risk_calculation(self):
        """Test risk calculation"""
        from oracle.risk_engine import RiskEngine
        from oracle.core import TokenomicsData, MarketData, SecurityData, TeamData
        
        engine = RiskEngine()
        
        tokenomics = TokenomicsData(
            team_allocation_pct=15,
            community_allocation_pct=30,
            vesting_period_months=24,
        )
        market = MarketData(
            volatility_30d=60,
            liquidity_score=70,
        )
        security = SecurityData(
            audit_count=2,
            security_score=80,
        )
        team = TeamData(
            team_public=True,
            team_score=75,
        )
        
        metrics = engine.calculate(tokenomics, market, security, team)
        
        assert 0 <= metrics.overall_score <= 100
        assert metrics.risk_level is not None
        assert hasattr(metrics, "stress_test_results")


class TestIntegration:
    """Integration tests"""
    
    def test_aladdin_engine_integration(self):
        """Test Aladdin engine is properly integrated in Oracle"""
        from oracle.core import Oracle
        
        oracle = Oracle()
        
        # Check Aladdin engine property exists
        assert hasattr(oracle, 'aladdin_engine')
        
        # Lazy loading - should create engine on access
        engine = oracle.aladdin_engine
        assert engine is not None
        assert engine.simulations == 10000
    
    def test_elc_world_currency_analysis(self):
        """Test ELC token with world currency grade parameters"""
        from oracle.aladdin_engine import run_aladdin_analysis
        
        report = run_aladdin_analysis(
            tokenomics={
                "name": "Lyxen (LYX)",
                "team_allocation_pct": 3,
                "community_allocation_pct": 28,
                "vesting_period_months": 120,
                "cliff_months": 36,
                "consensus_mechanism": "pos",
            },
            market={
                "volatility_30d": 8,
                "volume_24h_usd": 500_000_000,
                "volume_to_mcap_ratio": 0.05,
                "btc_correlation_30d": 0.15,
                "liquidity_score": 95,
            },
            security={
                "audit_count": 5,
                "critical_issues": 0,
                "security_score": 98,
                "contract_verified": True,
            },
            team={
                "team_public": True,
                "governance_type": "dao",
                "social_followers": 2_000_000,
            },
            project_type="infrastructure"
        )
        
        # World currency grade expectations (allow small tolerance for Monte Carlo randomness)
        assert report.composite_risk_score >= 69.5  # Rating A or above (with tolerance)
        assert report.risk_rating in ["AAA", "AA", "A"]
        assert report.esg.esg_rating in ["AAA", "AA", "A"]
        assert report.investment_recommendation in ["STRONG_BUY", "BUY"]
        
        # Low VaR due to low volatility
        assert report.monte_carlo.var_95 >= -0.15  # Less than 15% loss


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v", "--tb=short"])
