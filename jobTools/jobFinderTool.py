from smolagents.tools import Tool
import requests
from bs4 import BeautifulSoup
import urllib.parse


class JobFinderTool(Tool):
    """Find job postings using DuckDuckGo HTML search as a lightweight scraper"""

    name = "job_finder"
    description = "Search for job postings for a given title and location and return top result links and snippets."
    inputs = {
        "job_title": {"type": "string", "description": "Desired job title"},
        "location": {
            "type": "string",
            "description": "Location (city, remote, etc.) (optional)",
            "nullable": True,
        },
    }
    output_type = "string"

    def forward(self, job_title: str, location: str = "") -> str:
        try:
            query = f"{job_title} {location} jobs".strip()
            q = urllib.parse.quote_plus(query)
            url = f"https://html.duckduckgo.com/html/?q={q}"
            resp = requests.get(url, timeout=10, headers={"User-Agent": "GGSAgent/1.0"})
            if resp.status_code != 200:
                return f"Search failed: status {resp.status_code}"
            soup = BeautifulSoup(resp.text, "html.parser")
            links = []
            for a in soup.find_all("a", href=True):
                href = a["href"]
                # duckduckgo returns result links in various formats; filter reasonable http(s) links
                if href.startswith("/l/?kh="):
                    # duckduckgo redirect - try to extract 'uddg' param
                    parsed = urllib.parse.urlparse(href)
                    qs = urllib.parse.parse_qs(parsed.query)
                    if "uddg" in qs:
                        real = qs["uddg"][0]
                        links.append(real)
                elif href.startswith("http"):
                    links.append(href)
                if len(links) >= 10:
                    break

            # Deduplicate while preserving order
            seen = set()
            dedup = []
            for l in links:
                if l not in seen:
                    seen.add(l)
                    dedup.append(l)

            # For each, try to fetch short snippet header
            results = []
            for link in dedup[:5]:
                try:
                    r = requests.get(
                        link, timeout=6, headers={"User-Agent": "GGSAgent/1.0"}
                    )
                    title = "(no title)"
                    if r.status_code == 200:
                        s = BeautifulSoup(r.text, "html.parser")
                        if s.title and s.title.string:
                            title = s.title.string.strip()
                    results.append(f"{title} - {link}")
                except Exception:
                    results.append(link)

            if not results:
                return "No job links found for query: " + query
            return "\n".join(results)
        except Exception as e:
            return f"Error finding jobs: {str(e)}"
