"""
Oracle Core Engine - Main Analysis Orchestrator
================================================

The heart of Oracle system. Coordinates all analysis modules,
aggregates results, and produces comprehensive project evaluations.

Inspired by BlackRock's Aladdin architecture:
- Centralized data processing
- Multi-factor risk analysis
- Real-time market integration
- Automated decision support
"""

import os
import json
import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field, asdict
from pathlib import Path
from enum import Enum
import hashlib

logger = logging.getLogger("oracle")


class RiskLevel(Enum):
    """Risk classification levels"""
    CRITICAL = "critical"      # Score 0-20: Extremely high risk
    HIGH = "high"              # Score 21-40: High risk
    MEDIUM = "medium"          # Score 41-60: Moderate risk
    LOW = "low"                # Score 61-80: Low risk
    MINIMAL = "minimal"        # Score 81-100: Very low risk


class ProjectType(Enum):
    """Types of crypto projects"""
    DEFI = "defi"
    GAMING = "gaming"
    NFT = "nft"
    INFRASTRUCTURE = "infrastructure"
    EXCHANGE = "exchange"
    LENDING = "lending"
    STAKING = "staking"
    DAO = "dao"
    MEMECOIN = "memecoin"
    UNKNOWN = "unknown"


@dataclass
class TokenomicsData:
    """Tokenomics analysis results"""
    total_supply: float = 0
    circulating_supply: float = 0
    max_supply: Optional[float] = None
    
    # Distribution
    team_allocation_pct: float = 0
    investor_allocation_pct: float = 0
    community_allocation_pct: float = 0
    treasury_allocation_pct: float = 0
    liquidity_allocation_pct: float = 0
    
    # Vesting
    vesting_period_months: int = 0
    cliff_months: int = 0
    
    # Inflation/Deflation
    inflation_rate_annual_pct: float = 0
    burn_mechanism: bool = False
    staking_rewards_pct: float = 0
    
    # Scores
    distribution_score: float = 0  # 0-100
    vesting_score: float = 0       # 0-100
    sustainability_score: float = 0 # 0-100


@dataclass
class MarketData:
    """Market metrics"""
    price_usd: float = 0
    market_cap_usd: float = 0
    fully_diluted_valuation: float = 0
    volume_24h_usd: float = 0
    
    # Price changes
    price_change_1h_pct: float = 0
    price_change_24h_pct: float = 0
    price_change_7d_pct: float = 0
    price_change_30d_pct: float = 0
    
    # Volatility
    volatility_30d: float = 0
    volatility_90d: float = 0
    
    # Liquidity
    liquidity_score: float = 0     # 0-100
    volume_to_mcap_ratio: float = 0
    
    # Correlations
    btc_correlation_30d: float = 0
    eth_correlation_30d: float = 0


@dataclass
class SecurityData:
    """Smart contract security analysis"""
    contract_verified: bool = False
    audit_count: int = 0
    audit_firms: List[str] = field(default_factory=list)
    
    # Vulnerabilities
    critical_issues: int = 0
    high_issues: int = 0
    medium_issues: int = 0
    low_issues: int = 0
    
    # Code quality
    code_complexity_score: float = 0   # 0-100, higher is better
    test_coverage_pct: float = 0
    
    # Access control
    owner_privileges: List[str] = field(default_factory=list)
    has_pausable: bool = False
    has_upgradeable: bool = False
    has_mint_function: bool = False
    has_blacklist: bool = False
    
    # Overall
    security_score: float = 0  # 0-100


@dataclass
class TeamData:
    """Team and governance analysis"""
    team_public: bool = False
    team_size: int = 0
    team_experience_score: float = 0  # 0-100
    
    # Social presence
    twitter_followers: int = 0
    discord_members: int = 0
    telegram_members: int = 0
    github_contributors: int = 0
    
    # Activity
    github_commits_30d: int = 0
    social_engagement_score: float = 0  # 0-100
    
    # Governance
    governance_type: str = ""  # "multisig", "dao", "centralized"
    token_holder_voting: bool = False
    
    # Trust
    team_score: float = 0  # 0-100


