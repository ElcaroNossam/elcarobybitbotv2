"""
Oracle Tokenomics Analyzer
==========================

Analyzes token economics from:
- Whitepaper/documentation
- Smart contract code
- On-chain data
- Configuration files

Extracts:
- Token distribution
- Vesting schedules
- Inflation/deflation mechanisms
- Utility metrics
"""

import re
import json
import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass

from oracle.core import TokenomicsData

logger = logging.getLogger("oracle.tokenomics")


class TokenomicsAnalyzer:
    """
    Tokenomics Analysis Engine
    
    Extracts and scores token economic models from project data.
    """
    
    # Regex patterns for extracting tokenomics data
    PATTERNS = {
        "total_supply": [
            r"total\s*supply[:\s]*(\d+[\d,\.]*)\s*(million|billion|M|B)?",
            r"(\d+[\d,\.]*)\s*(million|billion|M|B)?\s*tokens?\s*(total|max)",
            r"max\s*supply[:\s]*(\d+[\d,\.]*)",
        ],
        "team_allocation": [
            r"team[:\s]*(\d+(?:\.\d+)?)\s*%",
            r"(\d+(?:\.\d+)?)\s*%\s*(?:for\s*)?team",
            r"team\s*allocation[:\s]*(\d+(?:\.\d+)?)\s*%",
        ],
        "investor_allocation": [
            r"investor[s]?[:\s]*(\d+(?:\.\d+)?)\s*%",
            r"private\s*sale[:\s]*(\d+(?:\.\d+)?)\s*%",
            r"seed[:\s]*(\d+(?:\.\d+)?)\s*%",
        ],
        "community_allocation": [
            r"community[:\s]*(\d+(?:\.\d+)?)\s*%",
            r"airdrop[:\s]*(\d+(?:\.\d+)?)\s*%",
            r"public\s*sale[:\s]*(\d+(?:\.\d+)?)\s*%",
        ],
        "treasury_allocation": [
            r"treasury[:\s]*(\d+(?:\.\d+)?)\s*%",
            r"ecosystem[:\s]*(\d+(?:\.\d+)?)\s*%",
            r"development[:\s]*(\d+(?:\.\d+)?)\s*%",
        ],
        "liquidity_allocation": [
            r"liquidity[:\s]*(\d+(?:\.\d+)?)\s*%",
            r"dex\s*liquidity[:\s]*(\d+(?:\.\d+)?)\s*%",
        ],
        "vesting_period": [
            r"vesting[:\s]*(\d+)\s*(months?|years?)",
            r"(\d+)\s*(months?|years?)\s*vesting",
            r"linear\s*vesting[:\s]*(\d+)\s*(months?|years?)",
        ],
        "cliff_period": [
            r"cliff[:\s]*(\d+)\s*(months?|years?)",
            r"(\d+)\s*(months?|years?)\s*cliff",
        ],
    }
    
    # Solidity patterns
    SOLIDITY_PATTERNS = {
        "burn": [
            r"function\s+burn\s*\(",
            r"_burn\s*\(",
            r"event\s+Burn\s*\(",
        ],
        "mint": [
            r"function\s+mint\s*\(",
            r"_mint\s*\(",
            r"function\s+_mint\s*\(",
        ],
        "total_supply": [
            r"totalSupply\s*=\s*(\d+)\s*\*\s*10\s*\*\*\s*(\d+)",
            r"uint256.*totalSupply\s*=\s*(\d+)",
            r"_totalSupply\s*=\s*(\d+)",
        ],
        "staking_rewards": [
            r"stakingReward[s]?",
            r"rewardRate",
            r"function\s+stake\s*\(",
        ],
    }
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
    
    async def analyze(
        self,
        project_data: Dict[str, Any],
        token_name: Optional[str] = None
    ) -> TokenomicsData:
        """
        Analyze tokenomics from project data.
        
        Args:
            project_data: Scanned project data from Oracle core
            token_name: Token name for API lookups
        
        Returns:
            TokenomicsData with extracted metrics
        """
        tokenomics = TokenomicsData()
        
        # Collect all text content
        all_text = self._collect_text(project_data)
        
        # Collect all Solidity code
        solidity_code = self._collect_solidity(project_data)
        
        # Extract from documentation
        doc_data = self._extract_from_docs(all_text)
        
        # Extract from smart contracts
        contract_data = self._extract_from_contracts(solidity_code)
        
        # Merge data (contract data takes precedence)
        tokenomics = self._merge_data(tokenomics, doc_data, contract_data)
        
        # Analyze tokenomics files specifically
        for tf in project_data.get("tokenomics_files", []):
            specific_data = self._analyze_tokenomics_file(tf.get("content", ""))
            tokenomics = self._merge_data(tokenomics, {}, specific_data)
        
        # Calculate scores
        tokenomics.distribution_score = self._score_distribution(tokenomics)
        tokenomics.vesting_score = self._score_vesting(tokenomics)
        tokenomics.sustainability_score = self._score_sustainability(tokenomics)
        
        logger.info(f"Tokenomics analysis complete. Distribution score: {tokenomics.distribution_score:.0f}")
        
        return tokenomics
    
    def _collect_text(self, project_data: Dict) -> str:
        """Collect all text content from project"""
        texts = [project_data.get("readme_content", "")]
        
        for doc in project_data.get("documentation", []):
            texts.append(doc.get("content", ""))
        
        for tf in project_data.get("tokenomics_files", []):
            texts.append(tf.get("content", ""))
        
        return "\n".join(texts)
    
    def _collect_solidity(self, project_data: Dict) -> str:
        """Collect all Solidity code"""
        codes = []
        for contract in project_data.get("smart_contracts", []):
            codes.append(contract.get("content", ""))
        return "\n".join(codes)
    
    def _extract_from_docs(self, text: str) -> Dict[str, Any]:
        """Extract tokenomics data from documentation"""
        data = {}
        text_lower = text.lower()
        
        # Extract each metric
        for metric, patterns in self.PATTERNS.items():
            for pattern in patterns:
                match = re.search(pattern, text_lower, re.IGNORECASE)
                if match:
                    value = match.group(1).replace(",", "")
                    try:
                        data[metric] = float(value)
                        
                        # Handle multipliers (million, billion)
                        if metric == "total_supply" and len(match.groups()) > 1:
                            multiplier = match.group(2)
                            if multiplier:
                                multiplier = multiplier.lower()
                                if multiplier in ["million", "m"]:
                                    data[metric] *= 1_000_000
                                elif multiplier in ["billion", "b"]:
                                    data[metric] *= 1_000_000_000
                        
                        # Handle time units for vesting
                        if metric in ["vesting_period", "cliff_period"] and len(match.groups()) > 1:
                            unit = match.group(2)
                            if unit and "year" in unit.lower():
                                data[metric] *= 12  # Convert years to months
                        
                        break
                    except ValueError:
                        continue
        
        return data
    
    def _extract_from_contracts(self, code: str) -> Dict[str, Any]:
        """Extract tokenomics data from Solidity code"""
        data = {
            "burn_mechanism": False,
            "has_mint": False,
            "has_staking": False,
        }
        
        if not code:
            return data
        
        # Check for burn mechanism
        for pattern in self.SOLIDITY_PATTERNS["burn"]:
            if re.search(pattern, code, re.IGNORECASE):
                data["burn_mechanism"] = True
                break
        
        # Check for mint function
        for pattern in self.SOLIDITY_PATTERNS["mint"]:
            if re.search(pattern, code, re.IGNORECASE):
                data["has_mint"] = True
                break
        
        # Check for staking
        for pattern in self.SOLIDITY_PATTERNS["staking_rewards"]:
            if re.search(pattern, code, re.IGNORECASE):
                data["has_staking"] = True
                break
        
        # Try to extract total supply from code
        for pattern in self.SOLIDITY_PATTERNS["total_supply"]:
            match = re.search(pattern, code)
            if match:
                try:
                    if len(match.groups()) == 2:
                        # Pattern like: 1000000 * 10 ** 18
                        base = int(match.group(1))
                        decimals = int(match.group(2))
                        data["total_supply"] = base  # Store without decimals
                    else:
                        data["total_supply"] = int(match.group(1))
                    break
                except ValueError:
                    continue
        
        return data
    
    def _analyze_tokenomics_file(self, content: str) -> Dict[str, Any]:
        """Deep analysis of tokenomics-specific file"""
        data = {}
        
        # Try to parse as JSON first
        try:
            json_data = json.loads(content)
            if isinstance(json_data, dict):
                # Direct mapping for common fields
                mappings = {
                    "totalSupply": "total_supply",
                    "total_supply": "total_supply",
                    "maxSupply": "max_supply",
                    "teamAllocation": "team_allocation_pct",
                    "team": "team_allocation_pct",
                    "investorAllocation": "investor_allocation_pct",
                    "communityAllocation": "community_allocation_pct",
                    "vestingMonths": "vesting_period_months",
                    "cliffMonths": "cliff_months",
                }
                for json_key, our_key in mappings.items():
                    if json_key in json_data:
                        data[our_key] = json_data[json_key]
                return data
        except json.JSONDecodeError:
            pass
        
        # Fall back to text parsing
        return self._extract_from_docs(content)
    
    def _merge_data(
        self,
        base: TokenomicsData,
        doc_data: Dict,
        contract_data: Dict
    ) -> TokenomicsData:
        """Merge extracted data into TokenomicsData"""
        # Apply doc data
        if "total_supply" in doc_data:
            base.total_supply = doc_data["total_supply"]
        if "team_allocation" in doc_data:
            base.team_allocation_pct = doc_data["team_allocation"]
        if "investor_allocation" in doc_data:
            base.investor_allocation_pct = doc_data["investor_allocation"]
        if "community_allocation" in doc_data:
            base.community_allocation_pct = doc_data["community_allocation"]
        if "treasury_allocation" in doc_data:
            base.treasury_allocation_pct = doc_data["treasury_allocation"]
        if "liquidity_allocation" in doc_data:
            base.liquidity_allocation_pct = doc_data["liquidity_allocation"]
        if "vesting_period" in doc_data:
            base.vesting_period_months = int(doc_data["vesting_period"])
        if "cliff_period" in doc_data:
            base.cliff_months = int(doc_data["cliff_period"])
        
        # Apply contract data (overrides)
        if contract_data.get("burn_mechanism"):
            base.burn_mechanism = True
        if contract_data.get("total_supply"):
            base.total_supply = contract_data["total_supply"]
        if contract_data.get("has_staking"):
            base.staking_rewards_pct = 5.0  # Assume some staking rewards if detected
        
        return base
    
    def _score_distribution(self, t: TokenomicsData) -> float:
        """Score token distribution (0-100)"""
        score = 50.0
        
        # Team allocation (lower is better)
        if t.team_allocation_pct <= 10:
            score += 25
        elif t.team_allocation_pct <= 15:
            score += 15
        elif t.team_allocation_pct <= 20:
            score += 5
        elif t.team_allocation_pct > 30:
            score -= 20
        elif t.team_allocation_pct > 40:
            score -= 35
        
        # Community allocation (higher is better)
        if t.community_allocation_pct >= 40:
            score += 20
        elif t.community_allocation_pct >= 25:
            score += 10
        elif t.community_allocation_pct < 10:
            score -= 10
        
        # Check if allocations sum to ~100%
        total = (
            t.team_allocation_pct +
            t.investor_allocation_pct +
            t.community_allocation_pct +
            t.treasury_allocation_pct +
            t.liquidity_allocation_pct
        )
        if 95 <= total <= 105:
            score += 5  # Well-documented
        
        return max(0, min(100, score))
    
    def _score_vesting(self, t: TokenomicsData) -> float:
        """Score vesting schedule (0-100)"""
        score = 30.0  # Low base if no vesting
        
        # Vesting period
        if t.vesting_period_months >= 48:
            score += 40
        elif t.vesting_period_months >= 36:
            score += 35
        elif t.vesting_period_months >= 24:
            score += 25
        elif t.vesting_period_months >= 12:
            score += 15
        elif t.vesting_period_months >= 6:
            score += 5
        
        # Cliff period
        if t.cliff_months >= 12:
            score += 20
        elif t.cliff_months >= 6:
            score += 10
        elif t.cliff_months >= 3:
            score += 5
        
        return max(0, min(100, score))
    
    def _score_sustainability(self, t: TokenomicsData) -> float:
        """Score long-term sustainability (0-100)"""
        score = 50.0
        
        # Deflationary mechanisms
        if t.burn_mechanism:
            score += 15
        
        # Inflation control
        if t.inflation_rate_annual_pct == 0:
            score += 10  # Fixed supply
        elif t.inflation_rate_annual_pct <= 5:
            score += 5
        elif t.inflation_rate_annual_pct > 20:
            score -= 20
        elif t.inflation_rate_annual_pct > 10:
            score -= 10
        
        # Max supply defined
        if t.max_supply and t.max_supply > 0:
            score += 10
        
        # Staking rewards (balanced)
        if 3 <= t.staking_rewards_pct <= 10:
            score += 10
        elif t.staking_rewards_pct > 30:
            score -= 15  # Too inflationary
        
        # Liquidity provision
        if t.liquidity_allocation_pct >= 10:
            score += 5
        
        return max(0, min(100, score))


async def test():
    """Test tokenomics analyzer"""
    analyzer = TokenomicsAnalyzer()
    
    # Mock project data
    project_data = {
        "readme_content": """
        # Test Token
        
        ## Tokenomics
        - Total Supply: 100 million tokens
        - Team: 15%
        - Community: 40%
        - Treasury: 20%
        - Liquidity: 10%
        - Investors: 15%
        
        Vesting: 24 months with 6 month cliff
        """,
        "smart_contracts": [{
            "content": """
            contract Token is ERC20 {
                uint256 public totalSupply = 100000000 * 10 ** 18;
                
                function burn(uint256 amount) external {
                    _burn(msg.sender, amount);
                }
            }
            """
        }],
        "documentation": [],
        "tokenomics_files": []
    }
    
    result = await analyzer.analyze(project_data, "TEST")
    print(f"Total Supply: {result.total_supply}")
    print(f"Team Allocation: {result.team_allocation_pct}%")
    print(f"Vesting: {result.vesting_period_months} months")
    print(f"Burn Mechanism: {result.burn_mechanism}")
    print(f"Distribution Score: {result.distribution_score}")
    print(f"Vesting Score: {result.vesting_score}")


if __name__ == "__main__":
    import asyncio
    asyncio.run(test())
