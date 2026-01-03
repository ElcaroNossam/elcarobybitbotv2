"""
Oracle Smart Contract Auditor
=============================

Automated security analysis for smart contracts:
- Vulnerability detection
- Gas optimization suggestions
- Access control analysis
- Reentrancy checks
- Common exploit patterns

Supports:
- Solidity (.sol)
- Vyper (.vy)
- Move (.move)
"""

import re
import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum

from oracle.core import SecurityData

logger = logging.getLogger("oracle.auditor")


class Severity(Enum):
    """Vulnerability severity levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "informational"


@dataclass
class Vulnerability:
    """Detected vulnerability"""
    title: str
    severity: Severity
    description: str
    location: str = ""  # File:line
    recommendation: str = ""
    cwe_id: Optional[str] = None  # Common Weakness Enumeration


@dataclass
class AuditResult:
    """Complete audit result"""
    vulnerabilities: List[Vulnerability] = field(default_factory=list)
    critical_count: int = 0
    high_count: int = 0
    medium_count: int = 0
    low_count: int = 0
    info_count: int = 0
    
    # Security features detected
    has_ownable: bool = False
    has_pausable: bool = False
    has_reentrancy_guard: bool = False
    uses_safe_math: bool = False
    has_access_control: bool = False
    
    # Risky patterns detected
    has_selfdestruct: bool = False
    has_delegatecall: bool = False
    has_inline_assembly: bool = False
    has_tx_origin: bool = False
    
    # Scores
    security_score: float = 0.0
    code_quality_score: float = 0.0


class SmartContractAuditor:
    """
    Automated Smart Contract Security Auditor
    
    Performs static analysis on smart contract code to detect
    vulnerabilities and security issues.
    """
    
    # Vulnerability patterns for Solidity
    VULNERABILITY_PATTERNS = {
        # Reentrancy
        "reentrancy": {
            "patterns": [
                # External call before state change
                r"\.call\{.*value.*\}\s*\([^)]*\)[^;]*;[^}]*\w+\s*[=\-\+]",
                r"\.transfer\s*\([^)]*\)[^;]*;[^}]*\w+\s*[=\-\+]",
                r"\.send\s*\([^)]*\)[^;]*;[^}]*\w+\s*[=\-\+]",
            ],
            "severity": Severity.CRITICAL,
            "title": "Potential Reentrancy Vulnerability",
            "description": "External call is made before state variable is updated. This can allow an attacker to re-enter the function.",
            "recommendation": "Follow the checks-effects-interactions pattern. Update state variables before making external calls.",
            "cwe": "CWE-841"
        },
        
        # Unchecked external call
        "unchecked_call": {
            "patterns": [
                r"\.call\{.*\}\s*\([^)]*\)\s*;(?!\s*require|\s*if|\s*assert)",
                r"\.send\s*\([^)]*\)\s*;(?!\s*require|\s*if|\s*assert)",
            ],
            "severity": Severity.HIGH,
            "title": "Unchecked External Call Return Value",
            "description": "The return value of an external call is not checked. This can lead to silent failures.",
            "recommendation": "Always check the return value of external calls and handle failures appropriately.",
            "cwe": "CWE-252"
        },
        
        # Integer overflow/underflow (pre-Solidity 0.8)
        "integer_overflow": {
            "patterns": [
                r"pragma\s+solidity\s+[\^<>=]*0\.[0-7]\.\d+",
            ],
            "severity": Severity.HIGH,
            "title": "Potential Integer Overflow/Underflow",
            "description": "Contract uses Solidity version <0.8.0 without SafeMath. Integer operations can overflow.",
            "recommendation": "Upgrade to Solidity 0.8+ or use OpenZeppelin's SafeMath library.",
            "cwe": "CWE-190"
        },
        
        # tx.origin authentication
        "tx_origin": {
            "patterns": [
                r"tx\.origin\s*[=!]=",
                r"require\s*\([^)]*tx\.origin",
                r"if\s*\([^)]*tx\.origin",
            ],
            "severity": Severity.HIGH,
            "title": "tx.origin Used for Authentication",
            "description": "Using tx.origin for authorization is vulnerable to phishing attacks.",
            "recommendation": "Use msg.sender instead of tx.origin for authentication.",
            "cwe": "CWE-284"
        },
        
        # Delegatecall to user input
        "dangerous_delegatecall": {
            "patterns": [
                r"\.delegatecall\s*\(",
            ],
            "severity": Severity.HIGH,
            "title": "Dangerous delegatecall Usage",
            "description": "delegatecall executes code in the context of the calling contract. If the target is user-controlled, this can be exploited.",
            "recommendation": "Ensure delegatecall targets are trusted and not user-controlled.",
            "cwe": "CWE-829"
        },
        
        # Selfdestruct
        "selfdestruct": {
            "patterns": [
                r"\bselfdestruct\s*\(",
                r"\bsuicide\s*\(",
            ],
            "severity": Severity.MEDIUM,
            "title": "Selfdestruct Present",
            "description": "Contract can be destroyed. Ensure only authorized addresses can trigger this.",
            "recommendation": "Implement proper access control for selfdestruct or remove if not needed.",
            "cwe": "CWE-284"
        },
        
        # Timestamp dependence
        "timestamp_dependence": {
            "patterns": [
                r"block\.timestamp\s*[<>=]",
                r"now\s*[<>=]",
            ],
            "severity": Severity.LOW,
            "title": "Timestamp Dependence",
            "description": "Block timestamp can be manipulated by miners within ~15 second range.",
            "recommendation": "Avoid using block.timestamp for critical logic. Use block numbers for time-based conditions.",
            "cwe": "CWE-367"
        },
        
        # Floating pragma
        "floating_pragma": {
            "patterns": [
                r"pragma\s+solidity\s+[\^~]",
            ],
            "severity": Severity.INFO,
            "title": "Floating Pragma",
            "description": "Contract uses a floating pragma. This can lead to deploying with an unintended compiler version.",
            "recommendation": "Lock the pragma to a specific version (e.g., pragma solidity 0.8.19;)",
            "cwe": None
        },
        
        # Missing zero address check
        "zero_address": {
            "patterns": [
                r"function\s+\w+\s*\([^)]*address[^)]*\)[^{]*\{(?![^}]*require\s*\([^)]*!=\s*address\(0\))",
            ],
            "severity": Severity.LOW,
            "title": "Missing Zero Address Validation",
            "description": "Function accepts address parameter without checking for zero address.",
            "recommendation": "Add require(addr != address(0)) checks for address parameters.",
            "cwe": "CWE-20"
        },
        
        # Public functions that should be external
        "public_not_external": {
            "patterns": [
                r"function\s+\w+\s*\([^)]*\)\s*public(?!\s*view|\s*pure)",
            ],
            "severity": Severity.INFO,
            "title": "Public Functions Could Be External",
            "description": "Functions not called internally should be marked as external for gas optimization.",
            "recommendation": "Change public to external for functions not called internally.",
            "cwe": None
        },
        
        # Unbounded loops
        "unbounded_loop": {
            "patterns": [
                r"for\s*\([^)]*\.length[^)]*\)",
                r"while\s*\([^)]*<\s*\w+\.length[^)]*\)",
            ],
            "severity": Severity.MEDIUM,
            "title": "Potentially Unbounded Loop",
            "description": "Loop iterates over array length which could grow unbounded, causing DoS.",
            "recommendation": "Implement pagination or limit array sizes to prevent gas exhaustion.",
            "cwe": "CWE-834"
        },
        
        # Hardcoded addresses
        "hardcoded_address": {
            "patterns": [
                r"0x[a-fA-F0-9]{40}",
            ],
            "severity": Severity.INFO,
            "title": "Hardcoded Address",
            "description": "Contract contains hardcoded addresses which reduces flexibility.",
            "recommendation": "Consider using constructor parameters or configuration functions.",
            "cwe": None
        },
        
        # Missing events
        "missing_events": {
            "patterns": [
                # State changes without events (simplified)
                r"function\s+set\w*\s*\([^)]*\)[^}]*\{[^}]*=\s*[^;]+;[^}]*\}(?![^}]*emit)",
            ],
            "severity": Severity.LOW,
            "title": "Missing Event Emission",
            "description": "State-changing functions should emit events for off-chain tracking.",
            "recommendation": "Add event emissions for all state changes.",
            "cwe": None
        },
    }
    
    # Security features to detect
    SECURITY_FEATURES = {
        "ownable": [
            r"import.*Ownable",
            r"contract\s+\w+\s+is\s+[^{]*Ownable",
            r"modifier\s+onlyOwner",
        ],
        "pausable": [
            r"import.*Pausable",
            r"contract\s+\w+\s+is\s+[^{]*Pausable",
            r"modifier\s+whenNotPaused",
        ],
        "reentrancy_guard": [
            r"import.*ReentrancyGuard",
            r"modifier\s+nonReentrant",
            r"reentrancy",
        ],
        "access_control": [
            r"import.*AccessControl",
            r"contract\s+\w+\s+is\s+[^{]*AccessControl",
            r"hasRole\s*\(",
        ],
        "safe_math": [
            r"import.*SafeMath",
            r"using\s+SafeMath\s+for",
        ],
    }
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
    
    async def audit(self, project_data: Dict[str, Any]) -> Tuple[SecurityData, AuditResult]:
        """
        Perform security audit on smart contracts.
        
        Args:
            project_data: Scanned project data containing smart contracts
        
        Returns:
            Tuple of (SecurityData, AuditResult)
        """
        security = SecurityData()
        result = AuditResult()
        
        contracts = project_data.get("smart_contracts", [])
        
        if not contracts:
            logger.info("No smart contracts found for audit")
            security.audit_count = 0
            return security, result
        
        logger.info(f"Auditing {len(contracts)} smart contracts")
        
        # Analyze each contract
        for contract in contracts:
            file_path = contract.get("path", "unknown")
            code = contract.get("content", "")
            
            if not code:
                continue
            
            # Detect vulnerabilities
            vulns = self._detect_vulnerabilities(code, file_path)
            result.vulnerabilities.extend(vulns)
            
            # Detect security features
            self._detect_security_features(code, result)
            
            # Check for risky patterns
            self._detect_risky_patterns(code, result)
        
        # Count by severity
        for vuln in result.vulnerabilities:
            if vuln.severity == Severity.CRITICAL:
                result.critical_count += 1
            elif vuln.severity == Severity.HIGH:
                result.high_count += 1
            elif vuln.severity == Severity.MEDIUM:
                result.medium_count += 1
            elif vuln.severity == Severity.LOW:
                result.low_count += 1
            else:
                result.info_count += 1
        
        # Calculate scores
        result.security_score = self._calculate_security_score(result)
        result.code_quality_score = self._calculate_quality_score(result)
        
        # Populate SecurityData
        security.contract_verified = True  # We have the source
        security.audit_count = 0  # Self-audit doesn't count
        security.critical_issues = result.critical_count
        security.high_issues = result.high_count
        security.medium_issues = result.medium_count
        security.has_reentrancy_guard = result.has_reentrancy_guard
        security.has_mint_function = self._check_mint_function(contracts)
        security.has_blacklist = self._check_blacklist(contracts)
        security.has_pause = result.has_pausable
        security.upgradeable = self._check_upgradeable(contracts)
        security.security_score = result.security_score
        
        logger.info(
            f"Audit complete: {result.critical_count} critical, "
            f"{result.high_count} high, {result.medium_count} medium issues"
        )
        
        return security, result
    
    def _detect_vulnerabilities(
        self,
        code: str,
        file_path: str
    ) -> List[Vulnerability]:
        """Detect vulnerabilities using pattern matching"""
        vulnerabilities = []
        
        for vuln_type, vuln_config in self.VULNERABILITY_PATTERNS.items():
            for pattern in vuln_config["patterns"]:
                matches = re.finditer(pattern, code, re.IGNORECASE | re.MULTILINE)
                
                for match in matches:
                    # Calculate line number
                    line_num = code[:match.start()].count('\n') + 1
                    
                    vuln = Vulnerability(
                        title=vuln_config["title"],
                        severity=vuln_config["severity"],
                        description=vuln_config["description"],
                        location=f"{file_path}:{line_num}",
                        recommendation=vuln_config["recommendation"],
                        cwe_id=vuln_config.get("cwe")
                    )
                    vulnerabilities.append(vuln)
        
        return vulnerabilities
    
    def _detect_security_features(self, code: str, result: AuditResult):
        """Detect security features in code"""
        for feature, patterns in self.SECURITY_FEATURES.items():
            for pattern in patterns:
                if re.search(pattern, code, re.IGNORECASE):
                    if feature == "ownable":
                        result.has_ownable = True
                    elif feature == "pausable":
                        result.has_pausable = True
                    elif feature == "reentrancy_guard":
                        result.has_reentrancy_guard = True
                    elif feature == "access_control":
                        result.has_access_control = True
                    elif feature == "safe_math":
                        result.uses_safe_math = True
                    break
    
    def _detect_risky_patterns(self, code: str, result: AuditResult):
        """Detect risky patterns"""
        if re.search(r"selfdestruct|suicide", code, re.IGNORECASE):
            result.has_selfdestruct = True
        
        if re.search(r"delegatecall", code, re.IGNORECASE):
            result.has_delegatecall = True
        
        if re.search(r"assembly\s*\{", code, re.IGNORECASE):
            result.has_inline_assembly = True
        
        if re.search(r"tx\.origin", code, re.IGNORECASE):
            result.has_tx_origin = True
    
    def _calculate_security_score(self, result: AuditResult) -> float:
        """Calculate overall security score (0-100)"""
        score = 100.0
        
        # Deduct for vulnerabilities
        score -= result.critical_count * 25
        score -= result.high_count * 15
        score -= result.medium_count * 8
        score -= result.low_count * 3
        score -= result.info_count * 1
        
        # Bonus for security features
        if result.has_ownable:
            score += 5
        if result.has_pausable:
            score += 5
        if result.has_reentrancy_guard:
            score += 10
        if result.has_access_control:
            score += 5
        if result.uses_safe_math:
            score += 5
        
        # Penalty for risky patterns
        if result.has_selfdestruct:
            score -= 10
        if result.has_delegatecall:
            score -= 5
        if result.has_tx_origin:
            score -= 15
        
        return max(0, min(100, score))
    
    def _calculate_quality_score(self, result: AuditResult) -> float:
        """Calculate code quality score (0-100)"""
        score = 70.0  # Base score
        
        # Security features improve quality
        if result.has_ownable:
            score += 5
        if result.has_pausable:
            score += 5
        if result.has_reentrancy_guard:
            score += 10
        if result.has_access_control:
            score += 5
        
        # Risky patterns reduce quality
        if result.has_selfdestruct:
            score -= 5
        if result.has_inline_assembly:
            score -= 5
        if result.has_delegatecall:
            score -= 5
        
        return max(0, min(100, score))
    
    def _check_mint_function(self, contracts: List[Dict]) -> bool:
        """Check if any contract has mint function"""
        for contract in contracts:
            code = contract.get("content", "")
            if re.search(r"function\s+mint\s*\(", code, re.IGNORECASE):
                return True
        return False
    
    def _check_blacklist(self, contracts: List[Dict]) -> bool:
        """Check if any contract has blacklist functionality"""
        for contract in contracts:
            code = contract.get("content", "")
            if re.search(r"blacklist|blocklist|banned|_isBlacklisted", code, re.IGNORECASE):
                return True
        return False
    
    def _check_upgradeable(self, contracts: List[Dict]) -> bool:
        """Check if contract is upgradeable"""
        for contract in contracts:
            code = contract.get("content", "")
            if re.search(
                r"Upgradeable|Proxy|UUPS|TransparentProxy|implementation",
                code,
                re.IGNORECASE
            ):
                return True
        return False


async def test():
    """Test smart contract auditor"""
    auditor = SmartContractAuditor()
    
    # Mock vulnerable contract
    project_data = {
        "smart_contracts": [{
            "path": "contracts/Token.sol",
            "content": """
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";

