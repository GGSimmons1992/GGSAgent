from smolagents.tools import Tool
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import shutil


class SeleniumWebpageTool(Tool):
    """Tool for fetching web pages with JavaScript using Selenium"""

    name = "selenium_webpage"
    description = "Fetch the rendered content of a web page using Selenium (supports JavaScript). Returns the visible text content."
    inputs = {
        "url": {"type": "string", "description": "The URL of the web page to fetch"}
    }
    output_type = "string"

    def forward(self, url: str) -> str:
        try:
            # Check if chromedriver is available
            chromedriver_path = shutil.which("chromedriver")
            if not chromedriver_path:
                return "ChromeDriver is not installed or not in PATH. Please install it to use this tool."
            options = Options()
            options.add_argument("--headless")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            driver = webdriver.Chrome(options=options)
            try:
                driver.get(url)
                # Wait for page to load
                driver.implicitly_wait(5)
                text = driver.find_element("tag name", "body").text
                if len(text) > 5000:
                    text = text[:5000] + "\n... (truncated)"
                return text
            finally:
                driver.quit()
        except Exception as e:
            return f"Error fetching page with Selenium: {str(e)}"
