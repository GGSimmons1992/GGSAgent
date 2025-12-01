import wikipedia
from smolagents.tools import Tool


class WikipediaSearchTool(Tool):
    """Tool for searching Wikipedia"""

    name = "wikipedia_search"
    description = "Search Wikipedia for information on a given topic. Returns a summary of the Wikipedia article."
    inputs = {
        "query": {"type": "string", "description": "The search query for Wikipedia"}
    }
    output_type = "string"

    def forward(self, query: str) -> str:
        """Search Wikipedia and return article summary"""
        try:
            # Search for the query
            results = wikipedia.search(query, results=1)
            if not results:
                return f"No Wikipedia results found for '{query}'"

            # Get the summary of the first result
            summary = wikipedia.summary(results[0], sentences=3)
            return f"Wikipedia - {results[0]}:\n{summary}"
        except Exception as e:
            return f"Error searching Wikipedia: {str(e)}"
