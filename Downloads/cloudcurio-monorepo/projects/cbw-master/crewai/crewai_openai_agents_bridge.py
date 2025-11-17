#!/usr/bin/env python3
# Script Name : crewai_openai_agents_bridge.py
# Author      : cbwinslow + ChatGPT
# Date        : 2025-11-16
#
# Summary:
#   Bridge layer that maps your existing OpenAI-style agents & tools
#   (Web Research, Code Analysis, Data Processing, Consensus, Self-Healing,
#   Memory Management, etc.) into a runnable CrewAI multi-agent crew.
#
#   This script shows how to:
#     * Define CrewAI Agents and Tasks directly in code.
#     * Attach tools (via crewai-tools) that align with your logical toolsets.
#     * Create a multi-step workflow:
#           research -> analysis -> consensus -> self-healing check
#     * Provide a single entrypoint `main()` for quick manual tests.
#
# Inputs:
#   CLI / programmatic:
#     - topic: str  (what you want the crew to research/analyze)
#
# Outputs:
#   - Printed final result from the consensus task.
#   - Rich logs describing each phase and task.
#
# Dependencies (minimal):
#   pip install "crewai>=0.70" "crewai-tools>=0.30"
from __future__ import annotations

import logging
import os
from typing import List

from crewai import Agent, Crew, LLM, Process, Task
from crewai_tools import (
    SerperDevTool,
    ScrapeWebsiteTool,
    FileReadTool,
    FileWriterTool,
)

LOGGER_NAME = "crewai_openai_agents_bridge"
logger = logging.getLogger(LOGGER_NAME)

if not logger.handlers:
    _handler = logging.StreamHandler()
    _fmt = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] %(name)s :: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    _handler.setFormatter(_fmt)
    logger.addHandler(_handler)
    logger.setLevel(logging.INFO)


def build_default_llm() -> LLM:
    model_name = os.getenv("CREWAI_DEFAULT_MODEL", "gpt-4o")
    logger.info("Using default CrewAI LLM model: %s", model_name)
    return LLM(model=model_name)


def build_web_research_tools():
    return [
        SerperDevTool(),
        ScrapeWebsiteTool(),
        FileReadTool(),
        FileWriterTool(),
    ]


def build_data_processing_tools():
    return [FileReadTool(), FileWriterTool()]


def build_consensus_tools():
    return [FileReadTool()]


def build_self_healing_tools():
    return [FileReadTool(), FileWriterTool()]


def build_web_research_agent(llm: LLM) -> Agent:
    return Agent(
        role="Senior Web Research Analyst",
        goal=(
            "Perform deep, citation-rich web research about {topic} using "
            "search and scraping tools, returning structured notes."
        ),
        backstory=(
            "You are a meticulous OSINT-style researcher. You respect robots.txt, "
            "prioritize trustworthy sources, and always capture URLs for traceability."
        ),
        tools=build_web_research_tools(),
        llm=llm,
        verbose=True,
        allow_delegation=False,
        max_iter=15,
    )


def build_data_processing_agent(llm: LLM) -> Agent:
    return Agent(
        role="Data Processing & Synthesis Specialist",
        goal=(
            "Clean, structure, and analyze the research notes about {topic} to "
            "extract key patterns, trade-offs, and metrics."
        ),
        backstory=(
            "You think in tables, charts, and bullet points. You summarize without "
            "losing nuance, and highlight uncertainties and assumptions."
        ),
        tools=build_data_processing_tools(),
        llm=llm,
        verbose=True,
        allow_delegation=False,
        max_iter=15,
    )


def build_consensus_agent(llm: LLM) -> Agent:
    return Agent(
        role="Democratic Consensus Coordinator",
        goal=(
            "Read all prior agent outputs about {topic}, resolve disagreements, "
            "and propose a clear, justified consensus recommendation."
        ),
        backstory=(
            "You act like a careful chairperson of a technical committee. You read "
            "everyone's notes, quote them fairly, and document where the group "
            "agrees, disagrees, and remains uncertain."
        ),
        tools=build_consensus_tools(),
        llm=llm,
        verbose=True,
        allow_delegation=False,
        max_iter=12,
    )


