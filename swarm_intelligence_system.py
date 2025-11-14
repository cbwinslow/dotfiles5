#!/usr/bin/env python3
"""
Swarm Intelligence Implementation for Multi-Agent Coordination
Demonstrates emergent behavior through simple local rules
"""

import asyncio
import json
import math
import random
from typing import List, Dict, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum
import numpy as np
from datetime import datetime

class AgentState(Enum):
    IDLE = "idle"
    EXPLORING = "exploring"
    WORKING = "working"
    COORDINATING = "coordinating"
    REPORTING = "reporting"

@dataclass
class Position:
    x: float
    y: float
    
    def distance_to(self, other: 'Position') -> float:
        return math.sqrt((self.x - other.x)**2 + (self.y - other.y)**2)

@dataclass
class SwarmAgent:
    id: str
    position: Position
    state: AgentState
    energy: float = 100.0
    vision_range: float = 10.0
    communication_range: float = 15.0
    task_queue: List[str] = field(default_factory=list)
    knowledge: Dict[str, Any] = field(default_factory=dict)
    
    def can_see(self, other: 'SwarmAgent') -> bool:
        return self.position.distance_to(other.position) <= self.vision_range
    
    def can_communicate_with(self, other: 'SwarmAgent') -> bool:
        return self.position.distance_to(other.position) <= self.communication_range

@dataclass
class Task:
    id: str
    position: Position
    priority: int
    required_agents: int
    assigned_agents: List[str] = field(default_factory=list)
    completed: bool = False

