"""
Oracle Risk Engine - Comprehensive Risk Assessment
===================================================

Multi-factor risk analysis inspired by BlackRock's Aladdin:
- Monte Carlo simulations
- Value at Risk (VaR) calculations
- Stress testing scenarios
- Correlation analysis
- Liquidity risk modeling
"""

import math
import random
import statistics
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import logging

from oracle.core import (
    TokenomicsData, MarketData, SecurityData, TeamData,
    RiskMetrics, RiskLevel
)

logger = logging.getLogger("oracle.risk")


@dataclass
class StressTestResult:
    """Results from stress testing scenario"""
    scenario_name: str
    price_impact_pct: float
    portfolio_loss_pct: float
    recovery_probability: float
    risk_rating: str


class RiskEngine:
    """
    Advanced Risk Assessment Engine
    
    Calculates comprehensive risk scores using multiple factors
    and generates investment recommendations.
    """
    
    # Default weights for risk calculation
    DEFAULT_WEIGHTS = {
        "tokenomics": 0.25,
        "market": 0.20,
        "security": 0.30,
        "team": 0.15,
        "liquidity": 0.10
    }
    
    # Risk thresholds for classification
    THRESHOLDS = {
        "critical": 20,
        "high": 40,
        "medium": 60,
        "low": 80
    }
    
    # Red flag conditions
    RED_FLAG_CONDITIONS = {
        "team_allocation_high": ("Team allocation > 40%", lambda t, m, s, tm: t.team_allocation_pct > 40),
        "no_vesting": ("No vesting period", lambda t, m, s, tm: t.vesting_period_months < 3),
        "no_audit": ("No security audit", lambda t, m, s, tm: s.audit_count == 0),
        "critical_vulnerabilities": ("Critical vulnerabilities found", lambda t, m, s, tm: s.critical_issues > 0),
        "mint_function": ("Unlimited minting possible", lambda t, m, s, tm: s.has_mint_function and not s.contract_verified),
        "unverified_contract": ("Unverified smart contract", lambda t, m, s, tm: not s.contract_verified and len(s.owner_privileges) > 0),
        "low_liquidity": ("Very low liquidity", lambda t, m, s, tm: m.liquidity_score < 20),
        "anonymous_team": ("Anonymous team with high control", lambda t, m, s, tm: not tm.team_public and t.team_allocation_pct > 20),
        "honeypot_risk": ("Potential honeypot (blacklist + no sell)", lambda t, m, s, tm: s.has_blacklist and s.has_pausable),
        "extreme_volatility": ("Extreme price volatility", lambda t, m, s, tm: m.volatility_30d > 200)
    }
    
    def __init__(self, config: Optional[Dict] = None):
        """Initialize risk engine with configuration"""
        self.config = config or {}
        self.weights = self.config.get("risk", {}).get("weights", self.DEFAULT_WEIGHTS)
        self.thresholds = self.config.get("risk", {}).get("thresholds", self.THRESHOLDS)
    
    def calculate(
        self,
        tokenomics: TokenomicsData,
        market: MarketData,
        security: SecurityData,
        team: TeamData
    ) -> RiskMetrics:
        """
        Calculate comprehensive risk metrics.
        
        Args:
            tokenomics: Tokenomics analysis data
            market: Market data
            security: Security audit data
            team: Team analysis data
        
        Returns:
            RiskMetrics with all scores and recommendations
        """
        metrics = RiskMetrics()
        
        # Calculate individual scores
        metrics.tokenomics_score = self._score_tokenomics(tokenomics)
        metrics.market_score = self._score_market(market)
        metrics.security_score = security.security_score or self._score_security(security)
        metrics.team_score = team.team_score or self._score_team(team)
        metrics.liquidity_score = market.liquidity_score or self._score_liquidity(market)
        
        # Calculate specific risk factors (0-1, lower = safer)
        metrics.rug_pull_risk = self._calculate_rug_pull_risk(tokenomics, security, team) / 100
        metrics.liquidity_risk = (100 - metrics.liquidity_score) / 100
        metrics.smart_contract_risk = (100 - metrics.security_score) / 100
        metrics.centralization_risk = self._calculate_centralization_risk(tokenomics, security, team) / 100
        metrics.regulatory_risk = self._calculate_regulatory_risk(tokenomics, market) / 100
        
        # Calculate weighted overall score
        metrics.overall_score = (
            metrics.tokenomics_score * self.weights["tokenomics"] +
            metrics.market_score * self.weights["market"] +
            metrics.security_score * self.weights["security"] +
            metrics.team_score * self.weights["team"] +
            metrics.liquidity_score * self.weights["liquidity"]
        )
        
        # Determine risk level
        metrics.risk_level = self._classify_risk_level(metrics.overall_score)
        
        # Detect red flags
        metrics.red_flags = self._detect_red_flags(tokenomics, market, security, team)
        
        # Apply red flag penalty
        if metrics.red_flags:
            penalty = len(metrics.red_flags) * 5
            metrics.overall_score = max(0, metrics.overall_score - penalty)
            # Reclassify after penalty
            metrics.risk_level = self._classify_risk_level(metrics.overall_score)
        
        # Generate warnings
        metrics.warnings = self._generate_warnings(tokenomics, market, security, team)
        
        # Stress Testing & VaR
        metrics.stress_test_results = self._run_stress_tests(market)
        metrics.var_95, metrics.cvar_95 = self._calculate_var(market)
        
        # Generate recommendation
        metrics.investment_recommendation = self._generate_recommendation(metrics)
        
        logger.info(f"Risk calculation complete: {metrics.overall_score:.1f}/100 ({metrics.risk_level.value})")
        
        return metrics
    
    def _run_stress_tests(self, market: MarketData) -> Dict[str, float]:
        """Run stress test scenarios"""
        volatility = market.volatility_30d / 100 if market.volatility_30d > 0 else 0.5
        btc_corr = market.btc_correlation_30d if market.btc_correlation_30d else 0.7
        
        scenarios = {
            "Market Crash (-50%)": -0.50 * (1 + btc_corr * 0.5) * (1 + volatility * 0.3),
            "Bear Market (-30%)": -0.30 * (1 + btc_corr * 0.3),
            "Flash Crash (-20%)": -0.20 * (1 + volatility * 0.5),
            "Liquidity Crisis (-40%)": -0.40 * (2 - market.liquidity_score / 100),
            "Black Swan (-70%)": -0.70 * (1 + volatility * 0.2)
        }
        
        return scenarios
    
    def _calculate_var(self, market: MarketData) -> Tuple[float, float]:
        """Calculate Value at Risk and Conditional VaR"""
        volatility = market.volatility_30d / 100 if market.volatility_30d > 0 else 0.5
        
        # VaR 95% = -1.645 * σ (assuming normal distribution)
        var_95 = -1.645 * volatility / (365 ** 0.5) * 30  # 30-day VaR
        
        # CVaR (Expected Shortfall) = VaR * 1.25 approximately for normal
        cvar_95 = var_95 * 1.25
        
        return var_95, cvar_95
    
    def _score_tokenomics(self, t: TokenomicsData) -> float:
        """Score tokenomics (0-100)"""
        score = 50.0  # Base score
        
        # Team allocation (lower is better)
        if t.team_allocation_pct <= 10:
            score += 15
        elif t.team_allocation_pct <= 20:
            score += 10
        elif t.team_allocation_pct <= 30:
            score += 0
        elif t.team_allocation_pct <= 40:
            score -= 10
        else:
            score -= 20
        
        # Community allocation (higher is better)
        if t.community_allocation_pct >= 50:
            score += 15
        elif t.community_allocation_pct >= 30:
            score += 10
        elif t.community_allocation_pct >= 10:
            score += 5
        
        # Vesting period (longer is better)
        if t.vesting_period_months >= 36:
            score += 15
        elif t.vesting_period_months >= 24:
            score += 10
        elif t.vesting_period_months >= 12:
            score += 5
        elif t.vesting_period_months < 6:
            score -= 10
        
        # Cliff period
        if t.cliff_months >= 12:
            score += 5
        elif t.cliff_months >= 6:
            score += 3
        
        # Deflationary mechanisms
        if t.burn_mechanism:
            score += 5
        
        # High inflation is bad
        if t.inflation_rate_annual_pct > 20:
            score -= 15
        elif t.inflation_rate_annual_pct > 10:
            score -= 5
        
        return max(0, min(100, score))
    
    def _score_market(self, m: MarketData) -> float:
        """Score market metrics (0-100)"""
        score = 50.0
        
        # Market cap (higher generally more stable)
        if m.market_cap_usd >= 1_000_000_000:  # $1B+
            score += 20
        elif m.market_cap_usd >= 100_000_000:  # $100M+
            score += 15
        elif m.market_cap_usd >= 10_000_000:   # $10M+
            score += 5
        elif m.market_cap_usd < 1_000_000:     # <$1M
            score -= 10
        
        # Volume to market cap ratio (healthy: 0.05-0.5)
        ratio = m.volume_to_mcap_ratio
        if 0.05 <= ratio <= 0.5:
            score += 10
        elif ratio < 0.01:
            score -= 15  # Very low liquidity
        elif ratio > 1:
            score -= 5   # Possible wash trading
        
        # Volatility (lower is better for investment)
        if m.volatility_30d <= 30:
            score += 10
        elif m.volatility_30d <= 60:
            score += 5
        elif m.volatility_30d > 100:
            score -= 10
        elif m.volatility_30d > 150:
            score -= 20
        
        # Correlation with BTC (moderate is good for diversification)
        if 0.3 <= m.btc_correlation_30d <= 0.7:
            score += 5
        
        return max(0, min(100, score))
    
    def _score_security(self, s: SecurityData) -> float:
        """Score security (0-100)"""
        score = 40.0  # Base (assume some risk by default)
        
        # Contract verification
        if s.contract_verified:
            score += 15
        else:
            score -= 10
        
        # Audits
        if s.audit_count >= 3:
            score += 25
        elif s.audit_count >= 2:
            score += 20
        elif s.audit_count >= 1:
            score += 10
        
        # Known audit firms bonus
        reputable_firms = ["certik", "trail of bits", "openzeppelin", "consensys", "quantstamp", "halborn"]
        for firm in s.audit_firms:
            if firm.lower() in reputable_firms:
                score += 5
        
        # Vulnerabilities penalty
        score -= s.critical_issues * 20
        score -= s.high_issues * 10
        score -= s.medium_issues * 3
        score -= s.low_issues * 1
        
        # Risky functions
        if s.has_mint_function:
            score -= 10
        if s.has_blacklist:
            score -= 5
        if s.has_pausable:
            score -= 3
        if s.has_upgradeable:
            score -= 8  # Proxy patterns can be risky
        
        # Test coverage
        if s.test_coverage_pct >= 80:
            score += 10
        elif s.test_coverage_pct >= 50:
            score += 5
        
        return max(0, min(100, score))
    
    def _score_team(self, t: TeamData) -> float:
        """Score team (0-100)"""
        score = 30.0  # Base (anonymous team gets lower start)
        
        if t.team_public:
            score += 25
        
        if t.team_size >= 10:
            score += 10
        elif t.team_size >= 5:
            score += 5
        
        # Social presence
        if t.twitter_followers >= 100000:
            score += 10
        elif t.twitter_followers >= 10000:
            score += 5
        
        if t.discord_members >= 50000:
            score += 5
        
        # GitHub activity
        if t.github_commits_30d >= 50:
            score += 10
        elif t.github_commits_30d >= 20:
            score += 5
        
        if t.github_contributors >= 10:
            score += 5
        
        # Governance
        if t.governance_type == "dao":
            score += 10
        elif t.governance_type == "multisig":
            score += 5
        
        if t.token_holder_voting:
            score += 5
        
        return max(0, min(100, score))
    
    def _score_liquidity(self, m: MarketData) -> float:
        """Score liquidity (0-100)"""
        score = 50.0
        
        # Volume relative to market cap
        ratio = m.volume_to_mcap_ratio
        if ratio >= 0.2:
            score += 30
        elif ratio >= 0.1:
            score += 20
        elif ratio >= 0.05:
            score += 10
        elif ratio < 0.01:
            score -= 30
        
        # Raw volume
        if m.volume_24h_usd >= 10_000_000:  # $10M+
            score += 15
        elif m.volume_24h_usd >= 1_000_000:  # $1M+
            score += 10
        elif m.volume_24h_usd < 100_000:     # <$100K
            score -= 20
        
        return max(0, min(100, score))
    
    def _calculate_rug_pull_risk(
        self, t: TokenomicsData, s: SecurityData, tm: TeamData
    ) -> float:
        """Calculate rug pull risk (0-100, higher = MORE risky)"""
        risk = 20.0  # Base risk
        
        # High team allocation without vesting
        if t.team_allocation_pct > 30 and t.vesting_period_months < 12:
            risk += 30
        
        # Anonymous team with high control
        if not tm.team_public:
            risk += 20
        
        # No audit
        if s.audit_count == 0:
            risk += 15
        
        # Dangerous functions
        if s.has_mint_function:
            risk += 10
        if s.has_blacklist:
            risk += 10
        if s.has_pausable:
            risk += 5
        
        # Unverified contract
        if not s.contract_verified:
            risk += 10
        
        # New project (low social presence)
        if tm.twitter_followers < 1000:
            risk += 5
        
        return min(100, risk)
    
    def _calculate_centralization_risk(
        self, t: TokenomicsData, s: SecurityData, tm: TeamData
    ) -> float:
        """Calculate centralization risk (0-100)"""
        risk = 20.0
        
        # Team allocation
        risk += t.team_allocation_pct * 0.5
        
        # Owner privileges
        risk += len(s.owner_privileges) * 5
        
        # Governance type
        if tm.governance_type == "centralized":
            risk += 25
        elif tm.governance_type != "dao":
            risk += 10
        
        # No token holder voting
        if not tm.token_holder_voting:
            risk += 10
        
        return min(100, risk)
    
    def _calculate_regulatory_risk(self, t: TokenomicsData, m: MarketData) -> float:
        """Calculate regulatory risk (0-100)"""
        risk = 30.0  # Base regulatory risk for crypto
        
        # Securities-like characteristics
        if t.investor_allocation_pct > 30:
            risk += 15
        
        # Large market cap attracts more scrutiny
        if m.market_cap_usd > 1_000_000_000:
            risk += 10
        
        return min(100, risk)
    
    def _classify_risk_level(self, score: float) -> RiskLevel:
        """Classify overall score into risk level"""
        if score < self.thresholds["critical"]:
            return RiskLevel.CRITICAL
        elif score < self.thresholds["high"]:
            return RiskLevel.HIGH
        elif score < self.thresholds["medium"]:
            return RiskLevel.MEDIUM
        elif score < self.thresholds["low"]:
            return RiskLevel.LOW
        else:
            return RiskLevel.MINIMAL
    
    def _detect_red_flags(
        self, t: TokenomicsData, m: MarketData, s: SecurityData, tm: TeamData
    ) -> List[str]:
        """Detect critical red flags"""
        red_flags = []
        
        for flag_id, (description, condition) in self.RED_FLAG_CONDITIONS.items():
            try:
                if condition(t, m, s, tm):
                    red_flags.append(description)
            except Exception:
                pass  # Skip if data missing
        
        return red_flags
    
    def _generate_warnings(
        self, t: TokenomicsData, m: MarketData, s: SecurityData, tm: TeamData
    ) -> List[str]:
        """Generate warning messages"""
        warnings = []
        
        if t.team_allocation_pct > 20:
            warnings.append(f"Team holds {t.team_allocation_pct:.1f}% of supply")
        
        if t.vesting_period_months < 12:
            warnings.append(f"Short vesting: {t.vesting_period_months} months")
        
        if m.volatility_30d > 80:
            warnings.append(f"High volatility: {m.volatility_30d:.1f}% (30d)")
        
        if s.high_issues > 0:
            warnings.append(f"{s.high_issues} high-severity issues in audit")
        
        if not tm.team_public:
            warnings.append("Team identity not publicly verified")
        
        return warnings
    
    def _generate_recommendation(self, metrics: RiskMetrics) -> str:
        """Generate investment recommendation"""
        score = metrics.overall_score
        red_flags = len(metrics.red_flags)
        
        if red_flags >= 3 or score < 20:
            return "avoid"
        elif red_flags >= 2 or score < 40:
            return "sell"
        elif score < 60:
            return "hold"
        elif score < 80:
            return "buy"
        else:
            return "strong_buy"
    
    def stress_test(
        self,
        market: MarketData,
        scenarios: Optional[List[Dict]] = None
    ) -> List[StressTestResult]:
        """
        Run stress test scenarios.
        
        Simulates market conditions and calculates potential losses.
        """
        if scenarios is None:
            scenarios = [
                {"name": "Market Crash (-50%)", "price_drop": 0.50, "volume_drop": 0.70},
                {"name": "Bear Market (-30%)", "price_drop": 0.30, "volume_drop": 0.40},
                {"name": "Flash Crash (-20%)", "price_drop": 0.20, "volume_drop": 0.50},
                {"name": "Liquidity Crisis", "price_drop": 0.40, "volume_drop": 0.90},
                {"name": "Black Swan (-70%)", "price_drop": 0.70, "volume_drop": 0.80}
            ]
        
        results = []
        for scenario in scenarios:
            price_impact = scenario["price_drop"] * 100
            volume_impact = scenario["volume_drop"]
            
            # Estimate slippage based on volume impact
            slippage = min(50, volume_impact * 30)  # Up to 50% slippage
            
            total_loss = price_impact + slippage
            
            # Recovery probability (based on volatility and liquidity)
            recovery_prob = max(0.1, min(0.9, 
                (market.liquidity_score / 100) * (1 - scenario["price_drop"])
            ))
            
            # Risk rating
            if total_loss > 80:
                rating = "SEVERE"
            elif total_loss > 50:
                rating = "HIGH"
            elif total_loss > 30:
                rating = "MODERATE"
            else:
                rating = "LOW"
            
            results.append(StressTestResult(
                scenario_name=scenario["name"],
                price_impact_pct=price_impact,
                portfolio_loss_pct=total_loss,
                recovery_probability=recovery_prob,
                risk_rating=rating
            ))
        
        return results
    
    def monte_carlo_var(
        self,
        current_price: float,
        volatility: float,
        days: int = 30,
        simulations: int = 10000,
        confidence: float = 0.95
    ) -> Dict[str, float]:
        """
        Calculate Value at Risk using Monte Carlo simulation.
        
        Args:
            current_price: Current asset price
            volatility: Annual volatility (as percentage, e.g., 80 for 80%)
            days: Holding period in days
            simulations: Number of Monte Carlo simulations
            confidence: Confidence level (e.g., 0.95 for 95%)
        
        Returns:
            Dict with VaR metrics
        """
        # Convert annual volatility to daily
        daily_vol = (volatility / 100) / math.sqrt(252)
        
        # Generate random returns
        random.seed(42)  # For reproducibility
        final_prices = []
        
        for _ in range(simulations):
            price = current_price
            for _ in range(days):
                # Geometric Brownian Motion
                daily_return = random.gauss(0, daily_vol)
                price *= (1 + daily_return)
            final_prices.append(price)
        
        # Calculate returns
        returns = [(p - current_price) / current_price for p in final_prices]
        returns.sort()
        
        # VaR at confidence level
        var_index = int((1 - confidence) * simulations)
        var_return = returns[var_index]
        var_amount = abs(var_return * current_price)
        
        # Expected Shortfall (CVaR) - average of losses beyond VaR
        cvar_returns = returns[:var_index]
        cvar_return = statistics.mean(cvar_returns) if cvar_returns else var_return
        cvar_amount = abs(cvar_return * current_price)
        
        # Statistics
        mean_return = statistics.mean(returns)
        std_return = statistics.stdev(returns)
        
        return {
            "var_pct": abs(var_return) * 100,
            "var_amount": var_amount,
            "cvar_pct": abs(cvar_return) * 100,
            "cvar_amount": cvar_amount,
            "expected_return_pct": mean_return * 100,
            "return_std_pct": std_return * 100,
            "simulations": simulations,
            "confidence": confidence,
            "holding_period_days": days
        }
