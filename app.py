"""
Research Assistant Agent — Streamlit UI
=======================================
A simple web interface for the agent. Type a question, watch the agent
think -> search -> observe -> answer, and see its reasoning steps live.

Run with:  streamlit run app.py
"""

import streamlit as st
from agent import run_agent   # import the agent we built in agent.py

st.set_page_config(page_title="Research Assistant Agent", page_icon="🔎")

st.title("🔎 Research Assistant Agent")
st.caption(
    "An LLM agent that searches the web to answer your question. "
    "It decides what to search for, reads the results, and synthesizes a cited answer."
)

# A short explainer so viewers (and interviewers) understand what they're seeing
with st.expander("How it works"):
    st.markdown(
        "This agent runs a **think → act → observe** loop:\n\n"
        "1. **Think** — Claude reasons about what it needs\n"
        "2. **Act** — it calls the web-search tool with a query it chooses\n"
        "3. **Observe** — it reads the search results\n"
        "4. **Repeat** — it searches again if needed, then writes a final cited answer"
    )

# The input box
question = st.text_input(
    "Ask a question:",
    placeholder="e.g. What are the latest breakthroughs in battery technology?",
)

if st.button("Run Agent") and question:
    # A live area to show the agent's reasoning steps as they happen
    steps_box = st.container()
    step_log = []

    def show_step(msg):
        """Callback the agent calls on each step — appends to the live log."""
        step_log.append(msg)
        with steps_box:
            st.write(msg)

    # Run the agent, streaming its steps into the UI
    with st.spinner("The agent is researching..."):
        answer = run_agent(question, on_step=show_step)

    # Show the final answer
    st.subheader("Answer")
    st.markdown(answer)