@dataclass
class RiskMetrics:
    """Comprehensive risk assessment"""
    # Individual scores (0-100, higher = better/safer)
    tokenomics_score: float = 0
    market_score: float = 0
    security_score: float = 0
    team_score: float = 0
    liquidity_score: float = 0
    
    # Weighted overall score
    overall_score: float = 0
    risk_level: RiskLevel = RiskLevel.HIGH
    
    # Specific risks (0-1, lower = safer)
    rug_pull_risk: float = 0
    liquidity_risk: float = 0
    smart_contract_risk: float = 0
    centralization_risk: float = 0
    regulatory_risk: float = 0
    
    # Value at Risk (Aladdin-style Monte Carlo)
    var_95: float = 0  # 95% VaR
    var_99: float = 0  # 99% VaR
    cvar_95: float = 0  # Conditional VaR (Expected Shortfall)
    cvar_99: float = 0  # 99% Expected Shortfall
    
    # Stress test results (Aladdin historical scenarios)
    stress_test_results: Dict[str, float] = field(default_factory=dict)
    worst_case_scenario: str = ""
    worst_case_loss: float = 0
    
    # Aladdin-style metrics
    risk_rating: str = ""  # AAA to D (like credit ratings)
    esg_score: float = 0   # ESG score (0-100)
    esg_rating: str = ""   # AA, A, BBB, etc.
    factors_analyzed: int = 0
    simulations_run: int = 0
    
    # Drawdown analysis
    max_drawdown_pct: float = 0
    recovery_probability: float = 0
    
    # Factor contributions
    factor_contributions: Dict[str, float] = field(default_factory=dict)
    
    # Correlations
    btc_correlation: float = 0
    eth_correlation: float = 0
    
    # Warnings
    red_flags: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    
    # Recommendation
    investment_recommendation: str = ""  # "STRONG_BUY", "BUY", "HOLD", "REDUCE", "AVOID"
    position_size_pct: float = 0  # Recommended position size


@dataclass
class OracleReport:
    """Complete project analysis report"""
    # Metadata
    project_name: str = ""
    project_path: str = ""
    project_type: ProjectType = ProjectType.UNKNOWN
    analysis_timestamp: str = ""
    oracle_version: str = "1.0.0"
    report_id: str = ""
    
    # Analysis results
    tokenomics: TokenomicsData = field(default_factory=TokenomicsData)
    market: MarketData = field(default_factory=MarketData)
    security: SecurityData = field(default_factory=SecurityData)
    team: TeamData = field(default_factory=TeamData)
    risk: RiskMetrics = field(default_factory=RiskMetrics)
    
    # Summary
    executive_summary: str = ""
    key_findings: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    
    # Raw data
    raw_files_analyzed: int = 0
    analysis_duration_seconds: float = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)
    
    def to_json(self) -> str:
        """Convert to JSON string"""
        data = self.to_dict()
        # Handle enums
        data["project_type"] = self.project_type.value
        data["risk"]["risk_level"] = self.risk.risk_level.value
        return json.dumps(data, indent=2, default=str)


