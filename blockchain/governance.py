"""
ELCARO Chain - DAO Governance System

Decentralized governance with on-chain voting.

Features:
- Proposal creation and voting
- Timelock execution
- Treasury management
- Parameter updates
- Emergency actions
"""

import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from decimal import Decimal
from enum import Enum
import time

logger = logging.getLogger(__name__)


# ------------------------------------------------------------------------------------
# Enums
# ------------------------------------------------------------------------------------

class ProposalType(Enum):
    PROTOCOL_UPGRADE = "protocol_upgrade"
    PARAMETER_CHANGE = "parameter_change"
    TREASURY_SPENDING = "treasury_spending"
    EMERGENCY_ACTION = "emergency_action"
    VALIDATOR_UPDATE = "validator_update"


class ProposalStatus(Enum):
    PENDING = "pending"
    ACTIVE = "active"
    SUCCEEDED = "succeeded"
    DEFEATED = "defeated"
    QUEUED = "queued"
    EXECUTED = "executed"
    CANCELLED = "cancelled"


class VoteOption(Enum):
    FOR = "for"
    AGAINST = "against"
    ABSTAIN = "abstain"


# ------------------------------------------------------------------------------------
# Data Structures
# ------------------------------------------------------------------------------------

@dataclass
class Proposal:
    """DAO governance proposal."""
    proposal_id: str
    proposer: str
    proposal_type: ProposalType
    title: str
    description: str
    targets: List[str]  # Contract addresses to call
    values: List[Decimal]  # ETH values to send
    calldatas: List[bytes]  # Function calls to execute
    
    # Voting parameters
    voting_start: int  # Unix timestamp
    voting_end: int    # Unix timestamp
    quorum: Decimal = Decimal("0.1")  # 10% of circulating supply
    
    # Vote counts
    votes_for: Decimal = Decimal(0)
    votes_against: Decimal = Decimal(0)
    votes_abstain: Decimal = Decimal(0)
    
    # Status
    status: ProposalStatus = ProposalStatus.PENDING
    execution_time: int = 0  # When proposal can be executed (after timelock)
    executed_at: int = 0
    
    created_at: int = field(default_factory=lambda: int(time.time()))
    
    @property
    def total_votes(self) -> Decimal:
        """Get total votes cast."""
        return self.votes_for + self.votes_against + self.votes_abstain
    
    @property
    def is_active(self) -> bool:
        """Check if voting is currently active."""
        now = int(time.time())
        return self.voting_start <= now < self.voting_end and self.status == ProposalStatus.ACTIVE
    
    @property
    def has_succeeded(self) -> bool:
        """Check if proposal has passed."""
        return self.votes_for > self.votes_against and self.total_votes >= self.quorum
    
    @property
    def can_execute(self) -> bool:
        """Check if proposal can be executed."""
        return (
            self.status == ProposalStatus.QUEUED
            and self.execution_time > 0
            and int(time.time()) >= self.execution_time
        )
    
    def to_dict(self) -> Dict:
        return {
            "proposal_id": self.proposal_id,
            "proposer": self.proposer,
            "type": self.proposal_type.value,
            "title": self.title,
            "description": self.description,
            "voting_start": self.voting_start,
            "voting_end": self.voting_end,
            "quorum": str(self.quorum),
            "votes_for": str(self.votes_for),
            "votes_against": str(self.votes_against),
            "votes_abstain": str(self.votes_abstain),
            "total_votes": str(self.total_votes),
            "status": self.status.value,
            "is_active": self.is_active,
            "has_succeeded": self.has_succeeded,
            "can_execute": self.can_execute,
            "execution_time": self.execution_time if self.execution_time > 0 else None,
            "created_at": self.created_at
        }


@dataclass
class Vote:
    """Individual vote on a proposal."""
    voter: str
    proposal_id: str
    option: VoteOption
    voting_power: Decimal
    timestamp: int = field(default_factory=lambda: int(time.time()))
    reason: str = ""


# ------------------------------------------------------------------------------------
# DAO Governance
# ------------------------------------------------------------------------------------

