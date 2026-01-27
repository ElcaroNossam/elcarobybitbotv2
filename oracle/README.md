# 🔮 Oracle - Financial Intelligence System

> **BlackRock Aladdin-inspired Analysis Engine for Crypto Projects**

Oracle is an autonomous financial analysis system that evaluates crypto projects across multiple dimensions: tokenomics, security, market data, and team metrics. It produces comprehensive risk assessments and investment recommendations.

## 🚀 Quick Start

### CLI Usage

```bash
# Analyze a project
python -m oracle.cli analyze ./path/to/project

# Analyze with HTML report
python -m oracle.cli analyze ./project -o ./reports/my_report.html -f html

# Start API server
python -m oracle.cli serve --port 8888

# Watch directory for auto-analysis
python -m oracle.cli watch ./projects
```

### Python API

```python
from oracle import Oracle, ReportGenerator

# Initialize
oracle = Oracle()

# Analyze project
report = await oracle.analyze_project("./my_crypto_project")

# Get results
print(f"Score: {report.risk.overall_score}/100")
print(f"Risk: {report.risk.risk_level}")
print(f"Recommendation: {report.risk.investment_recommendation}")
print(f"Red Flags: {len(report.risk.red_flags)}")

# Generate HTML report
generator = ReportGenerator()
generator.generate(report, format="html")
```

## 📊 Analysis Modules

### 1. Tokenomics Analyzer
Extracts and scores token economics:
- Token distribution (team, community, treasury)
- Vesting schedules and cliff periods
- Inflation/deflation mechanisms
- Burn mechanisms
- Staking rewards

**Score Components:**
- Distribution Score (fair allocation)
- Vesting Score (lock-up quality)
- Sustainability Score (long-term health)

### 2. Market Analyzer
Real-time market data analysis:
- Price and market cap
- 24h/7d/30d volume
- Volatility (30d annualized)
- BTC/ETH correlation
- Liquidity depth

**Data Sources:**
- CoinGecko API
- CoinMarketCap API (with key)

### 3. Smart Contract Auditor
Automated security analysis:
- Reentrancy vulnerabilities
- Integer overflow (pre-0.8.0)
- Unchecked external calls
- tx.origin authentication
- Delegatecall risks
- Selfdestruct presence

**Detects 12+ vulnerability patterns**

### 4. Risk Engine
Comprehensive risk scoring:

| Factor | Weight |
|--------|--------|
| Security | 30% |
| Tokenomics | 25% |
| Market | 20% |
| Team | 15% |
| Liquidity | 10% |

**Red Flag Detection (10 conditions):**
- Team allocation >30%
- No vesting/cliff
- Unaudited contracts
- Anonymous team
- Mint function + no multisig
- Blacklist capability
- Low liquidity
- High volatility
- No GitHub activity
- Regulatory concerns

**Risk Levels:**
- 🟢 **Minimal** (81-100): Very safe
- 🔵 **Low** (61-80): Generally safe
- 🟡 **Medium** (41-60): Caution advised
- 🟠 **High** (21-40): Significant risk
- 🔴 **Critical** (0-20): Avoid

### 5. Portfolio Optimizer
Modern Portfolio Theory for crypto:
- Efficient frontier calculation
- Maximum Sharpe ratio allocation
- Minimum volatility portfolio
- Risk parity allocation
- Kelly criterion position sizing
- Monte Carlo VaR simulations

### 6. Report Generator
Professional report formats:
- **HTML**: Beautiful dashboards with charts
- **JSON**: API-friendly data
- **Markdown**: Documentation-ready
- **Text**: Simple summary

## 🏗️ Architecture

```
oracle/
├── __init__.py           # Package exports
├── core.py               # Main Oracle class & data models
├── risk_engine.py        # Risk scoring & Monte Carlo
├── tokenomics_analyzer.py # Token economics analysis
├── market_analyzer.py    # CoinGecko/CMC integration
├── smart_contract_auditor.py # Solidity security audit
├── portfolio_optimizer.py # MPT & position sizing
├── report_generator.py   # Multi-format reports
└── cli.py               # CLI & API server
```

## 📦 Data Classes

### TokenomicsData
```python
@dataclass
class TokenomicsData:
    total_supply: float
    circulating_supply: float
    team_allocation_pct: float
    community_allocation_pct: float
    vesting_period_months: int
    cliff_months: int
    burn_mechanism: bool
    distribution_score: float  # 0-100
```

### MarketData
```python
@dataclass
class MarketData:
    price_usd: float
    market_cap_usd: float
    volume_24h_usd: float
    volatility_30d: float
    btc_correlation_30d: float
    liquidity_score: float  # 0-100
```

### SecurityData
```python
@dataclass
class SecurityData:
    contract_verified: bool
    audit_count: int
    critical_issues: int
    has_reentrancy_guard: bool
    has_mint_function: bool
    has_blacklist: bool
    security_score: float  # 0-100
```

