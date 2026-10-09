"""CrewAI research workflow for the AI Research Agent."""

import os
from dotenv import load_dotenv

load_dotenv()

class ResearchAgentError(Exception):
    """An understandable error raised when research cannot be completed."""


def _get_groq_api_key() -> str:
    """Read the Groq key from local environment or Streamlit Cloud secrets."""
    key = os.getenv("GROQ_API_KEY", "").strip()

    # Streamlit Cloud secrets are not guaranteed to become environment variables.
    if not key:
        try:
            import streamlit as st
            key = str(st.secrets.get("GROQ_API_KEY", "")).strip()
        except Exception:
            # Outside Streamlit, secrets may not be configured; report this below.
            key = ""

    if not key:
        raise ResearchAgentError(
            "GROQ_API_KEY is missing. For local use, add it to your .env file. "
            "On Streamlit Community Cloud, add it under App settings → Secrets."
        )
    return key


def run_research(topic: str) -> str:
    """Run one CrewAI agent with a web-search tool and return its report."""
    if not topic or not topic.strip():
        raise ResearchAgentError("Please enter a research topic.")

    api_key = _get_groq_api_key()

    # Import these here so missing or incompatible dependencies produce a useful message.
    try:
        from crewai import Agent, Crew, LLM, Process, Task
    except ImportError as exc:
        raise ResearchAgentError(
            "A required CrewAI package could not be imported. Run "
            "`python -m pip install -r requirements.txt` and check the terminal for errors."
        ) from exc

    # DuckDuckGo is free to try but its unofficial search endpoints can be less reliable.
    # DuckDuckGoSearchRun is used via LangChain's community tools.
    try:
        from langchain_community.tools import DuckDuckGoSearchRun
    except ImportError as exc:
        raise ResearchAgentError(
            "The DuckDuckGo search package is missing. Run "
            "`python -m pip install -r requirements.txt`."
        ) from exc

    try:
        search_tool = DuckDuckGoSearchRun()
        llm = LLM(
            model="groq/openai/gpt-oss-120b",
            api_key=api_key,
            temperature=0.2,
        )

        agent = Agent(
            role="Web Research Analyst",
            goal=(
                "Research the user's topic using web search, compare relevant findings, "
                "and produce a clear report supported by source URLs."
            ),
            backstory=(
                "You are a careful research analyst. You distinguish sourced facts from "
                "uncertainty, avoid inventing citations, and explain when search results "
                "are incomplete."
            ),
            llm=llm,
            tools=[search_tool],
            verbose=True,
            allow_delegation=False,
        )

        task = Task(
            description=(
                "Research this topic: {topic}\n\n"
                "Use the web search tool several times with focused queries where useful. "
                "Base the report on information returned by search. Preserve source URLs "
                "exactly as returned. Do not invent sources, URLs, quotations, statistics, "
                "or claims. If sources cannot be retrieved, clearly state that limitation.\n\n"
                "Write a Markdown report with these sections:\n"
                "# Title\n"
                "## Executive Summary\n"
                "## Introduction and Background\n"
                "## Key Findings\n"
                "## Detailed Analysis\n"
                "## Challenges and Limitations\n"
                "## Conclusion\n"
                "## Sources\n\n"
                "In Sources, list each source title or description and its URL when available. "
                "Do not claim a source is verified or currently working unless you checked it. "
                "Separate sourced findings from your interpretation and mention uncertainty."
            ),
            expected_output=(
                "A readable Markdown research report with all requested sections and a source "
                "list containing URLs actually returned by the search tool."
            ),
            agent=agent,
        )

        crew = Crew(
            agents=[agent],
            tasks=[task],
            process=Process.sequential,
            verbose=True,
        )
        result = crew.kickoff(inputs={"topic": topic.strip()})
        return str(result)
    except ResearchAgentError:
        raise
    except Exception as exc:
        message = str(exc)
        lowered = message.lower()
        if "401" in message or "unauthorized" in lowered or "invalid api key" in lowered:
            raise ResearchAgentError(
                "Groq rejected the API key. Check GROQ_API_KEY and make sure the key is active."
            ) from exc
        if "429" in message or "rate limit" in lowered:
            raise ResearchAgentError(
                "A rate limit was reached. Wait a little while and try again."
            ) from exc
        if "duckduckgo" in lowered or "search" in lowered or "timeout" in lowered:
            raise ResearchAgentError(
                "Web search or a network request failed. Check your internet connection and try again."
            ) from exc
        raise ResearchAgentError(
            f"The research workflow failed: {type(exc).__name__}: {message}"
        ) from exc
