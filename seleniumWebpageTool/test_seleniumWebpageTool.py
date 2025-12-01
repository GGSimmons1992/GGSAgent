

import unittest
from unittest.mock import patch, MagicMock
from seleniumWebpageTool.seleniumWebpageTool import SeleniumWebpageTool


class TestSeleniumWebpageTool(unittest.TestCase):
    def setUp(self):
        self.tool = SeleniumWebpageTool()

    @patch("seleniumWebpageTool.seleniumWebpageTool.shutil.which")
    def test_chromedriver_not_installed(self, mock_which):
        mock_which.return_value = None
        result = self.tool.forward("http://example.com")
        self.assertIn("ChromeDriver is not installed", result)

    @patch(
        "seleniumWebpageTool.seleniumWebpageTool.shutil.which",
        return_value="/usr/bin/chromedriver",
    )
    @patch("seleniumWebpageTool.seleniumWebpageTool.webdriver.Chrome")
    def test_successful_fetch(self, mock_chrome, mock_which):
        mock_driver = MagicMock()
        mock_driver.find_element.return_value.text = "Hello World"
        mock_chrome.return_value = mock_driver
        result = self.tool.forward("http://example.com")
        self.assertEqual(result, "Hello World")
        mock_driver.get.assert_called_with("http://example.com")
        mock_driver.quit.assert_called_once()

    @patch(
        "seleniumWebpageTool.seleniumWebpageTool.shutil.which",
        return_value="/usr/bin/chromedriver",
    )
    @patch(
        "seleniumWebpageTool.seleniumWebpageTool.webdriver.Chrome",
        side_effect=Exception("webdriver error"),
    )
    def test_selenium_exception(self, mock_chrome, mock_which):
        result = self.tool.forward("http://example.com")
        self.assertIn("Error fetching page with Selenium", result)


if __name__ == "__main__":
    unittest.main()
