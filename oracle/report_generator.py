"""
Oracle Report Generator
=======================

Generates comprehensive analysis reports:
- PDF reports
- HTML dashboards
- JSON API responses
- Executive summaries
- Risk alerts

Formats designed for:
- Investors
- Developers
- Compliance
"""

import json
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
import html

from oracle.core import (
    OracleReport,
    TokenomicsData,
    MarketData,
    SecurityData,
    TeamData,
    RiskMetrics
)

logger = logging.getLogger("oracle.reports")


@dataclass
class ReportConfig:
    """Report generation configuration"""
    output_dir: str = "./reports"
    include_charts: bool = True
    include_raw_data: bool = False
    language: str = "en"
    theme: str = "dark"  # dark/light


class ReportGenerator:
    """
    Report Generation Engine
    
    Creates professional analysis reports from Oracle data.
    """
    
    # Risk level colors
    RISK_COLORS = {
        "low": "#22c55e",       # Green
        "medium": "#eab308",    # Yellow
        "high": "#ef4444",      # Red
        "critical": "#dc2626",  # Dark red
    }
    
    # Score colors
    SCORE_COLORS = {
        "excellent": "#22c55e",  # 80+
        "good": "#84cc16",       # 60-79
        "fair": "#eab308",       # 40-59
        "poor": "#f97316",       # 20-39
        "critical": "#ef4444",   # 0-19
    }
    
    def __init__(self, config: Optional[ReportConfig] = None):
        self.config = config or ReportConfig()
        Path(self.config.output_dir).mkdir(parents=True, exist_ok=True)
    
    def generate(
        self,
        report: OracleReport,
        format: str = "html"  # html, json, text, pdf
    ) -> str:
        """
        Generate report in specified format.
        
        Args:
            report: OracleReport from Oracle analysis
            format: Output format (html, json, text, pdf)
        
        Returns:
            Path to generated report or report content
        """
        if format == "html":
            return self._generate_html(report)
        elif format == "json":
            return self._generate_json(report)
        elif format == "text":
            return self._generate_text(report)
        elif format == "markdown":
            return self._generate_markdown(report)
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def _generate_html(self, report: OracleReport) -> str:
        """Generate HTML report"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"oracle_report_{report.project_name}_{timestamp}.html"
        filepath = Path(self.config.output_dir) / filename
        
        # Get colors
        risk_color = self.RISK_COLORS.get(report.risk.risk_level, "#6b7280")
        score_color = self._get_score_color(report.risk.overall_score)
        
        # Build HTML
        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Oracle Report: {html.escape(report.project_name)}</title>
    <style>
        :root {{
            --bg-primary: #0f0f0f;
            --bg-secondary: #1a1a1a;
            --bg-card: #252525;
            --text-primary: #ffffff;
            --text-secondary: #a0a0a0;
            --border: #333333;
            --accent: #8b5cf6;
            --success: #22c55e;
            --warning: #eab308;
            --danger: #ef4444;
        }}
        
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            background: var(--bg-primary);
            color: var(--text-primary);
            line-height: 1.6;
            padding: 2rem;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
        }}
        
        header {{
            text-align: center;
            margin-bottom: 3rem;
            padding: 2rem;
            background: linear-gradient(135deg, rgba(139, 92, 246, 0.1), rgba(59, 130, 246, 0.1));
            border-radius: 16px;
            border: 1px solid var(--border);
        }}
        
        .logo {{
            font-size: 3rem;
            margin-bottom: 1rem;
        }}
        
        h1 {{
            font-size: 2.5rem;
            background: linear-gradient(135deg, #8b5cf6, #3b82f6);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 0.5rem;
        }}
        
        .project-name {{
            font-size: 1.5rem;
            color: var(--text-secondary);
        }}
        
        .score-hero {{
            display: flex;
            justify-content: center;
            align-items: center;
            gap: 3rem;
            margin: 2rem 0;
        }}
        
        .score-circle {{
            width: 150px;
            height: 150px;
            border-radius: 50%;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            border: 4px solid {score_color};
            background: rgba(255, 255, 255, 0.05);
        }}
        
        .score-value {{
            font-size: 3rem;
            font-weight: bold;
            color: {score_color};
        }}
        
        .score-label {{
            font-size: 0.875rem;
            color: var(--text-secondary);
        }}
        
        .risk-badge {{
            padding: 0.5rem 1.5rem;
            border-radius: 9999px;
            font-weight: 600;
            text-transform: uppercase;
            background: {risk_color}20;
            color: {risk_color};
            border: 1px solid {risk_color};
        }}
        
        .grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 1.5rem;
            margin-bottom: 2rem;
        }}
        
        .card {{
            background: var(--bg-card);
            border-radius: 12px;
            padding: 1.5rem;
            border: 1px solid var(--border);
        }}
        
        .card-title {{
            font-size: 1.25rem;
            margin-bottom: 1rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }}
        
        .metric {{
            display: flex;
            justify-content: space-between;
            padding: 0.75rem 0;
            border-bottom: 1px solid var(--border);
        }}
        
        .metric:last-child {{
            border-bottom: none;
        }}
        
        .metric-label {{
            color: var(--text-secondary);
        }}
        
        .metric-value {{
            font-weight: 600;
        }}
        
        .metric-value.positive {{
            color: var(--success);
        }}
        
        .metric-value.negative {{
            color: var(--danger);
        }}
        
        .progress-bar {{
            width: 100%;
            height: 8px;
            background: var(--bg-secondary);
            border-radius: 4px;
            overflow: hidden;
            margin-top: 0.5rem;
        }}
        
        .progress-fill {{
            height: 100%;
            border-radius: 4px;
            transition: width 0.3s ease;
        }}
        
        .red-flags {{
            background: rgba(239, 68, 68, 0.1);
            border-color: var(--danger);
        }}
        
        .red-flag-item {{
            display: flex;
            align-items: center;
            gap: 0.5rem;
            padding: 0.5rem 0;
            color: var(--danger);
        }}
        
        .executive-summary {{
            background: var(--bg-secondary);
            padding: 1.5rem;
            border-radius: 12px;
            margin-bottom: 2rem;
            border-left: 4px solid var(--accent);
        }}
        
        .recommendation {{
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            padding: 0.75rem 1.5rem;
            border-radius: 8px;
            font-weight: 600;
            margin-top: 1rem;
        }}
        
        .recommendation.buy {{
            background: rgba(34, 197, 94, 0.2);
            color: var(--success);
        }}
        
        .recommendation.hold {{
            background: rgba(234, 179, 8, 0.2);
            color: var(--warning);
        }}
        
        .recommendation.sell {{
            background: rgba(239, 68, 68, 0.2);
            color: var(--danger);
        }}
        
        footer {{
            text-align: center;
            padding: 2rem;
            color: var(--text-secondary);
            font-size: 0.875rem;
        }}
        
        @media (max-width: 768px) {{
            body {{
                padding: 1rem;
            }}
            
            .score-hero {{
                flex-direction: column;
                gap: 1rem;
            }}
            
            .score-circle {{
                width: 120px;
                height: 120px;
            }}
            
            .score-value {{
                font-size: 2rem;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <div class="logo">🔮</div>
            <h1>Oracle Analysis Report</h1>
            <div class="project-name">{html.escape(report.project_name)}</div>
            <div style="margin-top: 1rem; color: var(--text-secondary);">
                Generated: {report.generated_at}
            </div>
        </header>
        
        <div class="score-hero">
            <div class="score-circle">
                <div class="score-value">{report.risk.overall_score:.0f}</div>
                <div class="score-label">Overall Score</div>
            </div>
            <div>
                <div class="risk-badge">{report.risk.risk_level.upper()} RISK</div>
                {self._recommendation_html(report.risk.investment_recommendation)}
            </div>
        </div>
        
        <div class="executive-summary">
            <h3 style="margin-bottom: 1rem;">📋 Executive Summary</h3>
            <p>{html.escape(report.executive_summary)}</p>
        </div>
        
        {self._red_flags_html(report.risk.red_flags)}
        
        <div class="grid">
            {self._tokenomics_card_html(report.tokenomics)}
            {self._market_card_html(report.market)}
            {self._security_card_html(report.security)}
            {self._team_card_html(report.team)}
        </div>
        
        <div class="grid">
            {self._scores_card_html(report.risk)}
        </div>
        
        <footer>
            <p>🔮 Oracle Financial Intelligence System</p>
            <p>This report is for informational purposes only. Not financial advice.</p>
            <p>Report ID: {report.report_id}</p>
        </footer>
    </div>
</body>
</html>"""
        
        # Save file
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(html_content)
        
        logger.info(f"HTML report generated: {filepath}")
        return str(filepath)
    
    def _recommendation_html(self, rec: str) -> str:
        """Generate recommendation badge HTML"""
        rec_class = "hold"
        emoji = "⏸️"
        
        if rec in ["strong_buy", "buy"]:
            rec_class = "buy"
            emoji = "✅"
        elif rec in ["avoid", "sell"]:
            rec_class = "sell"
            emoji = "❌"
        
        return f'<div class="recommendation {rec_class}">{emoji} {rec.upper().replace("_", " ")}</div>'
    
    def _red_flags_html(self, flags: List[str]) -> str:
        """Generate red flags section HTML"""
        if not flags:
            return ""
        
        items = "\n".join([
            f'<div class="red-flag-item">⚠️ {html.escape(flag)}</div>'
            for flag in flags
        ])
        
        return f"""
        <div class="card red-flags" style="margin-bottom: 2rem;">
            <div class="card-title">🚨 Red Flags ({len(flags)})</div>
            {items}
        </div>
        """
    
    def _tokenomics_card_html(self, t: TokenomicsData) -> str:
        """Generate tokenomics card HTML"""
        return f"""
        <div class="card">
            <div class="card-title">💰 Tokenomics</div>
            <div class="metric">
                <span class="metric-label">Total Supply</span>
                <span class="metric-value">{self._format_number(t.total_supply)}</span>
            </div>
            <div class="metric">
                <span class="metric-label">Team Allocation</span>
                <span class="metric-value">{t.team_allocation_pct:.1f}%</span>
            </div>
            <div class="metric">
                <span class="metric-label">Community Allocation</span>
                <span class="metric-value">{t.community_allocation_pct:.1f}%</span>
            </div>
            <div class="metric">
                <span class="metric-label">Vesting Period</span>
                <span class="metric-value">{t.vesting_period_months} months</span>
            </div>
            <div class="metric">
                <span class="metric-label">Burn Mechanism</span>
                <span class="metric-value">{"✅" if t.burn_mechanism else "❌"}</span>
            </div>
            <div class="metric">
                <span class="metric-label">Distribution Score</span>
                <span class="metric-value">{t.distribution_score:.0f}/100</span>
            </div>
            <div class="progress-bar">
                <div class="progress-fill" style="width: {t.distribution_score}%; background: {self._get_score_color(t.distribution_score)};"></div>
            </div>
        </div>
        """
    
    def _market_card_html(self, m: MarketData) -> str:
        """Generate market card HTML"""
        change_class = "positive" if m.price_change_24h_pct >= 0 else "negative"
        
        return f"""
        <div class="card">
            <div class="card-title">📊 Market Data</div>
            <div class="metric">
                <span class="metric-label">Price</span>
                <span class="metric-value">${m.price_usd:,.4f}</span>
            </div>
            <div class="metric">
                <span class="metric-label">Market Cap</span>
                <span class="metric-value">${self._format_number(m.market_cap_usd)}</span>
            </div>
            <div class="metric">
                <span class="metric-label">24h Volume</span>
                <span class="metric-value">${self._format_number(m.volume_24h_usd)}</span>
            </div>
            <div class="metric">
                <span class="metric-label">24h Change</span>
                <span class="metric-value {change_class}">{m.price_change_24h_pct:+.2f}%</span>
            </div>
            <div class="metric">
                <span class="metric-label">30d Volatility</span>
                <span class="metric-value">{m.volatility_30d:.1f}%</span>
            </div>
            <div class="metric">
                <span class="metric-label">BTC Correlation</span>
                <span class="metric-value">{m.btc_correlation_30d:.2f}</span>
            </div>
            <div class="metric">
                <span class="metric-label">Liquidity Score</span>
                <span class="metric-value">{m.liquidity_score:.0f}/100</span>
            </div>
        </div>
        """
    
    def _security_card_html(self, s: SecurityData) -> str:
        """Generate security card HTML"""
        return f"""
        <div class="card">
            <div class="card-title">🔒 Security</div>
            <div class="metric">
                <span class="metric-label">Contract Verified</span>
                <span class="metric-value">{"✅" if s.contract_verified else "❌"}</span>
            </div>
            <div class="metric">
                <span class="metric-label">Audit Count</span>
                <span class="metric-value">{s.audit_count}</span>
            </div>
            <div class="metric">
                <span class="metric-label">Critical Issues</span>
                <span class="metric-value {"negative" if s.critical_issues > 0 else ""}">{s.critical_issues}</span>
            </div>
            <div class="metric">
                <span class="metric-label">Reentrancy Guard</span>
                <span class="metric-value">{"✅" if s.has_reentrancy_guard else "❌"}</span>
            </div>
            <div class="metric">
                <span class="metric-label">Mint Function</span>
                <span class="metric-value">{"⚠️" if s.has_mint_function else "✅"}</span>
            </div>
            <div class="metric">
                <span class="metric-label">Blacklist</span>
                <span class="metric-value">{"⚠️" if s.has_blacklist else "✅"}</span>
            </div>
            <div class="metric">
                <span class="metric-label">Security Score</span>
                <span class="metric-value">{s.security_score:.0f}/100</span>
            </div>
            <div class="progress-bar">
                <div class="progress-fill" style="width: {s.security_score}%; background: {self._get_score_color(s.security_score)};"></div>
            </div>
        </div>
        """
    
    def _team_card_html(self, t: TeamData) -> str:
        """Generate team card HTML"""
        return f"""
        <div class="card">
            <div class="card-title">👥 Team</div>
            <div class="metric">
                <span class="metric-label">Team Public</span>
                <span class="metric-value">{"✅" if t.team_public else "❌"}</span>
            </div>
            <div class="metric">
                <span class="metric-label">Team Size</span>
                <span class="metric-value">{t.team_size}</span>
            </div>
            <div class="metric">
                <span class="metric-label">GitHub Commits (30d)</span>
                <span class="metric-value">{t.github_commits_30d}</span>
            </div>
            <div class="metric">
                <span class="metric-label">Governance</span>
                <span class="metric-value">{t.governance_type or "N/A"}</span>
            </div>
            <div class="metric">
                <span class="metric-label">Social Followers</span>
                <span class="metric-value">{self._format_number(t.social_followers)}</span>
            </div>
            <div class="metric">
                <span class="metric-label">Team Score</span>
                <span class="metric-value">{t.team_score:.0f}/100</span>
            </div>
            <div class="progress-bar">
                <div class="progress-fill" style="width: {t.team_score}%; background: {self._get_score_color(t.team_score)};"></div>
            </div>
        </div>
        """
    
    def _scores_card_html(self, r: RiskMetrics) -> str:
        """Generate risk scores breakdown HTML"""
        scores = [
            ("Tokenomics", r.tokenomics_score, 25),
            ("Market", r.market_score, 20),
            ("Security", r.security_score, 30),
            ("Team", r.team_score, 15),
            ("Liquidity", r.liquidity_score, 10),
        ]
        
        rows = ""
        for name, score, weight in scores:
            color = self._get_score_color(score)
            rows += f"""
            <div class="metric">
                <span class="metric-label">{name} ({weight}% weight)</span>
                <span class="metric-value" style="color: {color}">{score:.0f}/100</span>
            </div>
            <div class="progress-bar" style="margin-bottom: 1rem;">
                <div class="progress-fill" style="width: {score}%; background: {color};"></div>
            </div>
            """
        
        return f"""
        <div class="card" style="grid-column: 1 / -1;">
            <div class="card-title">📈 Score Breakdown</div>
            {rows}
            <div class="metric" style="margin-top: 1rem; border-top: 2px solid var(--border); padding-top: 1rem;">
                <span class="metric-label" style="font-weight: 600;">Overall Score</span>
                <span class="metric-value" style="font-size: 1.5rem; color: {self._get_score_color(r.overall_score)}">{r.overall_score:.0f}/100</span>
            </div>
        </div>
        """
    
    def _generate_json(self, report: OracleReport) -> str:
        """Generate JSON report"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"oracle_report_{report.project_name}_{timestamp}.json"
        filepath = Path(self.config.output_dir) / filename
        
        # Convert to dict
        data = {
            "report_id": report.report_id,
            "project_name": report.project_name,
            "project_path": report.project_path,
            "project_type": report.project_type,
            "generated_at": report.generated_at,
            "analysis_duration_seconds": report.analysis_duration_seconds,
            "executive_summary": report.executive_summary,
            "tokenomics": asdict(report.tokenomics),
            "market": asdict(report.market),
            "security": asdict(report.security),
            "team": asdict(report.team),
            "risk": asdict(report.risk),
        }
        
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, default=str)
        
        logger.info(f"JSON report generated: {filepath}")
        return str(filepath)
    
    def _generate_text(self, report: OracleReport) -> str:
        """Generate plain text report"""
        lines = [
            "=" * 60,
            f"🔮 ORACLE ANALYSIS REPORT",
            "=" * 60,
            f"Project: {report.project_name}",
            f"Generated: {report.generated_at}",
            f"Report ID: {report.report_id}",
            "",
            "=" * 60,
            "OVERALL ASSESSMENT",
            "=" * 60,
            f"Overall Score: {report.risk.overall_score:.0f}/100",
            f"Risk Level: {report.risk.risk_level.upper()}",
            f"Recommendation: {report.risk.investment_recommendation.upper()}",
            "",
            "EXECUTIVE SUMMARY:",
            report.executive_summary,
            "",
        ]
        
        if report.risk.red_flags:
            lines.extend([
                "=" * 60,
                f"🚨 RED FLAGS ({len(report.risk.red_flags)})",
                "=" * 60,
            ])
            for flag in report.risk.red_flags:
                lines.append(f"  ⚠️ {flag}")
            lines.append("")
        
        lines.extend([
            "=" * 60,
            "SCORES BREAKDOWN",
            "=" * 60,
            f"  Tokenomics (25%): {report.risk.tokenomics_score:.0f}/100",
            f"  Market (20%):     {report.risk.market_score:.0f}/100",
            f"  Security (30%):   {report.risk.security_score:.0f}/100",
            f"  Team (15%):       {report.risk.team_score:.0f}/100",
            f"  Liquidity (10%):  {report.risk.liquidity_score:.0f}/100",
            "",
            "=" * 60,
            "TOKENOMICS",
            "=" * 60,
            f"  Total Supply: {self._format_number(report.tokenomics.total_supply)}",
            f"  Team Allocation: {report.tokenomics.team_allocation_pct:.1f}%",
            f"  Vesting: {report.tokenomics.vesting_period_months} months",
            f"  Burn Mechanism: {'Yes' if report.tokenomics.burn_mechanism else 'No'}",
            "",
            "=" * 60,
            "MARKET DATA",
            "=" * 60,
            f"  Price: ${report.market.price_usd:,.4f}",
            f"  Market Cap: ${self._format_number(report.market.market_cap_usd)}",
            f"  24h Volume: ${self._format_number(report.market.volume_24h_usd)}",
            f"  30d Volatility: {report.market.volatility_30d:.1f}%",
            "",
            "=" * 60,
            "SECURITY",
            "=" * 60,
            f"  Contract Verified: {'Yes' if report.security.contract_verified else 'No'}",
            f"  Audit Count: {report.security.audit_count}",
            f"  Critical Issues: {report.security.critical_issues}",
            f"  Security Score: {report.security.security_score:.0f}/100",
            "",
            "=" * 60,
            "DISCLAIMER",
            "=" * 60,
            "This report is for informational purposes only.",
            "Not financial advice. DYOR.",
            "=" * 60,
        ])
        
        content = "\n".join(lines)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"oracle_report_{report.project_name}_{timestamp}.txt"
        filepath = Path(self.config.output_dir) / filename
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        
        logger.info(f"Text report generated: {filepath}")
        return str(filepath)
    
    def _generate_markdown(self, report: OracleReport) -> str:
        """Generate Markdown report"""
        md = f"""# 🔮 Oracle Analysis Report