class EnlikoDAO:
    """
    Decentralized Autonomous Organization for ELCARO Chain.
    
    Governance Features:
    - Proposal creation (100,000 ELC minimum)
    - On-chain voting (1 ELC = 1 vote)
    - 3-day discussion + 7-day voting
    - 10% quorum required
    - 2-day timelock after passing
    - Treasury management
    - Protocol parameter updates
    """
    
    def __init__(
        self,
        treasury_balance: Decimal = Decimal("200000000"),  # 200M ELC
        circulating_supply: Decimal = Decimal("1000000000")  # 1B ELC
    ):
        self.proposals: Dict[str, Proposal] = {}
        self.votes: Dict[str, List[Vote]] = {}  # proposal_id -> [Vote]
        self.user_voting_power: Dict[str, Decimal] = {}  # user -> locked ELC
        
        # Configuration
        self.min_proposal_threshold = Decimal("100000")  # 100k ELC to create proposal
        self.voting_period = 7 * 24 * 3600  # 7 days
        self.discussion_period = 3 * 24 * 3600  # 3 days
        self.timelock_delay = 2 * 24 * 3600  # 2 days
        self.quorum_percent = Decimal("0.1")  # 10%
        
        # Treasury
        self.treasury_balance = treasury_balance
        self.circulating_supply = circulating_supply
        
        # Statistics
        self.total_proposals = 0
        self.total_votes_cast = 0
        self.treasury_spent = Decimal(0)
        
        logger.info(f"ELCARO DAO initialized with {treasury_balance} ELC treasury")
    
    # ------------------------------------------------------------------------------------
    # Voting Power Management
    # ------------------------------------------------------------------------------------
    
    def lock_tokens_for_voting(self, user: str, amount: Decimal):
        """Lock ELC tokens to gain voting power."""
        if user not in self.user_voting_power:
            self.user_voting_power[user] = Decimal(0)
        
        self.user_voting_power[user] += amount
        logger.info(f"User {user} locked {amount} ELC for voting, total: {self.user_voting_power[user]}")
    
    def unlock_voting_tokens(self, user: str, amount: Decimal):
        """Unlock ELC tokens (after voting period ends)."""
        current_power = self.user_voting_power.get(user, Decimal(0))
        
        if current_power < amount:
            raise ValueError(f"Insufficient locked tokens: {current_power} < {amount}")
        
        self.user_voting_power[user] -= amount
        logger.info(f"User {user} unlocked {amount} ELC, remaining: {self.user_voting_power[user]}")
    
    def get_voting_power(self, user: str) -> Decimal:
        """Get user's current voting power."""
        return self.user_voting_power.get(user, Decimal(0))
    
    # ------------------------------------------------------------------------------------
    # Proposal Management
    # ------------------------------------------------------------------------------------
    
    def create_proposal(
        self,
        proposer: str,
        proposal_type: ProposalType,
        title: str,
        description: str,
        targets: List[str] = None,
        values: List[Decimal] = None,
        calldatas: List[bytes] = None
    ) -> str:
        """Create a new governance proposal."""
        # Check proposer has enough voting power
        voting_power = self.get_voting_power(proposer)
        if voting_power < self.min_proposal_threshold:
            raise ValueError(
                f"Insufficient voting power to create proposal: "
                f"{voting_power} < {self.min_proposal_threshold}"
            )
        
        # Generate proposal ID
        proposal_id = f"prop_{self.total_proposals + 1}_{int(time.time())}"
        
        # Calculate voting times
        now = int(time.time())
        voting_start = now + self.discussion_period
        voting_end = voting_start + self.voting_period
        
        # Calculate quorum
        quorum = self.circulating_supply * self.quorum_percent
        
        proposal = Proposal(
            proposal_id=proposal_id,
            proposer=proposer,
            proposal_type=proposal_type,
            title=title,
            description=description,
            targets=targets or [],
            values=values or [],
            calldatas=calldatas or [],
            voting_start=voting_start,
            voting_end=voting_end,
            quorum=quorum,
            status=ProposalStatus.PENDING
        )
        
        self.proposals[proposal_id] = proposal
        self.votes[proposal_id] = []
        self.total_proposals += 1
        
        logger.info(f"Proposal created: {proposal_id} by {proposer}")
        return proposal_id
    
    def activate_proposal(self, proposal_id: str):
        """Activate proposal for voting (after discussion period)."""
        proposal = self.proposals.get(proposal_id)
        if not proposal:
            raise ValueError(f"Proposal {proposal_id} not found")
        
        now = int(time.time())
        if now < proposal.voting_start:
            raise ValueError("Discussion period not yet ended")
        
        proposal.status = ProposalStatus.ACTIVE
        logger.info(f"Proposal activated: {proposal_id}")
    
    def cancel_proposal(self, proposal_id: str, canceller: str):
        """Cancel a proposal (only by proposer or if proposer loses voting power)."""
        proposal = self.proposals.get(proposal_id)
        if not proposal:
            raise ValueError(f"Proposal {proposal_id} not found")
        
        # Check if canceller is proposer or proposer lost voting power
        if canceller != proposal.proposer:
            proposer_power = self.get_voting_power(proposal.proposer)
            if proposer_power >= self.min_proposal_threshold:
                raise ValueError("Only proposer can cancel, and they still have enough voting power")
        
        proposal.status = ProposalStatus.CANCELLED
        logger.info(f"Proposal cancelled: {proposal_id}")
    
    # ------------------------------------------------------------------------------------
    # Voting
    # ------------------------------------------------------------------------------------
    
    def cast_vote(
        self,
        voter: str,
        proposal_id: str,
        option: VoteOption,
        reason: str = ""
    ):
        """Cast a vote on a proposal."""
        proposal = self.proposals.get(proposal_id)
        if not proposal:
            raise ValueError(f"Proposal {proposal_id} not found")
        
        if not proposal.is_active:
            raise ValueError("Proposal is not active for voting")
        
        # Check if user already voted
        existing_vote = self._get_user_vote(voter, proposal_id)
        if existing_vote:
            raise ValueError(f"User {voter} already voted on proposal {proposal_id}")
        
        # Get voting power
        voting_power = self.get_voting_power(voter)
        if voting_power == 0:
            raise ValueError(f"User {voter} has no voting power")
        
        # Create vote
        vote = Vote(
            voter=voter,
            proposal_id=proposal_id,
            option=option,
            voting_power=voting_power,
            reason=reason
        )
        
        self.votes[proposal_id].append(vote)
        
        # Update proposal vote counts
        if option == VoteOption.FOR:
            proposal.votes_for += voting_power
        elif option == VoteOption.AGAINST:
            proposal.votes_against += voting_power
        else:  # ABSTAIN
            proposal.votes_abstain += voting_power
        
        self.total_votes_cast += 1
        
        logger.info(f"Vote cast: {voter} voted {option.value} on {proposal_id} with power {voting_power}")
    
    def _get_user_vote(self, voter: str, proposal_id: str) -> Optional[Vote]:
        """Get user's vote on a proposal."""
        proposal_votes = self.votes.get(proposal_id, [])
        for vote in proposal_votes:
            if vote.voter == voter:
                return vote
        return None
    
    # ------------------------------------------------------------------------------------
    # Proposal Execution
    # ------------------------------------------------------------------------------------
    
    def finalize_proposal(self, proposal_id: str):
        """Finalize proposal after voting ends."""
        proposal = self.proposals.get(proposal_id)
        if not proposal:
            raise ValueError(f"Proposal {proposal_id} not found")
        
        now = int(time.time())
        if now < proposal.voting_end:
            raise ValueError("Voting period not yet ended")
        
        # Check if proposal succeeded
        if proposal.has_succeeded:
            proposal.status = ProposalStatus.SUCCEEDED
            
            # Queue for execution (with timelock)
            proposal.status = ProposalStatus.QUEUED
            proposal.execution_time = now + self.timelock_delay
            
            logger.info(f"Proposal succeeded and queued: {proposal_id}, executable at {proposal.execution_time}")
        else:
            proposal.status = ProposalStatus.DEFEATED
            logger.info(f"Proposal defeated: {proposal_id}")
    
    def execute_proposal(self, proposal_id: str, executor: str) -> bool:
        """Execute a proposal after timelock."""
        proposal = self.proposals.get(proposal_id)
        if not proposal:
            raise ValueError(f"Proposal {proposal_id} not found")
        
        if not proposal.can_execute:
            raise ValueError(f"Proposal {proposal_id} cannot be executed yet")
        
        # Execute proposal actions
        try:
            self._execute_proposal_actions(proposal)
            
            proposal.status = ProposalStatus.EXECUTED
            proposal.executed_at = int(time.time())
            
            logger.info(f"Proposal executed: {proposal_id} by {executor}")
            return True
            
        except Exception as e:
            logger.error(f"Proposal execution failed: {proposal_id}, error: {e}")
            return False
    
    def _execute_proposal_actions(self, proposal: Proposal):
        """Execute proposal-specific actions."""
        if proposal.proposal_type == ProposalType.TREASURY_SPENDING:
            # Execute treasury spending
            for target, value in zip(proposal.targets, proposal.values):
                self._transfer_from_treasury(target, value)
        
        elif proposal.proposal_type == ProposalType.PARAMETER_CHANGE:
            # Execute parameter changes
            logger.info(f"Parameter change executed: {proposal.title}")
        
        elif proposal.proposal_type == ProposalType.PROTOCOL_UPGRADE:
            # Execute protocol upgrade
            logger.info(f"Protocol upgrade executed: {proposal.title}")
        
        elif proposal.proposal_type == ProposalType.EMERGENCY_ACTION:
            # Execute emergency action
            logger.info(f"Emergency action executed: {proposal.title}")
    
    def _transfer_from_treasury(self, recipient: str, amount: Decimal):
        """Transfer funds from treasury."""
        if amount > self.treasury_balance:
            raise ValueError(f"Insufficient treasury balance: {self.treasury_balance} < {amount}")
        
        self.treasury_balance -= amount
        self.treasury_spent += amount
        
        logger.info(f"Treasury transfer: {amount} ELC to {recipient}")
    
    # ------------------------------------------------------------------------------------
    # Queries
    # ------------------------------------------------------------------------------------
    
    def get_proposal(self, proposal_id: str) -> Optional[Proposal]:
        """Get proposal by ID."""
        return self.proposals.get(proposal_id)
    
    def get_active_proposals(self) -> List[Proposal]:
        """Get all active proposals."""
        return [p for p in self.proposals.values() if p.is_active]
    
    def get_all_proposals(self, status: ProposalStatus = None) -> List[Proposal]:
        """Get all proposals, optionally filtered by status."""
        proposals = list(self.proposals.values())
        
        if status:
            proposals = [p for p in proposals if p.status == status]
        
        return sorted(proposals, key=lambda p: p.created_at, reverse=True)
    
    def get_proposal_votes(self, proposal_id: str) -> List[Vote]:
        """Get all votes for a proposal."""
        return self.votes.get(proposal_id, [])
    
    def get_user_votes(self, user: str) -> List[Vote]:
        """Get all votes by a user."""
        user_votes = []
        for proposal_votes in self.votes.values():
            for vote in proposal_votes:
                if vote.voter == user:
                    user_votes.append(vote)
        return user_votes
    
    def get_stats(self) -> Dict:
        """Get DAO statistics."""
        active_proposals = len(self.get_active_proposals())
        
        return {
            "total_proposals": self.total_proposals,
            "active_proposals": active_proposals,
            "total_votes_cast": self.total_votes_cast,
            "treasury_balance": str(self.treasury_balance),
            "treasury_spent": str(self.treasury_spent),
            "circulating_supply": str(self.circulating_supply),
            "total_voting_power_locked": str(sum(self.user_voting_power.values())),
            "unique_voters": len(self.user_voting_power),
            "min_proposal_threshold": str(self.min_proposal_threshold),
            "quorum_percent": str(self.quorum_percent * 100) + "%"
        }


