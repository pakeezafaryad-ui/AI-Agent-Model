import streamlit as st
from research_agent import ResearchAgentError, run_research

st.set_page_config(
    page_title="AI Research Agent",
    page_icon="🔎",
    layout="wide",
)

st.title("🔎 AI Research Agent")
st.write(
    "Enter a topic and the agent will search the web, organize the findings, "
    "and create a research report with source links."
)

with st.sidebar:
    st.header("About")
    st.write("Powered by CrewAI, Groq, and DuckDuckGo search.")
    st.caption("Research results can contain errors. Always verify important claims against the linked sources.")

topic = st.text_area(
    "Research topic",
    placeholder="For example: How is artificial intelligence changing education?",
    height=110,
)
run_button = st.button("Research topic", type="primary", use_container_width=True)

if run_button:
    if not topic.strip():
        st.warning("Please enter a research topic first.")
    else:
        try:
            with st.status("Researching your topic… This may take a few minutes.", expanded=True) as status:
                st.write("Connecting to the research agent and searching the web.")
                report = run_research(topic.strip())
                status.update(label="Research complete", state="complete", expanded=False)

            st.subheader("Research report")
            st.markdown(report)
            st.download_button(
                label="Download report (.md)",
                data=report,
                file_name="research_report.md",
                mime="text/markdown",
                use_container_width=True,
            )
        except ResearchAgentError as exc:
            st.error(str(exc))
        except Exception as exc:
            st.error("Something unexpected went wrong.")
            st.caption("Technical details (share these if you need help):")
            st.code(f"{type(exc).__name__}: {exc}")

st.divider()
st.caption("Tip: use a focused topic for clearer findings. This app is an educational prototype, not a substitute for expert research.")