contract Token is Ownable, ReentrancyGuard {
    mapping(address => uint256) public balances;
    
    function withdraw() external {
        uint256 amount = balances[msg.sender];
        (bool success, ) = msg.sender.call{value: amount}("");
        require(success, "Transfer failed");
        balances[msg.sender] = 0;  // State update after external call!
    }
    
    function setOwner(address newOwner) public {
        // Missing zero address check
        transferOwnership(newOwner);
    }
    
    function processAll(address[] memory users) external {
        for (uint i = 0; i < users.length; i++) {
            // Unbounded loop
        }
    }
}
            """
        }]
    }
    
    security, result = await auditor.audit(project_data)
    
    print(f"\n=== AUDIT RESULTS ===")
    print(f"Security Score: {result.security_score:.0f}/100")
    print(f"Code Quality Score: {result.code_quality_score:.0f}/100")
    print(f"\nVulnerabilities Found: {len(result.vulnerabilities)}")
    print(f"  Critical: {result.critical_count}")
    print(f"  High: {result.high_count}")
    print(f"  Medium: {result.medium_count}")
    print(f"  Low: {result.low_count}")
    print(f"  Info: {result.info_count}")
    
    print(f"\nSecurity Features:")
    print(f"  Ownable: {result.has_ownable}")
    print(f"  Pausable: {result.has_pausable}")
    print(f"  ReentrancyGuard: {result.has_reentrancy_guard}")
    
    print(f"\nVulnerability Details:")
    for vuln in result.vulnerabilities[:5]:
        print(f"\n  [{vuln.severity.value.upper()}] {vuln.title}")
        print(f"    Location: {vuln.location}")
        print(f"    Description: {vuln.description[:100]}...")


if __name__ == "__main__":
    import asyncio
    asyncio.run(test())
