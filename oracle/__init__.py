"""
╔═══════════════════════════════════════════════════════════════════════════════╗
║                                                                               ║
║   ██████╗ ██████╗  █████╗  ██████╗██╗     ███████╗                           ║
║  ██╔═══██╗██╔══██╗██╔══██╗██╔════╝██║     ██╔════╝                           ║
║  ██║   ██║██████╔╝███████║██║     ██║     █████╗                             ║
║  ██║   ██║██╔══██╗██╔══██║██║     ██║     ██╔══╝                             ║
║  ╚██████╔╝██║  ██║██║  ██║╚██████╗███████╗███████╗                           ║
║   ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝╚══════╝╚══════╝                           ║
║                                                                               ║
║   🔮 Financial Intelligence & Risk Analysis System                            ║
║   Inspired by BlackRock's Aladdin                                            ║
║                                                                               ║
║   Version: 1.0.0                                                             ║
║   (c) 2024-2026 Lyxen                                                       ║
║                                                                               ║
╚═══════════════════════════════════════════════════════════════════════════════╝

Oracle - Autonomous Financial Analysis System for Crypto Projects

Features:
---------
1. 📊 Project Scanning & Analysis
   - Tokenomics analysis (supply, distribution, vesting)
   - Smart contract security audit (vulnerabilities, reentrancy)
   - Team & governance assessment
   - Market metrics evaluation (price, volume, volatility)

2. ⚠️ Risk Assessment
   - Rug pull risk detection
   - Centralization analysis
   - Regulatory risk assessment
   - Red flag detection (10+ conditions)

3. 📈 Portfolio Optimization
   - Monte Carlo VaR simulations
   - Efficient frontier calculation
   - Risk-adjusted returns (Sharpe, Sortino)
   - Stress testing (5 scenarios)
   - Kelly criterion position sizing

4. 📄 Automated Reports
   - HTML dashboards
   - JSON API responses
   - Markdown documentation
   - Executive summaries

5. 🤖 Autonomous Mode
   - Directory watching for new projects
   - Auto-analysis on file changes
   - Continuous monitoring
   - REST API server

Quick Start:
------------
    # CLI
    python -m oracle.cli analyze ./my_project
    python -m oracle.cli serve --port 8888
    
    # Python API
    from oracle import Oracle
    
    oracle = Oracle()
    
    # Analyze a project
    report = await oracle.analyze_project("/path/to/project")
    
    # Get scores
    print(f"Overall: {report.risk.overall_score}/100")
    print(f"Risk: {report.risk.risk_level}")
    print(f"Recommendation: {report.risk.investment_recommendation}")
    
    # Generate HTML report
    from oracle import ReportGenerator
    generator = ReportGenerator()
    generator.generate(report, format="html")
"""

from oracle.core import (
    Oracle,
    OracleReport,
    TokenomicsData,
    MarketData,
    SecurityData,
    TeamData,
    RiskMetrics
)
from oracle.risk_engine import RiskEngine
from oracle.tokenomics_analyzer import TokenomicsAnalyzer
from oracle.market_analyzer import MarketAnalyzer
from oracle.smart_contract_auditor import SmartContractAuditor, AuditResult, Vulnerability, Severity
from oracle.portfolio_optimizer import PortfolioOptimizer, Asset, AllocationResult, PortfolioMetrics
from oracle.report_generator import ReportGenerator, ReportConfig

__version__ = "1.0.0"
__author__ = "Lyxen Oracle Team"

__all__ = [
    # Core
    "Oracle",
    "OracleReport",
    
    # Data models
    "TokenomicsData",
    "MarketData",
    "SecurityData",
    "TeamData",
    "RiskMetrics",
    
    # Analyzers
    "RiskEngine",
    "TokenomicsAnalyzer",
    "MarketAnalyzer",
    "SmartContractAuditor",
    
    # Auditor models
    "AuditResult",
    "Vulnerability",
    "Severity",
    
    # Portfolio
    "PortfolioOptimizer",
    "Asset",
    "AllocationResult",
    "PortfolioMetrics",
    
    # Reports
    "ReportGenerator",
    "ReportConfig",
]
