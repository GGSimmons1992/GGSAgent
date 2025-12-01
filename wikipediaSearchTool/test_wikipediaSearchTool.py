import unittest
from unittest.mock import patch, MagicMock
from wikipediaSearchTool import wikipediaSearchTool


class TestWikipediaSearchTool(unittest.TestCase):
    def setUp(self):
        self.tool = wikipediaSearchTool.WikipediaSearchTool()

    @patch("wikipediaSearchTool.wikipediaSearchTool.wikipedia")
    def test_successful_search(self, mock_wikipedia):
        mock_wikipedia.search.return_value = ["Python (programming language)"]
        mock_wikipedia.summary.return_value = "Python is a programming language."
        result = self.tool.forward("Python")
        self.assertIn("Wikipedia - Python (programming language):", result)
        self.assertIn("Python is a programming language.", result)

    @patch("wikipediaSearchTool.wikipediaSearchTool.wikipedia")
    def test_no_results(self, mock_wikipedia):
        mock_wikipedia.search.return_value = []
        result = self.tool.forward("asdkfjhasdkjfh")
        self.assertIn("No Wikipedia results found for 'asdkfjhasdkjfh'", result)

    @patch("wikipediaSearchTool.wikipediaSearchTool.wikipedia")
    def test_error_handling(self, mock_wikipedia):
        mock_wikipedia.search.side_effect = Exception("Some error")
        result = self.tool.forward("Python")
        self.assertIn("Error searching Wikipedia: Some error", result)


if __name__ == "__main__":
    unittest.main()
