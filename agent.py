"""
Research Assistant Agent
========================
An LLM agent that answers questions by deciding what to search for, using a
web-search tool, observing the results, and synthesizing a cited answer.

Demonstrates the core agentic pattern:  THINK -> ACT -> OBSERVE -> (repeat)

Architecture:
  - BRAIN:  Claude (decides what to do, what to search, when it's done)
  - TOOL:   web_search (the agent's ability to ACT in the world)
  - LOOP:   the orchestration that cycles brain <-> tool until the task is done

Author: Sunny Kumar Kandula
"""

import os
import anthropic
from tavily import TavilyClient   # Tavily = a search API built for AI agents (free tier)
import streamlit as st

# ----------------------------------------------------------------------------
# SETUP: API clients
# ----------------------------------------------------------------------------
# Keys are read from environment variables (never hard-code keys in your code).
#   export ANTHROPIC_API_KEY="your-key"
#   export TAVILY_API_KEY="your-key"
claude = anthropic.Anthropic(api_key=st.secrets["ANTHROPIC_API_KEY"])
tavily = TavilyClient(api_key=st.secrets["TAVILY_API_KEY"])

MODEL = "claude-sonnet-4-6"


# ----------------------------------------------------------------------------
# THE TOOL  (the agent's ability to ACT)
# ----------------------------------------------------------------------------
# A "tool" is just a plain function the agent can call. It's "dumb" — it only
# does one job (search) and returns a result. The intelligence (deciding WHEN
# and WHAT to search) lives in the LLM brain, not here.
def web_search(query: str) -> str:
    """Search the web and return the top results as text the agent can read."""
    response = tavily.search(query=query, max_results=3)
    # Format the results into a clean string for the LLM to observe
    results = []
    for r in response["results"]:
        results.append(f"Source: {r['url']}\n{r['content']}")
    return "\n\n".join(results) if results else "No results found."


# This is the description we give Claude so it KNOWS the tool exists and how to
# call it. Claude reads this to decide whether/how to use web_search.
TOOLS = [
    {
        "name": "web_search",
        "description": "Search the web for current, factual information on any topic. "
                       "Use this whenever you need up-to-date information you don't "
                       "already know.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search query to look up.",
                }
            },
            "required": ["query"],
        },
    }
]


# ----------------------------------------------------------------------------
# THE AGENT LOOP  (the orchestration — this is what makes it "agentic")
# ----------------------------------------------------------------------------
def run_agent(question: str, max_steps: int = 5, on_step=None):
    """
    Run the agent loop:  THINK -> ACT -> OBSERVE -> repeat, until Claude answers.

    question : the user's question
    max_steps: a safety cap so the loop can never run forever
    on_step  : optional callback to report progress (used by the UI to show steps)
    """
    # The running conversation. We append to this as the agent thinks and observes.
    messages = [{"role": "user", "content": question}]

    for step in range(max_steps):
        # ---- THINK: ask Claude what to do next ----
        response = claude.messages.create(
            model=MODEL,
            max_tokens=1500,
            tools=TOOLS,
            system=(
                "You are a research assistant. Use the web_search tool to gather "
                "current information, then give a clear, well-organized answer that "
                "cites its sources. Search multiple times if needed for a thorough answer."
            ),
            messages=messages,
        )

        # Save Claude's turn into the conversation history
        messages.append({"role": "assistant", "content": response.content})

        # ---- Did Claude decide to ACT (use a tool) or is it DONE? ----
        if response.stop_reason == "tool_use":
            # Claude wants to use one or more tools. Run each, collect results.
            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    query = block.input["query"]
                    if on_step:
                        on_step(f"🔍 Searching: {query}")   # report progress to UI

                    # ---- ACT: actually run the tool (our code does this) ----
                    result = web_search(query)

                    # ---- OBSERVE: package the result to send back to Claude ----
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": result,
                    })

            # Feed the observations back so Claude can think again on the next loop
            messages.append({"role": "user", "content": tool_results})

        else:
            # Claude returned a normal text answer instead of a tool request.
            # That's the STOP signal — the agent is done.
            final_answer = ""
            for block in response.content:
                if block.type == "text":
                    final_answer += block.text
            if on_step:
                on_step("✅ Done")
            return final_answer

    # Safety fallback if we hit max_steps without a final answer
    return "Reached the step limit before finishing. Try a more specific question."


# ----------------------------------------------------------------------------
# Quick command-line test (run this file directly to try it)
# ----------------------------------------------------------------------------
if __name__ == "__main__":
    q = "What are the latest developments in fusion energy in 2026?"
    print(f"Question: {q}\n")
    answer = run_agent(q, on_step=lambda s: print(s))
    print("\n--- ANSWER ---")
    print(answer)
