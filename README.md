# 🔎 Research Assistant Agent

An LLM **agent** that answers questions by autonomously searching the web — it
decides what to search for, reads the results, searches again if needed, and
synthesizes a clear, cited answer.

### 🚀 [**Try the live demo →**](https://ai-research-assistant-4ez5kydxuc4mgedl6y4iek.streamlit.app/)

> Ask it anything that needs current information — e.g. *"What are the latest
> breakthroughs in battery technology?"* — and watch it search, reason, and
> answer with sources, live.

*(Note: the demo calls the Anthropic and Tavily APIs, so responses take a few
seconds while the agent searches and reasons.)*

---

Unlike a plain chatbot (which only generates text from what it already knows),
this agent **takes actions**: it uses a web-search tool in a reasoning loop to
gather current information before answering.

## What it demonstrates

This project implements the core **agentic pattern** — the THINK -> ACT -> OBSERVE
loop that distinguishes an agent from a simple LLM call:

1. **Think** — Claude reasons about what information it needs
2. **Act** — it calls the web_search tool with a query *it chooses itself*
3. **Observe** — it reads the returned search results
4. **Repeat** — it searches again if the answer isn't complete, then writes a
   final answer citing its sources

The loop continues until Claude decides it has enough information and returns a
final answer instead of requesting another tool.

## Architecture

```
USER question
     |
     v
+-----------------------------------------------+
|  AGENT LOOP (orchestration)                    |
|                                                |
|   LLM BRAIN (Claude)  --"search for X"-->      |
|        ^                                  |     |
|        |                                  v     |
|   reads results <--------  web_search TOOL      |
|        |                                        |
|   enough info? -> final answer ; else -> loop   |
+-----------------------------------------------+
     |
     v
Cited answer
```

**Three components:**
- **Brain** — Claude (Anthropic API) reasons and decides
- **Tool** — web_search (Tavily API) lets the agent act in the world
- **Loop** — the orchestration that cycles brain <-> tool until the task is done

The key design principle: **the LLM decides, the code executes.** Claude never
runs a tool directly — it *requests* a tool call, and the application code runs
the real function and feeds the result back. This separation is what makes
agentic tool use controllable and safe.

## Tech stack

- **Claude (Anthropic API)** — the reasoning engine, using its tool-calling feature
- **Tavily** — a web-search API designed for AI agents
- **Streamlit** — interactive UI that shows the agent's reasoning steps live, deployed on Streamlit Community Cloud

## Run it locally

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set your API keys (copy .env.example to .env and fill in your keys)
cp .env.example .env
#    then edit .env with your real keys

# 3a. Run from the command line
python agent.py

# 3b. Or launch the web UI
streamlit run app.py
```

Get a free Anthropic key at console.anthropic.com and a free Tavily key at tavily.com.

## Files

- agent.py — the core agent (tool, brain, and the think->act->observe loop)
- app.py — the Streamlit UI
- requirements.txt — dependencies
- .env.example — template for the required API keys

## Possible extensions

- Add more tools (calculator, Wikipedia, a code interpreter) — the architecture supports multiple tools cleanly
- Add conversation memory so it handles follow-up questions
- Stream the final answer token-by-token for a smoother UX
