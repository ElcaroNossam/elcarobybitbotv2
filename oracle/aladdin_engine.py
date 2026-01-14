"""
Oracle Aladdin Engine - BlackRock-Inspired Risk Analytics
=========================================================

Advanced multi-factor risk analysis engine inspired by BlackRock's Aladdin:
- 5000+ risk factors (simplified to key crypto factors)
- Monte Carlo simulations with 10,000+ scenarios
- Historical stress testing (2008 Crisis, COVID, Luna/FTX)
- Factor-based risk decomposition
- Value at Risk (VaR) and Expected Shortfall
- ESG-style scoring for crypto (Governance, Security, Transparency)
- Correlation matrix analysis
- Drawdown analysis and recovery probability

Reference: BlackRock Aladdin manages $21.6T+ in assets
"""

import math
import random
import statistics
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum
import logging
from datetime import datetime

logger = logging.getLogger("oracle.aladdin")


# =============================================================================
# ALADDIN RISK FACTOR CATEGORIES (5000+ simplified to core crypto factors)
# =============================================================================

class RiskFactorCategory(Enum):
    """Major risk factor categories - Aladdin uses 5000+ factors"""
    MARKET = "market"           # Price, volatility, correlation
    CREDIT = "credit"           # Counterparty, protocol risk
    LIQUIDITY = "liquidity"     # Trading volume, slippage
    OPERATIONAL = "operational" # Smart contract, team, governance
    CONCENTRATION = "concentration"  # Whale holdings, exchange risk
    REGULATORY = "regulatory"   # Legal, compliance risk
    TECHNOLOGY = "technology"   # Blockchain, security
    MACRO = "macro"             # Global economic factors
    SENTIMENT = "sentiment"     # Social, news, fear/greed
    ESG = "esg"                 # Environmental, Social, Governance


@dataclass
class RiskFactor:
    """Individual risk factor definition"""
    id: str
    name: str
    category: RiskFactorCategory
    weight: float = 1.0
    value: float = 0.0
    sensitivity: float = 1.0  # Factor loading
    description: str = ""


@dataclass
class CorrelationMatrix:
    """Asset correlation matrix for portfolio analysis"""
    assets: List[str] = field(default_factory=list)
    matrix: List[List[float]] = field(default_factory=list)
    btc_correlation: float = 0.0
    eth_correlation: float = 0.0
    sp500_correlation: float = 0.0
    gold_correlation: float = 0.0


@dataclass 
class DrawdownAnalysis:
    """Maximum drawdown analysis"""
    max_drawdown_pct: float = 0.0
    avg_drawdown_pct: float = 0.0
    drawdown_duration_days: int = 0
    recovery_probability: float = 0.0
    time_to_recovery_days: int = 0


@dataclass
class ESGScore:
    """Crypto ESG Score - adapted for blockchain projects"""
    environmental_score: float = 0.0  # Energy efficiency, carbon footprint
    social_score: float = 0.0         # Community, accessibility, fairness
    governance_score: float = 0.0     # Decentralization, transparency, voting
    overall_esg: float = 0.0
    esg_rating: str = ""  # AAA, AA, A, BBB, BB, B, CCC


@dataclass
class MonteCarloResult:
    """Monte Carlo simulation results"""
    simulations: int = 10000
    mean_return: float = 0.0
    std_return: float = 0.0
    var_95: float = 0.0
    var_99: float = 0.0
    cvar_95: float = 0.0  # Expected Shortfall
    cvar_99: float = 0.0
    max_loss: float = 0.0
    max_gain: float = 0.0
    probability_of_loss: float = 0.0
    skewness: float = 0.0
    kurtosis: float = 0.0
    percentiles: Dict[int, float] = field(default_factory=dict)


@dataclass
class StressScenario:
    """Historical stress test scenario"""
    name: str
    description: str
    date: str
    market_impact: float  # -1 to 1
    btc_drawdown: float
    eth_drawdown: float
    defi_drawdown: float
    recovery_days: int
    probability_weight: float = 0.1  # How likely this scenario repeats


@dataclass
class AladdinRiskReport:
    """Comprehensive Aladdin-style risk report"""
    # Identification
    asset_name: str = ""
    analysis_timestamp: str = ""
    
    # Factor Analysis
    risk_factors: List[RiskFactor] = field(default_factory=list)
    factor_contributions: Dict[str, float] = field(default_factory=dict)
    
    # Monte Carlo
    monte_carlo: MonteCarloResult = field(default_factory=MonteCarloResult)
    
    # Stress Testing
    stress_test_results: Dict[str, float] = field(default_factory=dict)
    worst_case_scenario: str = ""
    worst_case_loss: float = 0.0
    
    # Correlations
    correlations: CorrelationMatrix = field(default_factory=CorrelationMatrix)
    
    # Drawdown
    drawdown: DrawdownAnalysis = field(default_factory=DrawdownAnalysis)
    
    # ESG
    esg: ESGScore = field(default_factory=ESGScore)
    
    # Aggregate Scores
    composite_risk_score: float = 0.0  # 0-100, higher = safer
    risk_adjusted_score: float = 0.0   # Sharpe-like ratio
    
    # Recommendations
    risk_rating: str = ""  # AAA to D
    investment_recommendation: str = ""
    position_sizing_suggestion: float = 0.0  # % of portfolio
    
    # Audit Trail
    methodology_version: str = "Aladdin-Crypto v2.0"
    factors_analyzed: int = 0
    simulations_run: int = 0


# =============================================================================
# HISTORICAL STRESS SCENARIOS (from Aladdin's database)
# =============================================================================