class SwarmIntelligence:
    """Implements swarm intelligence patterns for agent coordination"""
    
    def __init__(self, width: float = 100.0, height: float = 100.0):
        self.width = width
        self.height = height
        self.agents: List[SwarmAgent] = []
        self.tasks: List[Task] = []
        self.global_knowledge: Dict[str, Any] = {}
        self.time_step = 0
        
    def add_agent(self, agent: SwarmAgent):
        """Add an agent to the swarm"""
        self.agents.append(agent)
    
    def add_task(self, task: Task):
        """Add a task to be completed by the swarm"""
        self.tasks.append(task)
    
    async def simulate_step(self):
        """Simulate one time step of swarm behavior"""
        self.time_step += 1
        
        # Phase 1: Local perception
        await self._local_perception()
        
        # Phase 2: Decision making
        await self._decision_making()
        
        # Phase 3: Action execution
        await self._execute_actions()
        
        # Phase 4: Information sharing
        await self._information_sharing()
        
        # Phase 5: Global coordination
        await self._global_coordination()
    
    async def _local_perception(self):
        """Agents perceive their local environment"""
        for agent in self.agents:
            # Find nearby agents
            nearby_agents = [other for other in self.agents 
                           if agent.id != other.id and agent.can_see(other)]
            
            # Find nearby tasks
            nearby_tasks = [task for task in self.tasks 
                          if not task.completed and 
                          agent.position.distance_to(task.position) <= agent.vision_range]
            
            # Update local knowledge
            agent.knowledge.update({
                'nearby_agents': [a.id for a in nearby_agents],
                'nearby_tasks': [t.id for t in nearby_tasks],
                'agent_density': len(nearby_agents),
                'task_density': len(nearby_tasks)
            })
    
    async def _decision_making(self):
        """Agents make decisions based on local information"""
        for agent in self.agents:
            if agent.state == AgentState.IDLE:
                await self._decide_exploration(agent)
            elif agent.state == AgentState.EXPLORING:
                await self._decide_task_assignment(agent)
            elif agent.state == AgentState.WORKING:
                await self._decide_work_continuation(agent)
    
    async def _decide_exploration(self, agent: SwarmAgent):
        """Decide whether and where to explore"""
        # Simple exploration strategy: move towards areas with fewer agents
        if agent.knowledge.get('agent_density', 0) > 3:
            # Too crowded, move away
            agent.state = AgentState.EXPLORING
            direction = await self._find_least_crowded_direction(agent)
            agent.knowledge['exploration_direction'] = direction
        elif random.random() < 0.1:  # 10% chance to explore anyway
            agent.state = AgentState.EXPLORING
            direction = random.uniform(0, 2 * math.pi)
            agent.knowledge['exploration_direction'] = direction
    
    async def _decide_task_assignment(self, agent: SwarmAgent):
        """Decide whether to take on a task"""
        nearby_tasks = [task for task in self.tasks 
                       if not task.completed and 
                       agent.position.distance_to(task.position) <= agent.vision_range]
        
        if nearby_tasks:
            # Choose highest priority task that needs agents
            available_tasks = [t for t in nearby_tasks 
                             if len(t.assigned_agents) < t.required_agents]
            
            if available_tasks:
                task = max(available_tasks, key=lambda t: t.priority)
                task.assigned_agents.append(agent.id)
                agent.task_queue.append(task.id)
                agent.state = AgentState.WORKING
                agent.knowledge['current_task'] = task.id
    
    async def _decide_work_continuation(self, agent: SwarmAgent):
        """Decide whether to continue working on current task"""
        if not agent.task_queue:
            agent.state = AgentState.IDLE
            return
        
        current_task_id = agent.task_queue[0]
        current_task = next((t for t in self.tasks if t.id == current_task_id), None)
        
        if not current_task or current_task.completed:
            agent.task_queue.pop(0)
            agent.state = AgentState.IDLE
        elif agent.energy < 20:  # Low energy, take a break
            agent.state = AgentState.IDLE
    
    async def _execute_actions(self):
        """Execute agent actions based on decisions"""
        for agent in self.agents:
            if agent.state == AgentState.EXPLORING:
                await self._move_agent(agent, agent.knowledge.get('exploration_direction', 0))
            elif agent.state == AgentState.WORKING:
                await self._work_on_task(agent)
            
            # Energy consumption
            if agent.state != AgentState.IDLE:
                agent.energy = max(0, agent.energy - 1)
            else:
                agent.energy = min(100, agent.energy + 2)  # Rest and recover
    
    async def _move_agent(self, agent: SwarmAgent, direction: float):
        """Move agent in given direction"""
        speed = 2.0
        new_x = agent.position.x + speed * math.cos(direction)
        new_y = agent.position.y + speed * math.sin(direction)
        
        # Keep within bounds
        agent.position.x = max(0, min(self.width, new_x))
        agent.position.y = max(0, min(self.height, new_y))
    
    async def _work_on_task(self, agent: SwarmAgent):
        """Agent works on assigned task"""
        if not agent.task_queue:
            return
        
        task_id = agent.task_queue[0]
        task = next((t for t in self.tasks if t.id == task_id), None)
        
        if task:
            # Move towards task if not already there
            if agent.position.distance_to(task.position) > 1.0:
                direction = math.atan2(
                    task.position.y - agent.position.y,
                    task.position.x - agent.position.x
                )
                await self._move_agent(agent, direction)
            else:
                # Working on task
                task.priority -= 1  # Reduce priority as work progresses
                if task.priority <= 0:
                    task.completed = True
                    agent.task_queue.pop(0)
    
    async def _information_sharing(self):
        """Agents share information with nearby agents"""
        for agent in self.agents:
            nearby_agents = [other for other in self.agents 
                           if agent.id != other.id and agent.can_communicate_with(other)]
            
            for other in nearby_agents:
                # Share task locations
                if 'nearby_tasks' in agent.knowledge:
                    other_tasks = other.knowledge.get('known_tasks', set())
                    other_tasks.update(agent.knowledge['nearby_tasks'])
                    other.knowledge['known_tasks'] = other_tasks
    
    async def _global_coordination(self):
        """Periodic global coordination through leader election"""
        if self.time_step % 10 == 0:  # Every 10 steps
            await self._elect_coordinator()
            await self._broadcast_global_state()
    
    async def _elect_coordinator(self):
        """Elect a coordinator agent based on energy and position"""
        if not self.agents:
            return
        
        # Choose agent with highest energy and central position
        center = Position(self.width / 2, self.height / 2)
        
        def coordinator_score(agent: SwarmAgent) -> float:
            distance_from_center = agent.position.distance_to(center)
            return agent.energy - distance_from_center
        
        coordinator = max(self.agents, key=coordinator_score)
        self.global_knowledge['coordinator'] = coordinator.id
        
        # Mark coordinator
        for agent in self.agents:
            agent.state = AgentState.COORDINATING if agent.id == coordinator.id else agent.state
    
    async def _broadcast_global_state(self):
        """Broadcast global state through coordinator"""
        coordinator_id = self.global_knowledge.get('coordinator')
        if not coordinator_id:
            return
        
        coordinator = next((a for a in self.agents if a.id == coordinator_id), None)
        if not coordinator:
            return
        
        # Coordinator aggregates and broadcasts information
        completed_tasks = len([t for t in self.tasks if t.completed])
        total_tasks = len(self.tasks)
        average_energy = sum(a.energy for a in self.agents) / len(self.agents)
        
        global_state = {
            'completed_tasks': completed_tasks,
            'total_tasks': total_tasks,
            'completion_rate': completed_tasks / total_tasks if total_tasks > 0 else 0,
            'average_energy': average_energy,
            'time_step': self.time_step
        }
        
        self.global_knowledge.update(global_state)
        
        # Share with nearby agents
        for agent in self.agents:
            if coordinator.can_communicate_with(agent):
                agent.knowledge.update(global_state)