# ------------------------------------------------------------------------------------
# Helper Functions
# ------------------------------------------------------------------------------------

def create_parameter_change_proposal(
    dao: EnlikoDAO,
    proposer: str,
    parameter: str,
    old_value: Any,
    new_value: Any,
    justification: str
) -> str:
    """Helper to create a parameter change proposal."""
    title = f"Change {parameter}: {old_value} → {new_value}"
    description = f"Proposal to change {parameter} from {old_value} to {new_value}.\n\nJustification:\n{justification}"
    
    return dao.create_proposal(
        proposer=proposer,
        proposal_type=ProposalType.PARAMETER_CHANGE,
        title=title,
        description=description
    )


def create_treasury_spending_proposal(
    dao: EnlikoDAO,
    proposer: str,
    recipient: str,
    amount: Decimal,
    purpose: str
) -> str:
    """Helper to create a treasury spending proposal."""
    title = f"Treasury Spending: {amount} ELC to {recipient}"
    description = f"Proposal to spend {amount} ELC from treasury.\n\nRecipient: {recipient}\n\nPurpose:\n{purpose}"
    
    return dao.create_proposal(
        proposer=proposer,
        proposal_type=ProposalType.TREASURY_SPENDING,
        title=title,
        description=description,
        targets=[recipient],
        values=[amount]
    )