## {report.project_name}

**Generated:** {report.generated_at}  
**Report ID:** `{report.report_id}`

---

## 📊 Overall Assessment

| Metric | Value |
|--------|-------|
| **Overall Score** | **{report.risk.overall_score:.0f}/100** |
| **Risk Level** | {report.risk.risk_level.upper()} |
| **Recommendation** | {report.risk.investment_recommendation.upper()} |

### Executive Summary

{report.executive_summary}

"""
        
        if report.risk.red_flags:
            md += f"""
## 🚨 Red Flags ({len(report.risk.red_flags)})

"""
            for flag in report.risk.red_flags:
                md += f"- ⚠️ {flag}\n"
        
        md += f"""

## 📈 Score Breakdown

| Category | Score | Weight |
|----------|-------|--------|
| Tokenomics | {report.risk.tokenomics_score:.0f}/100 | 25% |
| Market | {report.risk.market_score:.0f}/100 | 20% |
| Security | {report.risk.security_score:.0f}/100 | 30% |
| Team | {report.risk.team_score:.0f}/100 | 15% |
| Liquidity | {report.risk.liquidity_score:.0f}/100 | 10% |

## 💰 Tokenomics

| Metric | Value |
|--------|-------|
| Total Supply | {self._format_number(report.tokenomics.total_supply)} |
| Team Allocation | {report.tokenomics.team_allocation_pct:.1f}% |
| Community Allocation | {report.tokenomics.community_allocation_pct:.1f}% |
| Vesting Period | {report.tokenomics.vesting_period_months} months |
| Burn Mechanism | {'✅' if report.tokenomics.burn_mechanism else '❌'} |