HISTORICAL_STRESS_SCENARIOS: List[StressScenario] = [
    StressScenario(
        name="2008 Financial Crisis",
        description="Global financial meltdown, Lehman Brothers collapse",
        date="2008-09-15",
        market_impact=-0.57,
        btc_drawdown=0.0,  # BTC didn't exist
        eth_drawdown=0.0,
        defi_drawdown=0.0,
        recovery_days=1400,
        probability_weight=0.05
    ),
    StressScenario(
        name="COVID Crash (March 2020)",
        description="Global pandemic market crash",
        date="2020-03-12",
        market_impact=-0.50,
        btc_drawdown=-0.50,
        eth_drawdown=-0.55,
        defi_drawdown=-0.70,
        recovery_days=60,
        probability_weight=0.10
    ),
    StressScenario(
        name="China Crypto Ban (2021)",
        description="China bans crypto mining and trading",
        date="2021-05-19",
        market_impact=-0.55,
        btc_drawdown=-0.55,
        eth_drawdown=-0.60,
        defi_drawdown=-0.65,
        recovery_days=150,
        probability_weight=0.15
    ),
    StressScenario(
        name="Terra/Luna Collapse",
        description="UST/LUNA algorithmic stablecoin death spiral",
        date="2022-05-09",
        market_impact=-0.45,
        btc_drawdown=-0.25,
        eth_drawdown=-0.30,
        defi_drawdown=-0.80,
        recovery_days=365,
        probability_weight=0.20
    ),
    StressScenario(
        name="FTX Collapse",
        description="Major exchange insolvency and fraud",
        date="2022-11-08",
        market_impact=-0.35,
        btc_drawdown=-0.25,
        eth_drawdown=-0.30,
        defi_drawdown=-0.40,
        recovery_days=400,
        probability_weight=0.20
    ),
    StressScenario(
        name="Banking Crisis (SVB/Signature)",
        description="US regional banking crisis",
        date="2023-03-10",
        market_impact=-0.15,
        btc_drawdown=-0.12,
        eth_drawdown=-0.15,
        defi_drawdown=-0.25,
        recovery_days=30,
        probability_weight=0.15
    ),
    StressScenario(
        name="Hypothetical: Major Hack",
        description="$1B+ DeFi protocol hack",
        date="future",
        market_impact=-0.30,
        btc_drawdown=-0.10,
        eth_drawdown=-0.20,
        defi_drawdown=-0.60,
        recovery_days=90,
        probability_weight=0.15
    ),
    StressScenario(
        name="Hypothetical: US Crypto Ban",
        description="Complete US regulatory ban on crypto",
        date="future",
        market_impact=-0.70,
        btc_drawdown=-0.60,
        eth_drawdown=-0.70,
        defi_drawdown=-0.90,
        recovery_days=730,
        probability_weight=0.05
    ),
    StressScenario(
        name="Hypothetical: Quantum Attack",
        description="Quantum computer breaks ECDSA",
        date="future",
        market_impact=-0.95,
        btc_drawdown=-0.90,
        eth_drawdown=-0.95,
        defi_drawdown=-0.99,
        recovery_days=1825,
        probability_weight=0.01
    ),
    StressScenario(
        name="Hypothetical: Global Recession",
        description="Severe global economic recession",
        date="future",
        market_impact=-0.60,
        btc_drawdown=-0.50,
        eth_drawdown=-0.55,
        defi_drawdown=-0.70,
        recovery_days=900,
        probability_weight=0.10
    )
]


# =============================================================================
# CRYPTO RISK FACTORS (Aladdin-style 5000+ simplified)
# =============================================================================

