import os
import re

from crewai.tools import tool
from firecrawl import FirecrawlApp, ScrapeOptions


@tool
def web_search_tool(query: str):
    """
    Web Search Tool
    Args:
        query: str
            The query to search the web for
    Returns:
        A list of search results with the website content in markdown format
    """
    firecrawl = FirecrawlApp(api_key=os.getenv("FIRECRAWL_API_KEY"))

    response = firecrawl.search(
        query=query,
        limit=5,
        scrape_options=ScrapeOptions(
            formats=["markdown"],
        ),
    )

    cleaned_chunks = []

    if not response.success:
        return "Error using tool: " + response.error

    for result in response.data:

        title = result["title"]
        url = result["url"]
        markdown = result["markdown"]

        cleaned = re.sub(r"\\+|\n+", "", markdown).strip()
        cleaned = cleaned = re.sub(r"\[[^\]]+\]\([^\)]+\)|https?://[^\s]+", "", cleaned)

        cleaned_chunk = {"title": title, "url": url, "markdown": cleaned}

        cleaned_chunks.append(cleaned_chunk)

    return cleaned_chunks