## 📊 Market Data

| Metric | Value |
|--------|-------|
| Price | ${report.market.price_usd:,.4f} |
| Market Cap | ${self._format_number(report.market.market_cap_usd)} |
| 24h Volume | ${self._format_number(report.market.volume_24h_usd)} |
| 24h Change | {report.market.price_change_24h_pct:+.2f}% |
| 30d Volatility | {report.market.volatility_30d:.1f}% |
| BTC Correlation | {report.market.btc_correlation_30d:.2f} |

## 🔒 Security

| Metric | Value |
|--------|-------|
| Contract Verified | {'✅' if report.security.contract_verified else '❌'} |
| Audit Count | {report.security.audit_count} |
| Critical Issues | {report.security.critical_issues} |
| Reentrancy Guard | {'✅' if report.security.has_reentrancy_guard else '❌'} |
| Security Score | {report.security.security_score:.0f}/100 |

## 👥 Team

| Metric | Value |
|--------|-------|
| Team Public | {'✅' if report.team.team_public else '❌'} |
| Team Size | {report.team.team_size} |
| GitHub Commits (30d) | {report.team.github_commits_30d} |
| Social Followers | {self._format_number(report.team.social_followers)} |

---

*This report is for informational purposes only. Not financial advice.*

*🔮 Oracle Financial Intelligence System*
"""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"oracle_report_{report.project_name}_{timestamp}.md"
        filepath = Path(self.config.output_dir) / filename
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(md)
        
        logger.info(f"Markdown report generated: {filepath}")
        return str(filepath)
    
    def _get_score_color(self, score: float) -> str:
        """Get color for score value"""
        if score >= 80:
            return self.SCORE_COLORS["excellent"]
        elif score >= 60:
            return self.SCORE_COLORS["good"]
        elif score >= 40:
            return self.SCORE_COLORS["fair"]
        elif score >= 20:
            return self.SCORE_COLORS["poor"]
        else:
            return self.SCORE_COLORS["critical"]
    
    def _format_number(self, n: float) -> str:
        """Format large numbers"""
        if n >= 1_000_000_000:
            return f"{n/1_000_000_000:.2f}B"
        elif n >= 1_000_000:
            return f"{n/1_000_000:.2f}M"
        elif n >= 1_000:
            return f"{n/1_000:.2f}K"
        else:
            return f"{n:,.0f}"


async def test():
    """Test report generator"""
    from oracle.core import Oracle
    
    # Create mock report
    report = OracleReport(
        project_name="TestToken",
        project_path="/test/path",
        project_type="defi",
    )
    
    # Set mock data
    report.tokenomics.total_supply = 100_000_000
    report.tokenomics.team_allocation_pct = 15
    report.tokenomics.community_allocation_pct = 40
    report.tokenomics.vesting_period_months = 24
    report.tokenomics.burn_mechanism = True
    report.tokenomics.distribution_score = 75
    
    report.market.price_usd = 0.5432
    report.market.market_cap_usd = 54_320_000
    report.market.volume_24h_usd = 5_432_000
    report.market.price_change_24h_pct = 5.67
    report.market.volatility_30d = 85.5
    report.market.btc_correlation_30d = 0.72
    report.market.liquidity_score = 65
    
    report.security.contract_verified = True
    report.security.audit_count = 2
    report.security.critical_issues = 0
    report.security.has_reentrancy_guard = True
    report.security.security_score = 82
    
    report.team.team_public = True
    report.team.team_size = 12
    report.team.github_commits_30d = 156
    report.team.social_followers = 25000
    report.team.team_score = 70
    
    report.risk.overall_score = 72
    report.risk.risk_level = "medium"
    report.risk.investment_recommendation = "hold"
    report.risk.tokenomics_score = 75
    report.risk.market_score = 65
    report.risk.security_score = 82
    report.risk.team_score = 70
    report.risk.liquidity_score = 60
    report.risk.red_flags = ["No cliff period for team tokens"]
    
    report.executive_summary = "TestToken is a DeFi protocol with solid tokenomics and security. The team is public and active on GitHub. Market metrics show healthy trading volume. One concern is the lack of cliff period for team tokens."
    
    # Generate reports
    generator = ReportGenerator(ReportConfig(output_dir="./test_reports"))
    
    html_path = generator.generate(report, format="html")
    print(f"HTML Report: {html_path}")
    
    json_path = generator.generate(report, format="json")
    print(f"JSON Report: {json_path}")
    
    md_path = generator.generate(report, format="markdown")
    print(f"Markdown Report: {md_path}")
    
    text_path = generator.generate(report, format="text")
    print(f"Text Report: {text_path}")


if __name__ == "__main__":
    import asyncio
    asyncio.run(test())