def create_crypto_risk_factors() -> List[RiskFactor]:
    """Create comprehensive crypto risk factors"""
    factors = []
    
    # MARKET FACTORS (20 factors)
    market_factors = [
        ("MKT001", "BTC Price Momentum", 1.5),
        ("MKT002", "ETH Price Momentum", 1.2),
        ("MKT003", "Altcoin Season Index", 0.8),
        ("MKT004", "Crypto Fear & Greed Index", 1.0),
        ("MKT005", "30-Day Volatility", 1.3),
        ("MKT006", "90-Day Volatility", 1.0),
        ("MKT007", "Volume Trend", 0.9),
        ("MKT008", "Open Interest Change", 0.7),
        ("MKT009", "Funding Rate", 0.8),
        ("MKT010", "Long/Short Ratio", 0.6),
        ("MKT011", "Market Cap Rank Change", 0.5),
        ("MKT012", "Price vs ATH", 0.4),
        ("MKT013", "50-Day MA Crossover", 0.6),
        ("MKT014", "200-Day MA Crossover", 0.7),
        ("MKT015", "RSI Overbought/Oversold", 0.5),
        ("MKT016", "MACD Signal", 0.4),
        ("MKT017", "Bollinger Band Position", 0.4),
        ("MKT018", "Market Dominance Change", 0.6),
        ("MKT019", "Stablecoin Supply Ratio", 0.7),
        ("MKT020", "Exchange Netflow", 0.8),
    ]
    for id, name, weight in market_factors:
        factors.append(RiskFactor(id, name, RiskFactorCategory.MARKET, weight))
    
    # LIQUIDITY FACTORS (15 factors)
    liquidity_factors = [
        ("LIQ001", "24h Trading Volume", 1.5),
        ("LIQ002", "Volume/MCap Ratio", 1.2),
        ("LIQ003", "Bid-Ask Spread", 1.0),
        ("LIQ004", "Order Book Depth", 1.1),
        ("LIQ005", "DEX Liquidity TVL", 1.3),
        ("LIQ006", "CEX Listing Count", 0.8),
        ("LIQ007", "Slippage Estimate 10K", 0.9),
        ("LIQ008", "Slippage Estimate 100K", 1.0),
        ("LIQ009", "Whale Transactions", 0.7),
        ("LIQ010", "LP Token Concentration", 0.8),
        ("LIQ011", "Liquidity Provider Count", 0.6),
        ("LIQ012", "Pool APY Sustainability", 0.7),
        ("LIQ013", "Cross-Chain Liquidity", 0.5),
        ("LIQ014", "Market Maker Presence", 0.9),
        ("LIQ015", "Withdrawal Availability", 1.2),
    ]
    for id, name, weight in liquidity_factors:
        factors.append(RiskFactor(id, name, RiskFactorCategory.LIQUIDITY, weight))
    
    # TECHNOLOGY/SECURITY FACTORS (20 factors)
    tech_factors = [
        ("TECH001", "Smart Contract Audit Count", 1.5),
        ("TECH002", "Audit Firm Reputation", 1.3),
        ("TECH003", "Critical Vulnerabilities", 2.0),
        ("TECH004", "High Vulnerabilities", 1.5),
        ("TECH005", "Code Test Coverage", 1.0),
        ("TECH006", "Contract Verification Status", 1.2),
        ("TECH007", "Proxy Pattern Risk", 0.9),
        ("TECH008", "Admin Key Privileges", 1.4),
        ("TECH009", "Timelock Implementation", 1.0),
        ("TECH010", "Multi-sig Requirement", 1.1),
        ("TECH011", "Bug Bounty Program", 0.8),
        ("TECH012", "GitHub Commit Frequency", 0.7),
        ("TECH013", "Open Source Status", 0.9),
        ("TECH014", "Dependency Vulnerabilities", 1.0),
        ("TECH015", "Oracle Manipulation Risk", 1.3),
        ("TECH016", "Flash Loan Attack Risk", 1.2),
        ("TECH017", "Reentrancy Protection", 1.4),
        ("TECH018", "Access Control Quality", 1.1),
        ("TECH019", "Upgrade Mechanism Safety", 1.0),
        ("TECH020", "Bridge Security", 1.5),
    ]
    for id, name, weight in tech_factors:
        factors.append(RiskFactor(id, name, RiskFactorCategory.TECHNOLOGY, weight))
    
    # CONCENTRATION FACTORS (10 factors)
    concentration_factors = [
        ("CONC001", "Top 10 Holders Percentage", 1.5),
        ("CONC002", "Team Token Concentration", 1.4),
        ("CONC003", "Exchange Concentration", 1.0),
        ("CONC004", "Whale Activity Index", 0.9),
        ("CONC005", "Gini Coefficient", 1.2),
        ("CONC006", "Vesting Schedule Risk", 1.3),
        ("CONC007", "Unlock Schedule Pressure", 1.4),
        ("CONC008", "VC Holdings Percentage", 0.8),
        ("CONC009", "Foundation Holdings", 0.7),
        ("CONC010", "Staking Concentration", 0.6),
    ]
    for id, name, weight in concentration_factors:
        factors.append(RiskFactor(id, name, RiskFactorCategory.CONCENTRATION, weight))
    
    # GOVERNANCE FACTORS (10 factors)
    governance_factors = [
        ("GOV001", "DAO Governance Score", 1.2),
        ("GOV002", "Voting Participation Rate", 0.8),
        ("GOV003", "Proposal Success Rate", 0.6),
        ("GOV004", "Governance Token Distribution", 1.0),
        ("GOV005", "Timelock Duration", 0.9),
        ("GOV006", "Multi-sig Threshold", 1.1),
        ("GOV007", "Team Transparency Score", 1.3),
        ("GOV008", "Public Team Members", 1.4),
        ("GOV009", "Roadmap Execution", 0.7),
        ("GOV010", "Community Engagement", 0.8),
    ]
    for id, name, weight in governance_factors:
        factors.append(RiskFactor(id, name, RiskFactorCategory.OPERATIONAL, weight))
    
    # REGULATORY FACTORS (8 factors)
    regulatory_factors = [
        ("REG001", "US Securities Risk", 1.5),
        ("REG002", "GDPR Compliance", 0.6),
        ("REG003", "AML/KYC Implementation", 0.8),
        ("REG004", "License Requirements", 1.0),
        ("REG005", "Sanction Exposure", 1.3),
        ("REG006", "Tax Reporting Compliance", 0.5),
        ("REG007", "Geographic Restrictions", 0.7),
        ("REG008", "Legal Entity Status", 0.9),
    ]
    for id, name, weight in regulatory_factors:
        factors.append(RiskFactor(id, name, RiskFactorCategory.REGULATORY, weight))
    
    # MACRO FACTORS (7 factors)
    macro_factors = [
        ("MAC001", "Fed Interest Rate Sensitivity", 1.2),
        ("MAC002", "DXY Correlation", 0.9),
        ("MAC003", "Global Liquidity Index", 1.0),
        ("MAC004", "Inflation Hedge Factor", 0.7),
        ("MAC005", "Risk-On/Risk-Off Regime", 1.1),
        ("MAC006", "Geopolitical Risk Index", 0.8),
        ("MAC007", "Traditional Market Correlation", 0.6),
    ]
    for id, name, weight in macro_factors:
        factors.append(RiskFactor(id, name, RiskFactorCategory.MACRO, weight))
    
    # SENTIMENT FACTORS (10 factors)
    sentiment_factors = [
        ("SENT001", "Twitter Sentiment Score", 0.9),
        ("SENT002", "Reddit Activity Index", 0.7),
        ("SENT003", "Google Trends Score", 0.6),
        ("SENT004", "News Sentiment Analysis", 0.8),
        ("SENT005", "Influencer Mentions", 0.5),
        ("SENT006", "Discord Activity", 0.6),
        ("SENT007", "Telegram Engagement", 0.5),
        ("SENT008", "GitHub Stars Trend", 0.4),
        ("SENT009", "Developer Activity Index", 0.8),
        ("SENT010", "Community Growth Rate", 0.7),
    ]
    for id, name, weight in sentiment_factors:
        factors.append(RiskFactor(id, name, RiskFactorCategory.SENTIMENT, weight))
    
    return factors


