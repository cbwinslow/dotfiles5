#!/usr/bin/env python3
"""
Democratic Multi-Agent System Implementation
Demonstrates consensus-based decision making with OpenRouter integration
"""

import asyncio
import json
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
import openai
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VoteType(Enum):
    APPROVAL = "approval"
    RANKED_CHOICE = "ranked_choice"
    QUADRATIC = "quadratic"
    WEIGHTED = "weighted"

@dataclass
class Agent:
    id: str
    name: str
    role: str
    expertise: List[str]
    voting_power: float = 1.0
    model_preference: str = "anthropic/claude-3.5-sonnet"

@dataclass
class Proposal:
    id: str
    title: str
    description: str
    proposer_id: str
    created_at: datetime
    voting_deadline: datetime
    vote_type: VoteType
    options: List[str]

@dataclass
class Vote:
    agent_id: str
    proposal_id: str
    choice: str
    weight: float
    timestamp: datetime

class ConsensusEngine:
    """Implements various consensus algorithms for agent decision making"""
    
    def __init__(self):
        self.quorum_threshold = 0.6  # 60% participation required
        self.approval_threshold = 0.5  # 50% approval required
    
    async def raft_consensus(self, agents: List[Agent], proposal: Proposal) -> Dict[str, Any]:
        """Implement Raft-style leader election and consensus"""
        logger.info(f"Starting Raft consensus for proposal: {proposal.id}")
        
        # Phase 1: Leader election
        leader = await self._elect_leader(agents)
        logger.info(f"Agent {leader.name} elected as leader")
        
        # Phase 2: Log replication (voting)
        votes = await self._collect_votes(agents, proposal, leader)
        
        # Phase 3: Commit decision
        result = await self._commit_decision(votes, proposal)
        
        return {
            "algorithm": "raft",
            "leader": leader.id,
            "votes": votes,
            "decision": result,
            "consensus_reached": result["approved"]
        }
    
    async def _elect_leader(self, agents: List[Agent]) -> Agent:
        """Simple leader election based on expertise and voting power"""
        # In production, this would be more sophisticated
        return max(agents, key=lambda a: a.voting_power * len(a.expertise))
    
    async def _collect_votes(self, agents: List[Agent], proposal: Proposal, leader: Agent) -> List[Vote]:
        """Collect votes from all agents"""
        votes = []
        
        for agent in agents:
            if agent.id == leader.id:
                # Leader votes first
                vote = await self._cast_vote(agent, proposal)
                votes.append(vote)
            else:
                # Followers vote after leader
                vote = await self._cast_vote(agent, proposal)
                votes.append(vote)
        
        return votes
    
    async def _cast_vote(self, agent: Agent, proposal: Proposal) -> Vote:
        """Agent casts vote using OpenRouter model"""
        # Simulate AI agent decision making
        # In production, this would call OpenRouter API
        choice = await self._agent_deliberation(agent, proposal)
        
        return Vote(
            agent_id=agent.id,
            proposal_id=proposal.id,
            choice=choice,
            weight=agent.voting_power,
            timestamp=datetime.now()
        )
    
    async def _agent_deliberation(self, agent: Agent, proposal: Proposal) -> str:
        """Simulate agent deliberation using AI model"""
        # This would integrate with OpenRouter in production
        # For now, simulate based on agent expertise
        if "security" in agent.expertise and "security" in proposal.description.lower():
            return "approve" if "secure" in proposal.description.lower() else "reject"
        
        # Simple heuristic for demo
        return "approve" if len(proposal.options) > 1 else "reject"
    
    async def _commit_decision(self, votes: List[Vote], proposal: Proposal) -> Dict[str, Any]:
        """Commit decision based on votes"""
        total_weight = sum(vote.weight for vote in votes)
        approve_weight = sum(vote.weight for vote in votes if vote.choice == "approve")
        
        approval_rate = approve_weight / total_weight if total_weight > 0 else 0
        quorum_met = len(votes) >= len(proposal.options) * self.quorum_threshold
        
        return {
            "approved": approval_rate >= self.approval_threshold and quorum_met,
            "approval_rate": approval_rate,
            "quorum_met": quorum_met,
            "total_votes": len(votes),
            "total_weight": total_weight
        }