class Oracle:
    """
    Oracle - Autonomous Financial Intelligence System
    
    Main orchestrator that coordinates all analysis modules
    and produces comprehensive project evaluations.
    
    Usage:
        oracle = Oracle()
        report = await oracle.analyze_project("/path/to/project")
        print(report.risk.overall_score)
    """
    
    # Risk weights (must sum to 1.0)
    RISK_WEIGHTS = {
        "tokenomics": 0.25,
        "market": 0.20,
        "security": 0.30,
        "team": 0.15,
        "liquidity": 0.10
    }
    
    def __init__(
        self,
        config_path: Optional[str] = None,
        cache_dir: Optional[str] = None,
        api_keys: Optional[Dict[str, str]] = None
    ):
        """
        Initialize Oracle system.
        
        Args:
            config_path: Path to configuration file
            cache_dir: Directory for caching analysis results
            api_keys: API keys for external services (CoinGecko, Etherscan, etc.)
        """
        self.config = self._load_config(config_path)
        self.cache_dir = Path(cache_dir or ".oracle_cache")
        self.cache_dir.mkdir(exist_ok=True)
        self.api_keys = api_keys or {}
        
        # Initialize sub-modules (lazy loading)
        self._risk_engine = None
        self._aladdin_engine = None  # Aladdin-style advanced analysis
        self._tokenomics_analyzer = None
        self._market_analyzer = None
        self._contract_auditor = None
        self._portfolio_optimizer = None
        self._report_generator = None
        
        logger.info("Oracle system initialized (Aladdin-Enhanced)")
    
    def _load_config(self, config_path: Optional[str]) -> Dict[str, Any]:
        """Load configuration from file or use defaults"""
        default_config = {
            "analysis": {
                "max_files": 1000,
                "timeout_seconds": 300,
                "parallel_workers": 4
            },
            "risk": {
                "weights": self.RISK_WEIGHTS,
                "thresholds": {
                    "critical": 20,
                    "high": 40,
                    "medium": 60,
                    "low": 80
                }
            },
            "apis": {
                "coingecko_base_url": "https://api.coingecko.com/api/v3",
                "etherscan_base_url": "https://api.etherscan.io/api"
            }
        }
        
        if config_path and os.path.exists(config_path):
            with open(config_path) as f:
                user_config = json.load(f)
                default_config.update(user_config)
        
        return default_config
    
    @property
    def risk_engine(self):
        """Lazy load risk engine"""
        if self._risk_engine is None:
            from oracle.risk_engine import RiskEngine
            self._risk_engine = RiskEngine(self.config)
        return self._risk_engine
    
    @property
    def aladdin_engine(self):
        """Lazy load Aladdin advanced risk engine"""
        if self._aladdin_engine is None:
            from oracle.aladdin_engine import AladdinEngine
            self._aladdin_engine = AladdinEngine(
                monte_carlo_simulations=10000,
                confidence_level=0.95,
                time_horizon_days=30
            )
        return self._aladdin_engine
    
    @property
    def tokenomics_analyzer(self):
        """Lazy load tokenomics analyzer"""
        if self._tokenomics_analyzer is None:
            from oracle.tokenomics_analyzer import TokenomicsAnalyzer
            self._tokenomics_analyzer = TokenomicsAnalyzer(self.config)
        return self._tokenomics_analyzer
    
    @property
    def market_analyzer(self):
        """Lazy load market analyzer"""
        if self._market_analyzer is None:
            from oracle.market_analyzer import MarketAnalyzer
            self._market_analyzer = MarketAnalyzer(self.config, self.api_keys)
        return self._market_analyzer
    
    @property
    def contract_auditor(self):
        """Lazy load smart contract auditor"""
        if self._contract_auditor is None:
            from oracle.smart_contract_auditor import SmartContractAuditor
            self._contract_auditor = SmartContractAuditor(self.config)
        return self._contract_auditor
    
    @property
    def portfolio_optimizer(self):
        """Lazy load portfolio optimizer"""
        if self._portfolio_optimizer is None:
            from oracle.portfolio_optimizer import PortfolioOptimizer
            self._portfolio_optimizer = PortfolioOptimizer(self.config)
        return self._portfolio_optimizer
    
    @property
    def report_generator(self):
        """Lazy load report generator"""
        if self._report_generator is None:
            from oracle.report_generator import ReportGenerator
            self._report_generator = ReportGenerator(self.config)
        return self._report_generator
    
    async def analyze_project(
        self,
        project_path: str,
        project_name: Optional[str] = None,
        symbol: Optional[str] = None,
        contract_address: Optional[str] = None,
        chain: str = "ethereum"
    ) -> OracleReport:
        """
        Perform comprehensive project analysis.
        
        Args:
            project_path: Path to project directory or file
            project_name: Project/token name (auto-detected if not provided)
            symbol: Token symbol for market data
            contract_address: Smart contract address for on-chain analysis
            chain: Blockchain network (ethereum, bsc, polygon, etc.)
        
        Returns:
            OracleReport with complete analysis results
        """
        start_time = datetime.now()
        logger.info(f"Starting Oracle analysis for: {project_path}")
        
        # Initialize report
        report = OracleReport(
            project_path=project_path,
            project_name=project_name or os.path.basename(project_path),
            analysis_timestamp=start_time.isoformat(),
            report_id=self._generate_report_id(project_path)
        )
        
        try:
            # Step 1: Scan project files
            project_data = await self._scan_project(project_path)
            report.raw_files_analyzed = project_data.get("files_count", 0)
            report.project_type = self._detect_project_type(project_data)
            
            # Step 2: Analyze tokenomics (from whitepaper, docs, code)
            report.tokenomics = await self.tokenomics_analyzer.analyze(
                project_data, project_name
            )
            
            # Step 3: Get market data (if symbol provided)
            if symbol:
                report.market = await self.market_analyzer.analyze(symbol)
            
            # Step 4: Smart contract audit (if address provided)
            if contract_address:
                security, audit_result = await self.contract_auditor.audit(project_data)
                report.security = security
            else:
                # Analyze local smart contracts
                security, audit_result = await self.contract_auditor.audit(project_data)
                report.security = security
            
            # Step 5: Team analysis
            report.team = await self._analyze_team(project_data)
            
            # Step 6: Calculate comprehensive risk score (basic engine)
            report.risk = self.risk_engine.calculate(
                tokenomics=report.tokenomics,
                market=report.market,
                security=report.security,
                team=report.team
            )
            
            # Step 6b: Run Aladdin advanced analysis (enhanced metrics)
            aladdin_report = await self._run_aladdin_analysis(
                report.tokenomics,
                report.market,
                report.security,
                report.team,
                report.project_type.value
            )
            
            # Merge Aladdin results into risk metrics
            report.risk = self._merge_aladdin_results(report.risk, aladdin_report)
            
            # Step 7: Generate summary and recommendations
            report.executive_summary = self._generate_executive_summary(report)
            report.key_findings = self._extract_key_findings(report)
            report.recommendations = self._generate_recommendations(report)
            
            # Calculate duration
            report.analysis_duration_seconds = (
                datetime.now() - start_time
            ).total_seconds()
            
            # Cache report
            self._cache_report(report)
            
            logger.info(
                f"Analysis complete. Score: {report.risk.overall_score:.1f}/100 "
                f"({report.risk.risk_level.value})"
            )
            
        except Exception as e:
            logger.error(f"Analysis error: {e}", exc_info=True)
            report.risk.red_flags.append(f"Analysis error: {str(e)}")
            report.risk.overall_score = 0
            report.risk.risk_level = RiskLevel.CRITICAL
        
        return report
    
    async def _scan_project(self, project_path: str) -> Dict[str, Any]:
        """Scan project directory and extract relevant data"""
        path = Path(project_path)
        
        if not path.exists():
            raise FileNotFoundError(f"Project path not found: {project_path}")
        
        data = {
            "path": str(path.absolute()),
            "files_count": 0,
            "smart_contracts": [],
            "documentation": [],
            "config_files": [],
            "source_code": [],
            "tokenomics_files": [],
            "readme_content": "",
            "package_info": {}
        }
        
        # File patterns to look for
        patterns = {
            "smart_contracts": ["*.sol", "*.vy", "*.cairo", "*.move"],
            "documentation": ["*.md", "*.rst", "*.txt", "*.pdf"],
            "config_files": ["*.json", "*.yaml", "*.yml", "*.toml"],
            "source_code": ["*.py", "*.js", "*.ts", "*.go", "*.rs"]
        }
        
        if path.is_file():
            # Single file analysis
            data["files_count"] = 1
            content = self._read_file_safe(path)
            if path.suffix == ".sol":
                data["smart_contracts"].append({"path": str(path), "content": content})
            elif path.suffix in [".md", ".txt"]:
                data["documentation"].append({"path": str(path), "content": content})
        else:
            # Directory analysis
            for file_path in path.rglob("*"):
                if file_path.is_file():
                    data["files_count"] += 1
                    
                    # Skip node_modules, venv, etc.
                    if any(x in str(file_path) for x in [
                        "node_modules", "venv", ".git", "__pycache__", "dist", "build"
                    ]):
                        continue
                    
                    # Categorize files
                    content = self._read_file_safe(file_path)
                    file_info = {"path": str(file_path), "content": content}
                    
                    if file_path.suffix == ".sol":
                        data["smart_contracts"].append(file_info)
                    elif file_path.name.lower() in ["readme.md", "readme.txt"]:
                        data["readme_content"] = content
                    elif file_path.name.lower() in ["tokenomics.md", "whitepaper.md", "economics.md"]:
                        data["tokenomics_files"].append(file_info)
                    elif file_path.suffix in [".md", ".rst"]:
                        data["documentation"].append(file_info)
                    elif file_path.name in ["package.json", "hardhat.config.js", "truffle-config.js"]:
                        data["config_files"].append(file_info)
                        if file_path.name == "package.json" and content:
                            try:
                                data["package_info"] = json.loads(content)
                            except:
                                pass
        
        return data
    
    def _read_file_safe(self, path: Path, max_size: int = 1_000_000) -> str:
        """Safely read file content"""
        try:
            if path.stat().st_size > max_size:
                return ""  # Skip large files
            return path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            return ""
    
    def _detect_project_type(self, project_data: Dict) -> ProjectType:
        """Detect project type from code and documentation"""
        all_content = (
            project_data.get("readme_content", "") +
            " ".join(d.get("content", "") for d in project_data.get("documentation", []))
        ).lower()
        
        # Keywords for each type
        type_keywords = {
            ProjectType.DEFI: ["defi", "decentralized finance", "yield", "farming", "amm", "swap", "liquidity pool"],
            ProjectType.LENDING: ["lending", "borrowing", "collateral", "loan", "interest rate", "aave", "compound"],
            ProjectType.STAKING: ["staking", "stake", "validator", "delegation", "proof of stake"],
            ProjectType.EXCHANGE: ["exchange", "dex", "order book", "trading", "spot", "futures"],
            ProjectType.NFT: ["nft", "erc721", "erc1155", "non-fungible", "collectible", "marketplace"],
            ProjectType.GAMING: ["game", "gaming", "play to earn", "p2e", "metaverse", "gamefi"],
            ProjectType.DAO: ["dao", "governance", "voting", "proposal", "treasury"],
            ProjectType.INFRASTRUCTURE: ["infrastructure", "layer 2", "l2", "bridge", "oracle", "indexer"],
            ProjectType.MEMECOIN: ["meme", "doge", "shib", "pepe", "community", "fair launch"]
        }
        
        scores = {ptype: 0 for ptype in ProjectType}
        for ptype, keywords in type_keywords.items():
            for keyword in keywords:
                if keyword in all_content:
                    scores[ptype] += 1
        
        best_match = max(scores, key=scores.get)
        return best_match if scores[best_match] > 0 else ProjectType.UNKNOWN
    
    async def _analyze_team(self, project_data: Dict) -> TeamData:
        """Analyze team from available data"""
        team = TeamData()
        
        # Check for team info in readme
        readme = project_data.get("readme_content", "").lower()
        
        # Team visibility
        team.team_public = any(x in readme for x in ["team", "founder", "ceo", "cto", "developer"])
        
        # GitHub info from package.json
        pkg = project_data.get("package_info", {})
        if pkg:
            repo_url = pkg.get("repository", {})
            if isinstance(repo_url, dict):
                repo_url = repo_url.get("url", "")
            # Could fetch GitHub API for more data
            team.github_contributors = 1  # Placeholder
        
        # Calculate score based on available info
        score = 50  # Base score
        if team.team_public:
            score += 20
        if team.github_contributors > 5:
            score += 15
        if "audit" in readme:
            score += 15
        
        team.team_score = min(100, score)
        return team
    
    def _generate_executive_summary(self, report: OracleReport) -> str:
        """Generate executive summary paragraph"""
        risk = report.risk
        
        risk_text = {
            RiskLevel.CRITICAL: "extremely high risk with critical concerns",
            RiskLevel.HIGH: "high risk requiring careful consideration",
            RiskLevel.MEDIUM: "moderate risk with some concerns",
            RiskLevel.LOW: "relatively low risk with minor concerns",
            RiskLevel.MINIMAL: "minimal risk with strong fundamentals"
        }
        
        summary = f"""
{report.project_name} ({report.project_type.value.upper()})

Oracle Risk Assessment: {risk.overall_score:.0f}/100 ({risk.risk_level.value.upper()})

This project presents {risk_text.get(risk.risk_level, 'unknown risk')}.

Key Metrics:
- Tokenomics Score: {report.tokenomics.distribution_score:.0f}/100
- Security Score: {report.security.security_score:.0f}/100
- Team Score: {report.team.team_score:.0f}/100
- Market Score: {report.market.liquidity_score:.0f}/100

{f"⚠️ Red Flags: {', '.join(risk.red_flags[:3])}" if risk.red_flags else "✅ No critical red flags detected."}

Investment Recommendation: {risk.investment_recommendation.upper().replace('_', ' ')}
        """.strip()
        
        return summary
    
    def _extract_key_findings(self, report: OracleReport) -> List[str]:
        """Extract key findings from analysis"""
        findings = []
        
        # Tokenomics findings
        if report.tokenomics.team_allocation_pct > 30:
            findings.append(f"High team allocation ({report.tokenomics.team_allocation_pct:.1f}%)")
        if report.tokenomics.vesting_period_months < 12:
            findings.append(f"Short vesting period ({report.tokenomics.vesting_period_months} months)")
        if report.tokenomics.burn_mechanism:
            findings.append("✓ Deflationary mechanism (token burn)")
        
        # Security findings
        if report.security.critical_issues > 0:
            findings.append(f"⚠️ {report.security.critical_issues} critical security issues")
        if report.security.audit_count > 0:
            findings.append(f"✓ Audited by {', '.join(report.security.audit_firms[:2])}")
        if report.security.has_mint_function:
            findings.append("⚠️ Contract has mint function (inflation risk)")
        if not report.security.contract_verified:
            findings.append("⚠️ Contract not verified on block explorer")
        
        # Market findings
        if report.market.volume_to_mcap_ratio < 0.01:
            findings.append("Low trading volume relative to market cap")
        if report.market.volatility_30d > 100:
            findings.append(f"High volatility (30d: {report.market.volatility_30d:.1f}%)")
        
        # Add red flags
        findings.extend([f"🚨 {flag}" for flag in report.risk.red_flags[:5]])
        
        return findings[:10]  # Top 10 findings
    
    def _generate_recommendations(self, report: OracleReport) -> List[str]:
        """Generate actionable recommendations"""
        recs = []
        risk = report.risk
        
        # Investment stance
        if risk.overall_score >= 80:
            recs.append("Consider as part of diversified portfolio")
        elif risk.overall_score >= 60:
            recs.append("Proceed with moderate position size")
        elif risk.overall_score >= 40:
            recs.append("Small position only if risk tolerance is high")
        else:
            recs.append("AVOID - Risk profile exceeds safe investment parameters")
        
        # Specific recommendations
        if risk.rug_pull_risk > 50:
            recs.append("⚠️ High rug pull risk - verify team identity before investing")
        if risk.liquidity_risk > 50:
            recs.append("Use limit orders and small position sizes due to liquidity concerns")
        if risk.smart_contract_risk > 50:
            recs.append("Wait for additional security audits before significant investment")
        if risk.centralization_risk > 50:
            recs.append("Monitor governance decisions - high centralization detected")
        
        # Position sizing
        if risk.overall_score >= 70:
            recs.append("Suggested position size: 2-5% of portfolio")
        elif risk.overall_score >= 50:
            recs.append("Suggested position size: 0.5-1% of portfolio")
        else:
            recs.append("Suggested position size: 0% (avoid)")
        
        return recs
    
    def _generate_report_id(self, project_path: str) -> str:
        """Generate unique report ID"""
        data = f"{project_path}:{datetime.now().isoformat()}"
        return hashlib.md5(data.encode()).hexdigest()[:12]
    
    def _cache_report(self, report: OracleReport) -> None:
        """Cache report to disk"""
        cache_file = self.cache_dir / f"{report.report_id}.json"
        with open(cache_file, "w") as f:
            f.write(report.to_json())
    
    async def _run_aladdin_analysis(
        self,
        tokenomics: TokenomicsData,
        market: MarketData,
        security: SecurityData,
        team: TeamData,
        project_type: str
    ):
        """
        Run Aladdin-style advanced risk analysis.
        
        This provides BlackRock Aladdin-inspired features:
        - Monte Carlo simulation (10,000 scenarios)
        - Historical stress testing
        - 100+ risk factors
        - ESG scoring
        - Risk-adjusted returns
        """
        from dataclasses import asdict
        
        # Convert dataclasses to dicts for Aladdin engine
        tokenomics_dict = asdict(tokenomics) if tokenomics else {}
        tokenomics_dict["name"] = tokenomics_dict.get("name", "Unknown")
        
        market_dict = asdict(market) if market else {}
        security_dict = asdict(security) if security else {}
        team_dict = asdict(team) if team else {}
        
        # Add missing fields for Aladdin
        if "social_followers" not in team_dict:
            team_dict["social_followers"] = (
                team_dict.get("twitter_followers", 0) +
                team_dict.get("discord_members", 0)
            )
        
        # Run Aladdin analysis
        return self.aladdin_engine.analyze(
            tokenomics=tokenomics_dict,
            market=market_dict,
            security=security_dict,
            team=team_dict,
            project_type=project_type
        )
    
    def _merge_aladdin_results(self, risk: RiskMetrics, aladdin) -> RiskMetrics:
        """
        Merge Aladdin analysis results into RiskMetrics.
        
        Combines basic risk engine results with advanced Aladdin metrics.
        """
        # VaR and CVaR from Aladdin Monte Carlo
        if hasattr(aladdin, 'monte_carlo'):
            mc = aladdin.monte_carlo
            risk.var_95 = mc.var_95
            risk.var_99 = mc.var_99
            risk.cvar_95 = mc.cvar_95
            risk.cvar_99 = mc.cvar_99
        
        # Stress test results
        if hasattr(aladdin, 'stress_test_results'):
            risk.stress_test_results = aladdin.stress_test_results
            risk.worst_case_scenario = aladdin.worst_case_scenario
            risk.worst_case_loss = aladdin.worst_case_loss
        
        # ESG scores
        if hasattr(aladdin, 'esg'):
            risk.esg_score = aladdin.esg.overall_esg
            risk.esg_rating = aladdin.esg.esg_rating
        
        # Aladdin ratings and recommendations
        if hasattr(aladdin, 'risk_rating'):
            risk.risk_rating = aladdin.risk_rating
        if hasattr(aladdin, 'investment_recommendation'):
            risk.investment_recommendation = aladdin.investment_recommendation
        if hasattr(aladdin, 'position_sizing_suggestion'):
            risk.position_size_pct = aladdin.position_sizing_suggestion
        
        # Factor analysis
        if hasattr(aladdin, 'factors_analyzed'):
            risk.factors_analyzed = aladdin.factors_analyzed
        if hasattr(aladdin, 'simulations_run'):
            risk.simulations_run = aladdin.simulations_run
        if hasattr(aladdin, 'factor_contributions'):
            risk.factor_contributions = aladdin.factor_contributions
        
        # Correlations
        if hasattr(aladdin, 'correlations'):
            risk.btc_correlation = aladdin.correlations.btc_correlation
            risk.eth_correlation = aladdin.correlations.eth_correlation
        
        # Drawdown analysis
        if hasattr(aladdin, 'drawdown'):
            risk.max_drawdown_pct = aladdin.drawdown.max_drawdown_pct
            risk.recovery_probability = aladdin.drawdown.recovery_probability
        
        # Use Aladdin composite score if higher quality
        if hasattr(aladdin, 'composite_risk_score'):
            # Average with existing score for robustness
            risk.overall_score = (risk.overall_score + aladdin.composite_risk_score) / 2
        
        return risk
    
    def get_cached_report(self, report_id: str) -> Optional[OracleReport]:
        """Retrieve cached report by ID"""
        cache_file = self.cache_dir / f"{report_id}.json"
        if cache_file.exists():
            with open(cache_file) as f:
                data = json.load(f)
                # Reconstruct report (simplified)
                return data
        return None
    
    def generate_report(
        self,
        report: OracleReport,
        output_path: str,
        format: str = "pdf"
    ) -> str:
        """Generate formatted report file"""
        return self.report_generator.generate(report, output_path, format)
    
    async def watch_directory(
        self,
        directory: str,
        callback: Optional[callable] = None,
        interval_seconds: int = 60
    ):
        """
        Watch a directory for new projects and analyze them automatically.
        
        Args:
            directory: Directory to watch
            callback: Function to call with report when analysis completes
            interval_seconds: How often to check for new files
        """
        watched_dir = Path(directory)
        analyzed_projects = set()
        
        logger.info(f"Oracle watching directory: {watched_dir}")
        
        while True:
            try:
                # Find subdirectories (each is a project)
                for item in watched_dir.iterdir():
                    if item.is_dir() and item.name not in analyzed_projects:
                        if not item.name.startswith("."):
                            logger.info(f"New project detected: {item.name}")
                            
                            report = await self.analyze_project(str(item))
                            analyzed_projects.add(item.name)
                            
                            if callback:
                                callback(report)
                            else:
                                # Default: print summary
                                print(f"\n{'='*60}")
                                print(report.executive_summary)
                                print(f"{'='*60}\n")
                
                await asyncio.sleep(interval_seconds)
                
            except Exception as e:
                logger.error(f"Watch error: {e}")
                await asyncio.sleep(interval_seconds)