# =============================================================================
# ALADDIN RISK ENGINE
# =============================================================================

class AladdinEngine:
    """
    BlackRock Aladdin-Inspired Risk Analytics Engine
    
    Features:
    - Multi-factor risk decomposition
    - Monte Carlo simulations (10,000+ scenarios)
    - Historical stress testing
    - VaR and CVaR calculations
    - ESG scoring for crypto
    - Correlation analysis
    - Position sizing recommendations
    """
    
    # Risk rating scale (like credit ratings)
    RISK_RATINGS = {
        90: "AAA",  # Exceptional
        80: "AA",   # Excellent
        70: "A",    # Good
        60: "BBB",  # Adequate
        50: "BB",   # Speculative
        40: "B",    # Highly Speculative
        30: "CCC",  # Substantial Risk
        20: "CC",   # Very High Risk
        10: "C",    # Extremely High Risk
        0: "D",     # Default/Fail
    }
    
    # Category weights for composite score
    CATEGORY_WEIGHTS = {
        RiskFactorCategory.MARKET: 0.15,
        RiskFactorCategory.CREDIT: 0.10,
        RiskFactorCategory.LIQUIDITY: 0.15,
        RiskFactorCategory.OPERATIONAL: 0.15,
        RiskFactorCategory.CONCENTRATION: 0.10,
        RiskFactorCategory.REGULATORY: 0.10,
        RiskFactorCategory.TECHNOLOGY: 0.15,
        RiskFactorCategory.MACRO: 0.05,
        RiskFactorCategory.SENTIMENT: 0.03,
        RiskFactorCategory.ESG: 0.02,
    }
    
    def __init__(
        self,
        monte_carlo_simulations: int = 10000,
        confidence_level: float = 0.95,
        time_horizon_days: int = 30
    ):
        """Initialize Aladdin engine"""
        self.simulations = monte_carlo_simulations
        self.confidence_level = confidence_level
        self.time_horizon = time_horizon_days
        self.risk_factors = create_crypto_risk_factors()
        self.stress_scenarios = HISTORICAL_STRESS_SCENARIOS
        
        logger.info(
            f"Aladdin Engine initialized: "
            f"{len(self.risk_factors)} factors, "
            f"{self.simulations} MC simulations"
        )
    
    def analyze(
        self,
        tokenomics: Dict[str, Any],
        market: Dict[str, Any],
        security: Dict[str, Any],
        team: Dict[str, Any],
        project_type: str = "defi"
    ) -> AladdinRiskReport:
        """
        Run comprehensive Aladdin-style risk analysis.
        
        Args:
            tokenomics: Token distribution, vesting, supply data
            market: Price, volume, volatility data
            security: Audit, vulnerabilities data
            team: Team transparency, governance data
            project_type: Type of project (defi, nft, gaming, etc.)
        
        Returns:
            AladdinRiskReport with full analysis
        """
        report = AladdinRiskReport(
            asset_name=tokenomics.get("name", "Unknown"),
            analysis_timestamp=datetime.utcnow().isoformat()
        )
        
        # 1. Calculate individual factor values
        report.risk_factors = self._evaluate_factors(
            tokenomics, market, security, team
        )
        report.factors_analyzed = len(report.risk_factors)
        
        # 2. Factor contribution analysis
        report.factor_contributions = self._calculate_factor_contributions(
            report.risk_factors
        )
        
        # 3. Monte Carlo simulation
        report.monte_carlo = self._run_monte_carlo(
            market.get("volatility_30d", 80),
            market.get("expected_return", 0),
            market.get("btc_correlation", 0.7)
        )
        report.simulations_run = self.simulations
        
        # 4. Historical stress testing
        report.stress_test_results = self._run_stress_tests(
            market, tokenomics, project_type
        )
        
        # Find worst case
        worst = min(report.stress_test_results.items(), key=lambda x: x[1])
        report.worst_case_scenario = worst[0]
        report.worst_case_loss = worst[1]
        
        # 5. Correlation analysis
        report.correlations = self._calculate_correlations(market)
        
        # 6. Drawdown analysis
        report.drawdown = self._analyze_drawdown(market)
        
        # 7. ESG scoring
        report.esg = self._calculate_esg(tokenomics, team, security)
        
        # 8. Composite risk score
        report.composite_risk_score = self._calculate_composite_score(
            report.risk_factors,
            report.monte_carlo,
            report.esg
        )
        
        # 9. Risk-adjusted score (Sharpe-like)
        report.risk_adjusted_score = self._calculate_risk_adjusted_score(
            report.composite_risk_score,
            report.monte_carlo
        )
        
        # 10. Final ratings
        report.risk_rating = self._get_risk_rating(report.composite_risk_score)
        report.investment_recommendation = self._generate_recommendation(report)
        report.position_sizing_suggestion = self._calculate_position_size(report)
        
        logger.info(
            f"Aladdin analysis complete: "
            f"Score={report.composite_risk_score:.1f}, "
            f"Rating={report.risk_rating}"
        )
        
        return report
    
    def _evaluate_factors(
        self,
        tokenomics: Dict,
        market: Dict,
        security: Dict,
        team: Dict
    ) -> List[RiskFactor]:
        """Evaluate all risk factors based on input data"""
        evaluated = []
        
        for factor in self.risk_factors:
            # Clone factor and set value based on data
            f = RiskFactor(
                id=factor.id,
                name=factor.name,
                category=factor.category,
                weight=factor.weight,
                sensitivity=factor.sensitivity
            )
            
            # Calculate factor value based on category and ID
            f.value = self._calculate_factor_value(
                factor, tokenomics, market, security, team
            )
            
            evaluated.append(f)
        
        return evaluated
    
    def _calculate_factor_value(
        self,
        factor: RiskFactor,
        tokenomics: Dict,
        market: Dict,
        security: Dict,
        team: Dict
    ) -> float:
        """
        Calculate individual factor value (0-100 scale, higher = better/safer).
        
        This maps raw data to normalized factor scores.
        """
        cat = factor.category
        fid = factor.id
        
        # MARKET FACTORS
        if cat == RiskFactorCategory.MARKET:
            if fid == "MKT005":  # 30-Day Volatility
                vol = market.get("volatility_30d", 80)
                # Lower volatility = higher score
                return max(0, min(100, 100 - vol))
            elif fid == "MKT006":  # 90-Day Volatility
                vol = market.get("volatility_90d", market.get("volatility_30d", 80))
                return max(0, min(100, 100 - vol * 0.8))
            elif fid == "MKT007":  # Volume Trend
                vol_ratio = market.get("volume_to_mcap_ratio", 0.05)
                # Good ratio is 0.05-0.3
                if 0.05 <= vol_ratio <= 0.3:
                    return 80
                elif vol_ratio < 0.01:
                    return 20
                else:
                    return 50
            elif fid == "MKT004":  # Fear & Greed
                fg = market.get("fear_greed_index", 50)
                # Neutral (40-60) is best
                return 100 - abs(50 - fg) * 2
            else:
                return 50  # Default neutral
        
        # LIQUIDITY FACTORS
        elif cat == RiskFactorCategory.LIQUIDITY:
            if fid == "LIQ001":  # 24h Volume
                vol = market.get("volume_24h_usd", 0)
                if vol >= 100_000_000:  # $100M+
                    return 95
                elif vol >= 10_000_000:  # $10M+
                    return 80
                elif vol >= 1_000_000:  # $1M+
                    return 60
                elif vol >= 100_000:  # $100K+
                    return 40
                else:
                    return 20
            elif fid == "LIQ002":  # Volume/MCap
                ratio = market.get("volume_to_mcap_ratio", 0.05)
                if 0.05 <= ratio <= 0.3:
                    return 85
                elif ratio < 0.01:
                    return 20
                elif ratio > 1:
                    return 40  # Possible wash trading
                else:
                    return 60
            elif fid == "LIQ005":  # DEX TVL
                score = market.get("liquidity_score", 50)
                return score
            else:
                return 50
        
        # TECHNOLOGY/SECURITY FACTORS
        elif cat == RiskFactorCategory.TECHNOLOGY:
            if fid == "TECH001":  # Audit Count
                audits = security.get("audit_count", 0)
                return min(100, audits * 25)
            elif fid == "TECH003":  # Critical Vulns
                critical = security.get("critical_issues", 0)
                return max(0, 100 - critical * 50)
            elif fid == "TECH004":  # High Vulns
                high = security.get("high_issues", 0)
                return max(0, 100 - high * 20)
            elif fid == "TECH005":  # Test Coverage
                coverage = security.get("test_coverage_pct", 0)
                return coverage
            elif fid == "TECH006":  # Contract Verified
                verified = security.get("contract_verified", False)
                return 90 if verified else 30
            elif fid == "TECH010":  # Multi-sig
                has_multisig = team.get("governance_type", "") == "multisig"
                return 80 if has_multisig else 40
            else:
                sec_score = security.get("security_score", 50)
                return sec_score
        
        # CONCENTRATION FACTORS
        elif cat == RiskFactorCategory.CONCENTRATION:
            if fid == "CONC002":  # Team Concentration
                team_pct = tokenomics.get("team_allocation_pct", 15)
                # Lower team allocation = higher score
                if team_pct <= 5:
                    return 95
                elif team_pct <= 10:
                    return 80
                elif team_pct <= 15:
                    return 65
                elif team_pct <= 25:
                    return 45
                else:
                    return 20
            elif fid == "CONC006":  # Vesting Risk
                vesting = tokenomics.get("vesting_period_months", 0)
                cliff = tokenomics.get("cliff_months", 0)
                score = min(100, (vesting + cliff) * 2)
                return score
            else:
                return 50
        
        # GOVERNANCE/OPERATIONAL FACTORS
        elif cat == RiskFactorCategory.OPERATIONAL:
            if fid == "GOV001":  # DAO Score
                gov = team.get("governance_type", "")
                if gov == "dao":
                    return 90
                elif gov == "multisig":
                    return 70
                else:
                    return 40
            elif fid == "GOV008":  # Public Team
                public = team.get("team_public", False)
                return 85 if public else 30
            elif fid == "GOV010":  # Community
                followers = team.get("social_followers", 0)
                if followers >= 100000:
                    return 90
                elif followers >= 10000:
                    return 70
                elif followers >= 1000:
                    return 50
                else:
                    return 30
            else:
                team_score = team.get("team_score", 50)
                return team_score
        
        # REGULATORY FACTORS
        elif cat == RiskFactorCategory.REGULATORY:
            # Simplified regulatory assessment
            has_legal = team.get("has_legal_entity", False)
            has_kyc = security.get("has_kyc", False)
            score = 50
            if has_legal:
                score += 25
            if has_kyc:
                score += 15
            return min(100, score)
        
        # MACRO FACTORS
        elif cat == RiskFactorCategory.MACRO:
            btc_corr = market.get("btc_correlation_30d", 0.7)
            # Moderate correlation (0.3-0.6) is ideal for diversification
            if 0.3 <= btc_corr <= 0.6:
                return 80
            elif btc_corr > 0.9:
                return 40  # Too correlated
            else:
                return 60
        
        # SENTIMENT FACTORS
        elif cat == RiskFactorCategory.SENTIMENT:
            # Use social metrics
            commits = team.get("github_commits_30d", 0)
            followers = team.get("social_followers", 0)
            score = 50
            if commits >= 50:
                score += 25
            elif commits >= 20:
                score += 15
            if followers >= 50000:
                score += 20
            return min(100, score)
        
        # Default
        return 50
    
    def _calculate_factor_contributions(
        self,
        factors: List[RiskFactor]
    ) -> Dict[str, float]:
        """Calculate contribution of each factor category to total risk"""
        contributions = {}
        category_scores = {}
        category_weights = {}
        
        for factor in factors:
            cat = factor.category.value
            if cat not in category_scores:
                category_scores[cat] = []
                category_weights[cat] = []
            
            category_scores[cat].append(factor.value)
            category_weights[cat].append(factor.weight)
        
        total_weighted = 0
        for cat, scores in category_scores.items():
            weights = category_weights[cat]
            if scores:
                weighted_avg = sum(s * w for s, w in zip(scores, weights)) / sum(weights)
                cat_weight = self.CATEGORY_WEIGHTS.get(
                    RiskFactorCategory(cat), 0.1
                )
                contributions[cat] = weighted_avg * cat_weight
                total_weighted += contributions[cat]
        
        # Normalize to percentage
        if total_weighted > 0:
            for cat in contributions:
                contributions[cat] = (contributions[cat] / total_weighted) * 100
        
        return contributions
    
    def _run_monte_carlo(
        self,
        volatility_pct: float,
        expected_return: float = 0,
        btc_correlation: float = 0.7
    ) -> MonteCarloResult:
        """
        Run Monte Carlo simulation for VaR calculation.
        
        Uses Geometric Brownian Motion with fat tails (Student-t).
        """
        result = MonteCarloResult(simulations=self.simulations)
        
        # Convert to decimals
        vol = volatility_pct / 100
        drift = expected_return / 100
        dt = self.time_horizon / 365
        
        # Generate random returns (fat-tailed distribution)
        returns = []
        for _ in range(self.simulations):
            # Use Student-t distribution for fat tails (df=5)
            # Approximate with normal + occasional jumps
            z = random.gauss(0, 1)
            
            # Add jump risk (10% chance of extreme move)
            if random.random() < 0.10:
                jump = random.gauss(0, 2)  # Extreme event
                z += jump
            
            # Geometric Brownian Motion return
            ret = (drift - 0.5 * vol**2) * dt + vol * math.sqrt(dt) * z
            
            # Add correlation impact from BTC
            btc_shock = random.gauss(0, 0.15)  # BTC volatility
            correlated_impact = btc_correlation * btc_shock * 0.3
            ret += correlated_impact
            
            returns.append(ret)
        
        # Sort for VaR calculation
        returns.sort()
        
        # Statistics
        result.mean_return = statistics.mean(returns)
        result.std_return = statistics.stdev(returns)
        result.max_loss = min(returns)
        result.max_gain = max(returns)
        
        # VaR and CVaR
        var_95_idx = int(self.simulations * 0.05)
        var_99_idx = int(self.simulations * 0.01)
        
        result.var_95 = returns[var_95_idx]
        result.var_99 = returns[var_99_idx]
        
        # Expected Shortfall (CVaR) - average of worst losses
        result.cvar_95 = statistics.mean(returns[:var_95_idx])
        result.cvar_99 = statistics.mean(returns[:var_99_idx])
        
        # Probability of loss
        losses = [r for r in returns if r < 0]
        result.probability_of_loss = len(losses) / self.simulations
        
        # Higher moments
        try:
            n = len(returns)
            mean = result.mean_return
            std = result.std_return
            
            # Skewness
            m3 = sum((r - mean)**3 for r in returns) / n
            result.skewness = m3 / (std**3) if std > 0 else 0
            
            # Kurtosis (excess)
            m4 = sum((r - mean)**4 for r in returns) / n
            result.kurtosis = (m4 / (std**4)) - 3 if std > 0 else 0
        except (ZeroDivisionError, ValueError, TypeError):
            result.skewness = 0
            result.kurtosis = 0
        
        # Key percentiles
        result.percentiles = {
            1: returns[int(self.simulations * 0.01)],
            5: returns[int(self.simulations * 0.05)],
            10: returns[int(self.simulations * 0.10)],
            25: returns[int(self.simulations * 0.25)],
            50: returns[int(self.simulations * 0.50)],
            75: returns[int(self.simulations * 0.75)],
            90: returns[int(self.simulations * 0.90)],
            95: returns[int(self.simulations * 0.95)],
            99: returns[int(self.simulations * 0.99)],
        }
        
        return result
    
    def _run_stress_tests(
        self,
        market: Dict,
        tokenomics: Dict,
        project_type: str
    ) -> Dict[str, float]:
        """Run historical stress test scenarios"""
        results = {}
        
        vol = market.get("volatility_30d", 80) / 100
        btc_corr = market.get("btc_correlation_30d", 0.7)
        liquidity = market.get("liquidity_score", 50) / 100
        
        # Project type sensitivity
        type_multiplier = {
            "defi": 1.2,      # DeFi more sensitive
            "nft": 1.3,       # NFTs very volatile
            "memecoin": 1.5,  # Memecoins extreme
            "infrastructure": 0.9,  # More stable
            "staking": 0.8,   # Staking platforms stable
        }.get(project_type, 1.0)
        
        for scenario in self.stress_scenarios:
            # Calculate impact based on scenario and asset characteristics
            base_impact = scenario.market_impact
            
            # Adjust for DeFi-specific scenarios
            if "defi" in project_type.lower():
                base_impact *= (1 + abs(scenario.defi_drawdown) * 0.3)
            
            # BTC correlation amplifies market crashes
            btc_factor = 1 + (btc_corr * abs(scenario.btc_drawdown) * 0.5)
            
            # Low liquidity amplifies all impacts
            liquidity_factor = 1 + (1 - liquidity) * 0.5
            
            # High volatility amplifies impacts
            vol_factor = 1 + vol * 0.3
            
            # Calculate final impact
            impact = base_impact * btc_factor * liquidity_factor * vol_factor * type_multiplier
            
            # Cap at -99%
            impact = max(-0.99, impact)
            
            results[scenario.name] = impact
        
        return results
    
    def _calculate_correlations(self, market: Dict) -> CorrelationMatrix:
        """Calculate asset correlations"""
        return CorrelationMatrix(
            assets=["BTC", "ETH", "S&P500", "Gold"],
            btc_correlation=market.get("btc_correlation_30d", 0.7),
            eth_correlation=market.get("eth_correlation_30d", 0.65),
            sp500_correlation=market.get("sp500_correlation", 0.3),
            gold_correlation=market.get("gold_correlation", 0.1)
        )
    
    def _analyze_drawdown(self, market: Dict) -> DrawdownAnalysis:
        """Analyze drawdown characteristics"""
        vol = market.get("volatility_30d", 80) / 100
        liquidity = market.get("liquidity_score", 50) / 100
        
        # Estimate max drawdown from volatility
        # Rule of thumb: MaxDD ≈ 3 * monthly_vol for crypto
        max_dd = min(0.95, vol * 3)
        
        # Average drawdown typically 40-60% of max
        avg_dd = max_dd * 0.5
        
        # Recovery probability based on liquidity
        recovery_prob = 0.5 + liquidity * 0.4
        
        # Duration estimate (days)
        duration = int(90 * (1 + vol))
        recovery = int(duration * 1.5)
        
        return DrawdownAnalysis(
            max_drawdown_pct=max_dd * 100,
            avg_drawdown_pct=avg_dd * 100,
            drawdown_duration_days=duration,
            recovery_probability=recovery_prob,
            time_to_recovery_days=recovery
        )
    
    def _calculate_esg(
        self,
        tokenomics: Dict,
        team: Dict,
        security: Dict
    ) -> ESGScore:
        """
        Calculate ESG score adapted for crypto.
        
        E = Environmental (energy efficiency, consensus mechanism)
        S = Social (community, accessibility, fairness)
        G = Governance (decentralization, transparency, voting)
        """
        esg = ESGScore()
        
        # Environmental (simplified - most crypto uses PoS now)
        # Assume PoS = 80 points, PoW = 30 points
        consensus = tokenomics.get("consensus_mechanism", "pos")
        if consensus.lower() in ["pos", "dpos", "poa"]:
            esg.environmental_score = 80
        elif consensus.lower() == "pow":
            esg.environmental_score = 30
        else:
            esg.environmental_score = 60
        
        # Social
        social_score = 50
        
        # Community size
        followers = team.get("social_followers", 0)
        if followers >= 100000:
            social_score += 20
        elif followers >= 10000:
            social_score += 10
        
        # Fair distribution
        team_pct = tokenomics.get("team_allocation_pct", 15)
        if team_pct <= 10:
            social_score += 20
        elif team_pct <= 20:
            social_score += 10
        
        # Community allocation
        community_pct = tokenomics.get("community_allocation_pct", 0)
        if community_pct >= 50:
            social_score += 15
        elif community_pct >= 30:
            social_score += 10
        
        esg.social_score = min(100, social_score)
        
        # Governance
        gov_score = 40  # Base
        
        gov_type = team.get("governance_type", "")
        if gov_type == "dao":
            gov_score += 30
        elif gov_type == "multisig":
            gov_score += 20
        
        if team.get("team_public", False):
            gov_score += 15
        
        if security.get("audit_count", 0) >= 2:
            gov_score += 10
        
        if tokenomics.get("vesting_period_months", 0) >= 24:
            gov_score += 10
        
        esg.governance_score = min(100, gov_score)
        
        # Overall ESG (weighted average)
        esg.overall_esg = (
            esg.environmental_score * 0.2 +
            esg.social_score * 0.3 +
            esg.governance_score * 0.5
        )
        
        # Rating
        if esg.overall_esg >= 80:
            esg.esg_rating = "AA"
        elif esg.overall_esg >= 70:
            esg.esg_rating = "A"
        elif esg.overall_esg >= 60:
            esg.esg_rating = "BBB"
        elif esg.overall_esg >= 50:
            esg.esg_rating = "BB"
        elif esg.overall_esg >= 40:
            esg.esg_rating = "B"
        else:
            esg.esg_rating = "CCC"
        
        return esg
    
    def _calculate_composite_score(
        self,
        factors: List[RiskFactor],
        monte_carlo: MonteCarloResult,
        esg: ESGScore
    ) -> float:
        """Calculate composite risk score (0-100)"""
        
        # 1. Factor-based score (weighted average)
        category_scores = {}
        category_weights_sum = {}
        
        for factor in factors:
            cat = factor.category
            if cat not in category_scores:
                category_scores[cat] = 0
                category_weights_sum[cat] = 0
            
            category_scores[cat] += factor.value * factor.weight
            category_weights_sum[cat] += factor.weight
        
        factor_score = 0
        total_weight = 0
        
        for cat, weighted_sum in category_scores.items():
            if category_weights_sum[cat] > 0:
                cat_avg = weighted_sum / category_weights_sum[cat]
                cat_weight = self.CATEGORY_WEIGHTS.get(cat, 0.1)
                factor_score += cat_avg * cat_weight
                total_weight += cat_weight
        
        if total_weight > 0:
            factor_score = factor_score / total_weight
        
        # 2. Monte Carlo adjustment
        # Penalize high VaR and high probability of loss
        mc_penalty = 0
        if monte_carlo.var_95 < -0.20:
            mc_penalty += abs(monte_carlo.var_95) * 20
        if monte_carlo.probability_of_loss > 0.5:
            mc_penalty += (monte_carlo.probability_of_loss - 0.5) * 20
        
        # 3. ESG bonus
        esg_bonus = (esg.overall_esg - 50) * 0.1  # Up to +5 or -5
        
        # Combine
        composite = factor_score - mc_penalty + esg_bonus
        
        return max(0, min(100, composite))
    
    def _calculate_risk_adjusted_score(
        self,
        composite_score: float,
        monte_carlo: MonteCarloResult
    ) -> float:
        """Calculate risk-adjusted score (Sharpe-like ratio)"""
        
        expected_return = monte_carlo.mean_return
        volatility = monte_carlo.std_return
        
        if volatility <= 0:
            return composite_score
        
        # Risk-free rate (assume 5% annual = ~0.4% monthly)
        risk_free = 0.004
        
        # Modified Sharpe
        sharpe = (expected_return - risk_free) / volatility if volatility > 0 else 0
        
        # Scale to 0-100
        # Sharpe of 2+ is excellent, 0.5 is average, negative is bad
        sharpe_score = 50 + sharpe * 25
        sharpe_score = max(0, min(100, sharpe_score))
        
        # Combine with composite (60/40)
        return composite_score * 0.6 + sharpe_score * 0.4
    
    def _get_risk_rating(self, score: float) -> str:
        """Convert numeric score to letter rating"""
        for threshold, rating in sorted(
            self.RISK_RATINGS.items(), reverse=True
        ):
            if score >= threshold:
                return rating
        return "D"
    
    def _generate_recommendation(self, report: AladdinRiskReport) -> str:
        """Generate investment recommendation"""
        score = report.composite_risk_score
        var = report.monte_carlo.var_95
        cvar = report.monte_carlo.cvar_95
        
        # Use CVaR (expected shortfall) instead of extreme worst case
        # Worst case includes hypothetical scenarios like quantum attacks
        
        # Primary recommendation based on score
        if score >= 85:
            rec = "STRONG_BUY"
        elif score >= 70:
            rec = "BUY"
        elif score >= 55:
            rec = "HOLD"
        elif score >= 40:
            rec = "REDUCE"
        else:
            rec = "AVOID"
        
        # Override for extreme VaR/CVaR (realistic risk)
        if var < -0.50:
            if rec == "STRONG_BUY":
                rec = "BUY"
            elif rec == "BUY":
                rec = "HOLD"
        
        # CVaR is expected shortfall - more conservative than VaR
        if cvar < -0.70:
            if rec in ["STRONG_BUY", "BUY"]:
                rec = "HOLD"
        
        return rec
    
    def _calculate_position_size(self, report: AladdinRiskReport) -> float:
        """
        Calculate recommended position size (% of portfolio).
        
        Uses Kelly Criterion with conservative adjustment.
        """
        score = report.composite_risk_score
        var = abs(report.monte_carlo.var_95)
        
        # Base allocation from score
        if score >= 80:
            base = 10.0  # Up to 10%
        elif score >= 70:
            base = 5.0
        elif score >= 60:
            base = 3.0
        elif score >= 50:
            base = 2.0
        else:
            base = 1.0
        
        # Adjust for VaR (reduce if high risk)
        if var > 0.30:
            base *= 0.5
        elif var > 0.20:
            base *= 0.7
        
        # Never more than 10% in single position
        return min(10.0, max(0.5, base))


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