def build_self_healing_agent(llm: LLM) -> Agent:
    return Agent(
        role="Self-Healing Orchestrator",
        goal=(
            "Inspect the crew's previous steps for gaps or contradictions and "
            "suggest concrete follow-up actions or re-runs to improve results."
        ),
        backstory=(
            "You are an observability and QA engineer for multi-agent systems. You "
            "look for missing data, weak reasoning, and brittle assumptions, then "
            "propose specific remediation steps."
        ),
        tools=build_self_healing_tools(),
        llm=llm,
        verbose=True,
        allow_delegation=False,
        max_iter=10,
    )


def build_tasks(
    research_agent: Agent,
    data_agent: Agent,
    consensus_agent: Agent,
    self_healing_agent: Agent,
) -> List[Task]:

    research_task = Task(
        name="research_task",
        description=(
            "Conduct a thorough web and document research about {topic}. "
            "Cover definitions, current state, tools/libraries, risks, and "
            "at least 5 high-signal references with URLs."
        ),
        expected_output=(
            "A markdown outline with sections: Summary, Key Concepts, Tools, "
            "Risks, Open Questions, and a Bullet List of Sources (with URLs)."
        ),
        agent=research_agent,
        async_execution=False,
    )

    analysis_task = Task(
        name="analysis_task",
        description=(
            "Using the research notes, normalize the information into a compact "
            "set of bullet points and (if relevant) a comparison table. Focus "
            "on trade-offs, implementation details, and gotchas."
        ),
        expected_output=(
            "A markdown section with: Key Takeaways, Pros/Cons, Implementation "
            "Checklist, and Unknowns/Assumptions."
        ),
        agent=data_agent,
        context=[research_task],
        async_execution=False,
    )

    consensus_task = Task(
        name="consensus_task",
        description=(
            "Read the research and analysis outputs about {topic}. Resolve any "
            "conflicts, explicitly call out disagreements, and propose a "
            "consensus recommendation with rationale."
        ),
        expected_output=(
            "A markdown report titled 'Consensus Plan for {topic}', with sections "
            "for: Agreed Points, Disagreements, Final Recommendation, and "
            "Next Experiments to Validate."
        ),
        agent=consensus_agent,
        context=[research_task, analysis_task],
        async_execution=False,
    )

    self_healing_task = Task(
        name="self_healing_task",
        description=(
            "Review ALL previous outputs for {topic}. Identify gaps, missing data, "
            "or suspicious reasoning patterns. Propose a prioritized list of "
            "follow-up actions or tasks for the crew to re-run or extend."
        ),
        expected_output=(
            "A markdown checklist of 'Health Findings' with severity labels, "
            "plus a concrete plan (1-3 steps) for improving the crew's work."
        ),
        agent=self_healing_agent,
        context=[research_task, analysis_task, consensus_task],
        async_execution=False,
    )

    return [research_task, analysis_task, consensus_task, self_healing_task]


def build_crew() -> Crew:
    llm = build_default_llm()

    web_research_agent = build_web_research_agent(llm)
    data_agent = build_data_processing_agent(llm)
    consensus_agent = build_consensus_agent(llm)
    self_healing_agent = build_self_healing_agent(llm)

    tasks = build_tasks(
        research_agent=web_research_agent,
        data_agent=data_agent,
        consensus_agent=consensus_agent,
        self_healing_agent=self_healing_agent,
    )

    crew = Crew(
        agents=[
            web_research_agent,
            data_agent,
            consensus_agent,
            self_healing_agent,
        ],
        tasks=tasks,
        process=Process.sequential,
        verbose=True,
    )

    return crew


def main(topic: str = "AI agent frameworks and CrewAI integration") -> None:
    logger.info("Starting CrewAI multi-agent run for topic: %s", topic)
    crew = build_crew()
    result = crew.kickoff(inputs={"topic": topic})

    logger.info("Crew run completed. Final output (truncated to 500 chars):\n%s", str(result)[:500])
    print("\n=== FINAL OUTPUT (raw) ===\n")
    try:
        print(getattr(result, "raw", str(result)))
    except Exception as exc:
        logger.error("Error printing result.raw: %s", exc)
        print(str(result))


if __name__ == "__main__":
    main()
