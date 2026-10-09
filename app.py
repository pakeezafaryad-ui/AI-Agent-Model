
import os
import streamlit as st
from groq import Groq
from ddgs import DDGS

st.set_page_config(
    page_title="AI Research Agent",
    page_icon="🔎",
    layout="wide",
)

st.title("🔎 AI Research Agent")
st.write(
    "Enter a topic to search the web and generate "
    "an organized AI research report."
)

# Get the API key securely from Streamlit Secrets or environment
api_key = st.secrets.get("GROQ_API_KEY", None) if hasattr(st, "secrets") else None
api_key = api_key or os.getenv("GROQ_API_KEY")

def search_web(query):
    results = []

    with DDGS() as ddgs:
        for item in ddgs.text(query, max_results=6):
            results.append(
                {
                    "title": item.get("title", "Untitled"),
                    "url": item.get("href", ""),
                    "summary": item.get("body", ""),
                }
            )

    return results

def generate_report(topic, results, client):
    sources = "\n\n".join(
        f"Title: {item['title']}\n"
        f"URL: {item['url']}\n"
        f"Summary: {item['summary']}"
        for item in results
    )

    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[
            {
                "role": "system",
                "content": """
You are an AI research analyst.
Write a useful, well-structured Markdown research report.
Base factual claims on the provided search results.
Do not invent facts, statistics, quotations, or URLs.
Clearly explain limitations when evidence is insufficient.
Include a Sources section using only the supplied URLs.
"""
            },
            {
                "role": "user",
                "content": f"""
Research topic: {topic}

Use these web search results:
{sources}

Write the report with:
1. Title
2. Executive Summary
3. Introduction
4. Key Findings
5. Detailed Analysis
6. Challenges and Limitations
7. Conclusion
8. Sources
"""
            },
        ],
        temperature=0.2,
    )

    return response.choices[0].message.content

topic = st.text_input(
    "Research topic",
    placeholder="e.g. Applications of AI in education",
)

if st.button("Generate Research Report", type="primary"):
    if not api_key:
        st.error(
            "GROQ_API_KEY is missing. Add it under "
            "Streamlit app Settings → Secrets."
        )
    elif not topic.strip():
        st.warning("Please enter a research topic.")
    else:
        try:
            client = Groq(api_key=api_key)

            with st.spinner("Searching the web..."):
                results = search_web(topic)

            if not results:
                st.warning("No search results found. Try another topic.")
            else:
                with st.spinner("Writing your research report..."):
                    report = generate_report(topic, results, client)

                st.success("Research report generated!")
                st.markdown(report)

                with st.expander("View web search results"):
                    for item in results:
                        st.markdown(f"**[{item['title']}]({item['url']})**")
                        st.write(item["summary"])

                st.download_button(
                    "Download report as Markdown",
                    data=report,
                    file_name="research_report.md",
                    mime="text/markdown",
                )

        except Exception as error:
            st.error(f"Something went wrong: {error}")
            st.info(
                "Check your API key, package versions, "
                "and web-search availability."
            )