# Visualization and monitoring
class SwarmMonitor:
    """Monitor and visualize swarm behavior"""
    
    def __init__(self, swarm: SwarmIntelligence):
        self.swarm = swarm
        self.history = []
    
    def record_state(self):
        """Record current swarm state"""
        state = {
            'time_step': self.swarm.time_step,
            'agents': [
                {
                    'id': a.id,
                    'position': {'x': a.position.x, 'y': a.position.y},
                    'state': a.state.value,
                    'energy': a.energy
                }
                for a in self.swarm.agents
            ],
            'tasks': [
                {
                    'id': t.id,
                    'position': {'x': t.position.x, 'y': t.position.y},
                    'priority': t.priority,
                    'completed': t.completed,
                    'assigned_agents': len(t.assigned_agents)
                }
                for t in self.swarm.tasks
            ],
            'global_knowledge': self.swarm.global_knowledge.copy()
        }
        self.history.append(state)
    
    def print_summary(self):
        """Print summary of current swarm state"""
        completed_tasks = len([t for t in self.swarm.tasks if t.completed])
        total_tasks = len(self.swarm.tasks)
        avg_energy = sum(a.energy for a in self.swarm.agents) / len(self.swarm.agents)
        
        print(f"\n=== Swarm State at Step {self.swarm.time_step} ===")
        print(f"Tasks: {completed_tasks}/{total_tasks} completed")
        print(f"Average Agent Energy: {avg_energy:.1f}")
        print(f"Coordinator: {self.swarm.global_knowledge.get('coordinator', 'None')}")
        
        # Agent states
        state_counts = {}
        for agent in self.swarm.agents:
            state_counts[agent.state.value] = state_counts.get(agent.state.value, 0) + 1
        
        print("Agent States:", ", ".join([f"{state}: {count}" for state, count in state_counts.items()]))

# Example usage
async def main():
    """Demonstrate swarm intelligence"""
    
    # Create swarm environment
    swarm = SwarmIntelligence(width=100, height=100)
    monitor = SwarmMonitor(swarm)
    
    # Add agents
    for i in range(20):
        agent = SwarmAgent(
            id=f"agent_{i}",
            position=Position(
                x=random.uniform(0, 100),
                y=random.uniform(0, 100)
            ),
            state=AgentState.IDLE,
            energy=random.uniform(50, 100)
        )
        swarm.add_agent(agent)
    
    # Add tasks
    for i in range(10):
        task = Task(
            id=f"task_{i}",
            position=Position(
                x=random.uniform(10, 90),
                y=random.uniform(10, 90)
            ),
            priority=random.randint(5, 20),
            required_agents=random.randint(1, 3)
        )
        swarm.add_task(task)
    
    print("Starting Swarm Intelligence Simulation")
    print("=" * 50)
    
    # Run simulation
    for step in range(50):
        await swarm.simulate_step()
        monitor.record_state()
        
        if step % 10 == 0:
            monitor.print_summary()
        
        # Check if all tasks completed
        if all(task.completed for task in swarm.tasks):
            print(f"\nAll tasks completed at step {step}!")
            break
    
    # Final summary
    monitor.print_summary()
    
    # Save simulation history
    with open('/home/cbwinslow/swarm_simulation_history.json', 'w') as f:
        json.dump(monitor.history, f, indent=2)
    
    print(f"\nSimulation history saved to swarm_simulation_history.json")

if __name__ == "__main__":
    asyncio.run(main())