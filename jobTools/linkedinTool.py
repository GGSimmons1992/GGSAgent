from smolagents.tools import Tool
import requests
from bs4 import BeautifulSoup


class LinkedInTool(Tool):
    """Tool for fetching public LinkedIn profile summary (best-effort)"""

    name = "linkedin_fetcher"
    description = "Fetch a public LinkedIn profile URL and return a summary of visible public info. Login-protected pages may not return full data."
    inputs = {"url": {"type": "string", "description": "LinkedIn profile URL"}}
    output_type = "string"

    def forward(self, url: str) -> str:
        try:
            resp = requests.get(url, timeout=10, headers={"User-Agent": "GGSAgent/1.0"})
            if resp.status_code != 200:
                return f"Failed to fetch {url}: status {resp.status_code}"
            soup = BeautifulSoup(resp.text, "html.parser")
            title = (
                soup.title.string.strip()
                if soup.title and soup.title.string
                else "(no title)"
            )
            # Try to extract intro text
            paragraphs = [
                p.get_text(strip=True) for p in soup.find_all(["p", "h1", "h2"])
            ][:20]
            content = " \n".join(paragraphs)
            if not content:
                content = "(no visible content; profile may require login)"
            return f"Title: {title}\n\nContent excerpt:\n{content[:4000]}"
        except Exception as e:
            return f"Error fetching LinkedIn profile: {str(e)}"
