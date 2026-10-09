
import os

import streamlit as st
from groq import Groq
from ddgs import DDGS


# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="AI Research Agent",
    page_icon="🔎",
    layout="wide",
)

st.title("🔎 AI Research Agent")
st.caption("AI-powered web research and report generation")

st.markdown(
    """
    Research any topic using web search and generate a structured
    report with key findings, analysis, limitations, and sources.
    """
)


# --------------------------------------------------
# API KEY CONFIGURATION
# --------------------------------------------------

def get_api_key():
    try:
        key = st.secrets.get("GROQ_API_KEY")
        if key:
            return key
    except Exception:
        pass

    return os.getenv("GROQ_API_KEY")


# --------------------------------------------------
# WEB SEARCH
# --------------------------------------------------

def search_web(query):
    results = []

    with DDGS() as ddgs:
        search_results = ddgs.text(query, max_results=6)

        for item in search_results:
            results.append(
                {
                    "title": item.get("title", "Untitled"),
                    "url": item.get("href", ""),
                    "summary": item.get("body", ""),
                }
            )

    return results


# --------------------------------------------------
# AI REPORT GENERATION
# --------------------------------------------------

def generate_report(topic, results, client):
    sources = "\n\n".join(
        (
            f"Title: {item['title']}\n"
            f"URL: {item['url']}\n"
            f"Summary: {item['summary']}"
        )
        for item in results
    )

    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[
            {
                "role": "system",
                "content": """
You are a careful AI research analyst.

Write clear, detailed, well-organized Markdown reports.
Base factual claims on the supplied search results.
Do not invent facts, statistics, quotations, or URLs.
Use only URLs provided in the search results.
Distinguish evidence from assumptions and explain limitations.
If the results do not support a claim, say so.
"""
            },
            {
                "role": "user",
                "content": f"""
Research topic: {topic}

Here are the web search results:

{sources}

Create a report using these sections:

# Title
## 1. Executive Summary
## 2. Introduction
## 3. Key Findings
## 4. Detailed Analysis
## 5. Challenges and Limitations
## 6. Conclusion
## 7. Sources

Use the search results to support the report.
Include relevant source URLs in the Sources section.
"""
            },
        ],
        temperature=0.2,
    )

    return response.choices[0].message.content


# --------------------------------------------------
# STREAMLIT USER INTERFACE
# --------------------------------------------------

topic = st.text_input(
    "Enter a research topic",
    placeholder="e.g. Applications of AI in education",
)

generate_button = st.button(
    "Generate Research Report",
    type="primary",
)

if generate_button:

    if not topic.strip():
        st.warning("Please enter a research topic.")

    else:
        api_key = get_api_key()

        if not api_key:
            st.error(
                "GROQ_API_KEY is missing. Open your Streamlit app settings, "
                "go to Secrets, and add your Groq API key."
            )

        else:
            try:
                client = Groq(api_key=api_key)

                with st.spinner("Searching the web..."):
                    results = search_web(topic)

                if not results:
                    st.warning(
                        "No search results were returned. "
                        "Please try another topic."
                    )

                else:
                    st.success(
                        f"Found {len(results)} search results."
                    )

                    with st.spinner(
                        "Analyzing information and writing your report..."
                    ):
                        report = generate_report(
                            topic,
                            results,
                            client,
                        )

                    st.success("Your research report is ready!")

                    st.markdown("---")
                    st.markdown(report)

                    st.download_button(
                        label="Download Research Report",
                        data=report,
                        file_name="research_report.md",
                        mime="text/markdown",
                    )

                    with st.expander("View Web Search Results"):
                        for index, item in enumerate(results, start=1):
                            st.markdown(
                                f"**{index}. [{item['title']}]"
                                f"({item['url']})**"
                            )
                            st.write(item["summary"])
                            st.markdown("---")

            except Exception as error:
                st.error(
                    "Something went wrong while generating the report."
                )
                st.code(str(error))
                st.info(
                    "Check your Groq API key, model availability, "
                    "internet connection, and installed dependencies."
                )


# --------------------------------------------------
# FOOTER
# --------------------------------------------------

st.markdown("---")
st.caption(
    "AI Research Agent | Powered by Streamlit, Groq, and DuckDuckGo Search"
)