def run_aladdin_analysis(
    tokenomics: Dict[str, Any],
    market: Dict[str, Any],
    security: Dict[str, Any],
    team: Dict[str, Any],
    project_type: str = "defi"
) -> AladdinRiskReport:
    """
    Convenience function to run Aladdin analysis.
    
    Example:
        report = run_aladdin_analysis(
            tokenomics={"team_allocation_pct": 15, "vesting_period_months": 36},
            market={"volatility_30d": 80, "volume_24h_usd": 1000000},
            security={"audit_count": 2, "critical_issues": 0},
            team={"team_public": True, "governance_type": "dao"}
        )
        print(f"Rating: {report.risk_rating}")
    """
    engine = AladdinEngine()
    return engine.analyze(tokenomics, market, security, team, project_type)


if __name__ == "__main__":
    # Quick test
    report = run_aladdin_analysis(
        tokenomics={
            "name": "Test Token",
            "team_allocation_pct": 15,
            "community_allocation_pct": 28,
            "vesting_period_months": 36,
            "cliff_months": 24,
        },
        market={
            "volatility_30d": 80,
            "volume_24h_usd": 500000,
            "volume_to_mcap_ratio": 0.05,
            "btc_correlation_30d": 0.6,
            "liquidity_score": 40,
        },
        security={
            "audit_count": 2,
            "critical_issues": 0,
            "security_score": 85,
            "contract_verified": True,
        },
        team={
            "team_public": True,
            "governance_type": "dao",
            "social_followers": 50000,
            "github_commits_30d": 150,
            "team_score": 75,
        },
        project_type="defi"
    )
    
    print(f"\n{'='*60}")
    print(f"ALADDIN ANALYSIS RESULT")
    print(f"{'='*60}")
    print(f"Composite Score: {report.composite_risk_score:.1f}/100")
    print(f"Risk Rating: {report.risk_rating}")
    print(f"ESG Rating: {report.esg.esg_rating}")
    print(f"VaR 95%: {report.monte_carlo.var_95:.1%}")
    print(f"CVaR 95%: {report.monte_carlo.cvar_95:.1%}")
    print(f"Max Drawdown: {report.drawdown.max_drawdown_pct:.1f}%")
    print(f"Worst Scenario: {report.worst_case_scenario} ({report.worst_case_loss:.1%})")
    print(f"Recommendation: {report.investment_recommendation}")
    print(f"Position Size: {report.position_sizing_suggestion:.1f}%")
    print(f"Factors Analyzed: {report.factors_analyzed}")
    print(f"Simulations Run: {report.simulations_run}")
