from smolagents.tools import Tool
import requests
from bs4 import BeautifulSoup


class PortfolioTool(Tool):
    """Tool for fetching and summarizing a portfolio or personal site"""

    name = "portfolio_fetcher"
    description = "Fetch a portfolio URL and return a short summary of visible content and metadata."
    inputs = {"url": {"type": "string", "description": "Portfolio URL"}}
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
            # Meta description
            desc_tag = soup.find("meta", attrs={"name": "description"}) or soup.find(
                "meta", attrs={"property": "og:description"}
            )
            desc = desc_tag.get("content", "") if desc_tag else ""
            # Get visible text from main areas
            texts = []
            for tag in soup.find_all(["h1", "h2", "p", "li"]):
                t = tag.get_text(separator=" ", strip=True)
                if t:
                    texts.append(t)
                    if len(" ".join(texts)) > 4000:
                        break
            content = "\n".join(texts)[:4000]
            summary = f"Title: {title}\nMeta description: {desc}\n\nContent excerpt:\n{content}"
            return summary
        except Exception as e:
            return f"Error fetching portfolio: {str(e)}"