class OpenRouterClient:
    """Client for interacting with OpenRouter API"""
    
    def __init__(self, api_key: str):
        self.client = openai.AsyncOpenAI(
            api_key=api_key,
            base_url="https://openrouter.ai/api/v1"
        )
    
    async def get_agent_recommendation(self, agent: Agent, proposal: Proposal) -> str:
        """Get AI-powered recommendation from agent"""
        prompt = f"""
        As {agent.name}, a {agent.role} with expertise in {', '.join(agent.expertise)},
        evaluate this proposal:
        
        Title: {proposal.title}
        Description: {proposal.description}
        Options: {', '.join(proposal.options)}
        
        Provide your recommendation (approve/reject/abstain) and brief reasoning.
        """
        
        try:
            response = await self.client.chat.completions.create(
                model=agent.model_preference,
                messages=[
                    {"role": "system", "content": f"You are {agent.name}, {agent.role}."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=200,
                temperature=0.7
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Error getting recommendation from {agent.name}: {e}")
            return "abstain"

class DemocraticMultiAgentSystem:
    """Main system coordinating democratic multi-agent decision making"""
    
    def __init__(self, openrouter_api_key: str):
        self.agents: List[Agent] = []
        self.proposals: List[Proposal] = []
        self.votes: List[Vote] = []
        self.consensus_engine = ConsensusEngine()
        self.openrouter_client = OpenRouterClient(openrouter_api_key)
    
    def add_agent(self, agent: Agent):
        """Add an agent to the system"""
        self.agents.append(agent)
        logger.info(f"Added agent: {agent.name} ({agent.role})")
    
    def create_proposal(self, proposal: Proposal):
        """Create a new proposal for voting"""
        self.proposals.append(proposal)
        logger.info(f"Created proposal: {proposal.title}")
    
    async def process_proposal(self, proposal_id: str) -> Dict[str, Any]:
        """Process a proposal through democratic consensus"""
        proposal = next((p for p in self.proposals if p.id == proposal_id), None)
        if not proposal:
            raise ValueError(f"Proposal {proposal_id} not found")
        
        logger.info(f"Processing proposal: {proposal.title}")
        
        # Use Raft consensus algorithm
        result = await self.consensus_engine.raft_consensus(self.agents, proposal)
        
        # Store votes
        self.votes.extend(result["votes"])
        
        return result

# Example usage
async def main():
    """Demonstrate the democratic multi-agent system"""
    
    # Initialize system
    system = DemocraticMultiAgentSystem("your-openrouter-api-key")
    
    # Create agents with different roles and expertise
    agents = [
        Agent("agent1", "Security Expert", "security_analyst", 
              ["security", "cryptography", "network_security"], 1.5),
        Agent("agent2", "ML Engineer", "ml_developer", 
              ["machine_learning", "data_science", "python"], 1.2),
        Agent("agent3", "Product Manager", "product_owner", 
              ["product_management", "user_experience", "agile"], 1.0),
        Agent("agent4", "DevOps Engineer", "devops_specialist", 
              ["infrastructure", "cloud", "monitoring"], 1.1),
    ]
    
    for agent in agents:
        system.add_agent(agent)
    
    # Create a proposal
    proposal = Proposal(
        id="prop1",
        title="Implement New Security Protocol",
        description="Should we implement a new end-to-end encryption protocol for user data?",
        proposer_id="agent1",
        created_at=datetime.now(),
        voting_deadline=datetime.now(),
        vote_type=VoteType.APPROVAL,
        options=["approve", "reject", "abstain"]
    )
    
    system.create_proposal(proposal)
    
    # Process the proposal
    result = await system.process_proposal("prop1")
    
    # Display results
    print("\n" + "="*50)
    print("DEMOCRATIC CONSENSUS RESULTS")
    print("="*50)
    print(f"Algorithm: {result['algorithm']}")
    print(f"Leader: {result['leader']}")
    print(f"Consensus Reached: {result['decision']['approved']}")
    print(f"Approval Rate: {result['decision']['approval_rate']:.2%}")
    print(f"Quorum Met: {result['decision']['quorum_met']}")
    print(f"Total Votes: {result['decision']['total_votes']}")
    
    print("\nVote Details:")
    for vote in result['votes']:
        agent = next(a for a in agents if a.id == vote.agent_id)
        print(f"  {agent.name}: {vote.choice} (weight: {vote.weight})")

if __name__ == "__main__":
    asyncio.run(main())