# CLI entry point
async def main():
    """Oracle CLI entry point"""
    import sys
    
    print("""
    ╔═══════════════════════════════════════════════════════════════╗
    ║  ORACLE - Financial Intelligence System v1.0                  ║
    ║  Autonomous Project Analysis Engine                           ║
    ╚═══════════════════════════════════════════════════════════════╝
    """)
    
    if len(sys.argv) < 2:
        print("Usage: python -m oracle.core <project_path> [symbol] [contract_address]")
        print("\nExample:")
        print("  python -m oracle.core ./my_project")
        print("  python -m oracle.core ./my_project BTC")
        print("  python -m oracle.core ./my_project ETH 0x1234...")
        return
    
    project_path = sys.argv[1]
    symbol = sys.argv[2] if len(sys.argv) > 2 else None
    contract = sys.argv[3] if len(sys.argv) > 3 else None
    
    oracle = Oracle()
    report = await oracle.analyze_project(
        project_path,
        symbol=symbol,
        contract_address=contract
    )
    
    print(report.executive_summary)
    print("\n" + "="*60)
    print("KEY FINDINGS:")
    for finding in report.key_findings:
        print(f"  • {finding}")
    print("\n" + "="*60)
    print("RECOMMENDATIONS:")
    for rec in report.recommendations:
        print(f"  → {rec}")
    print("="*60)


if __name__ == "__main__":
    asyncio.run(main())