### RiskMetrics
```python
@dataclass
class RiskMetrics:
    overall_score: float        # 0-100
    risk_level: str             # minimal/low/medium/high/critical
    investment_recommendation: str  # strong_buy/buy/hold/sell/avoid
    red_flags: List[str]
    rug_pull_risk: float
    centralization_risk: float
    regulatory_risk: float
```

## 🌐 API Server

Start the API server:
```bash
python -m oracle.cli serve --port 8888
```

### Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | API info |
| GET | `/api/status` | System status |
| POST | `/api/analyze` | Analyze project |
| GET | `/api/report/{id}` | Get report |
| GET | `/api/reports` | List all reports |
| DELETE | `/api/report/{id}` | Delete report |

### Analyze Request
```json
POST /api/analyze
{
    "path": "/path/to/project",
    "generate_report": true,
    "report_format": "json"
}
```

### Response
```json
{
    "success": true,
    "report_id": "abc123",
    "project_name": "MyToken",
    "overall_score": 72.5,
    "risk_level": "medium",
    "recommendation": "hold",
    "red_flags_count": 2
}
```

## 🔧 Configuration

### Environment Variables
```bash
# CoinMarketCap API key (optional)
CMC_API_KEY=your_api_key

# CoinGecko Pro API key (optional)
CG_API_KEY=your_api_key
```

### Config Object
```python
from oracle import Oracle

config = {
    "cmc_api_key": "your_key",
    "coingecko_api_key": "your_key",
    "cache_ttl": 300,
    "output_dir": "./reports"
}

oracle = Oracle(config)
```

## 📈 Stress Testing

The Risk Engine includes stress testing with 5 scenarios:

1. **Market Crash** (-50% BTC)
2. **Bear Market** (-30% gradual)
3. **Flash Crash** (-20% spike)
4. **Liquidity Crisis** (-40%)
5. **Black Swan** (-70% catastrophic)

Each scenario estimates portfolio impact based on:
- Asset volatility
- BTC correlation
- Liquidity depth

## 🎯 Use Cases

### 1. Project Due Diligence
```python
report = await oracle.analyze_project("./new_token")
if report.risk.risk_level in ["high", "critical"]:
    print("⚠️ High risk - avoid investment")
    for flag in report.risk.red_flags:
        print(f"  - {flag}")
```

### 2. Portfolio Optimization
```python
from oracle import PortfolioOptimizer, Asset

assets = [
    Asset("BTC", expected_return=0.5, volatility=0.6, risk_score=35),
    Asset("ETH", expected_return=0.8, volatility=0.8, risk_score=40),
    Asset("SOL", expected_return=1.2, volatility=1.2, risk_score=55),
]

optimizer = PortfolioOptimizer()
result = optimizer.optimize(assets, target="max_sharpe")

print(f"Optimal allocation: {result.weights}")
print(f"Expected return: {result.metrics.expected_return:.1%}")
print(f"Sharpe ratio: {result.metrics.sharpe_ratio:.2f}")
```

### 3. Continuous Monitoring
```python
# Watch directory for new projects
await oracle.watch_directory("./projects_to_analyze")
```

### 4. API Integration
```bash
# Analyze via API
curl -X POST http://localhost:8888/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"path": "./project", "generate_report": true}'
```

## 📝 Output Examples

### HTML Report
Beautiful dashboard with:
- Score circle visualization
- Risk badge (color-coded)
- Red flags section
- Metric cards (Tokenomics, Market, Security, Team)
- Progress bars for scores
- Executive summary

### JSON Report
```json
{
    "report_id": "oracle_20241230_143022_abcd1234",
    "project_name": "MyDeFi",
    "overall_score": 68.5,
    "risk_level": "low",
    "tokenomics": {
        "total_supply": 100000000,
        "team_allocation_pct": 15,
        "distribution_score": 75
    },
    "security": {
        "contract_verified": true,
        "audit_count": 2,
        "security_score": 82
    },
    "risk": {
        "rug_pull_risk": 0.15,
        "red_flags": ["No cliff period"]
    }
}
```

## 🔐 Security Notes

- Oracle performs **read-only** analysis
- No private keys required
- API calls use rate limiting
- Reports stored locally only
- No external data transmission

## 📚 References

- [Modern Portfolio Theory](https://en.wikipedia.org/wiki/Modern_portfolio_theory)
- [BlackRock Aladdin](https://www.blackrock.com/aladdin)
- [Smart Contract Security](https://swcregistry.io/)
- [CoinGecko API](https://www.coingecko.com/en/api)

---

**🔮 Oracle** - *Autonomous Financial Intelligence for Crypto*

Version 1.0.0 | Enliko © 2024-2025
