"""
GGSAgent - A smolagents CodeAgent with Gradio interface
"""
import os
from dotenv import load_dotenv
import gradio as gr
from smolagents import (
    CodeAgent,
    LiteLLMModel,
    DuckDuckGoSearchTool,
    VisitWebpageTool,
    PythonInterpreterTool,
)
from smolagents.tools import Tool


# Load environment variables
load_dotenv()


class WikipediaSearchTool(Tool):
    """Tool for searching Wikipedia"""
    name = "wikipedia_search"
    description = "Search Wikipedia for information on a given topic. Returns a summary of the Wikipedia article."
    inputs = {
        "query": {
            "type": "string",
            "description": "The search query for Wikipedia"
        }
    }
    output_type = "string"
    
    def forward(self, query: str) -> str:
        """Search Wikipedia and return article summary"""
        try:
            import wikipedia
            # Search for the query
            results = wikipedia.search(query, results=1)
            if not results:
                return f"No Wikipedia results found for '{query}'"
            
            # Get the summary of the first result
            summary = wikipedia.summary(results[0], sentences=3)
            return f"Wikipedia - {results[0]}:\n{summary}"
        except Exception as e:
            return f"Error searching Wikipedia: {str(e)}"


def initialize_agent():
    """Initialize the CodeAgent with tools and model"""
    # Get API keys from environment
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    hf_token = os.getenv("HF_TOKEN")
    
    if not gemini_api_key:
        raise ValueError("GEMINI_API_KEY environment variable is required")
    
    # Set environment variable for LiteLLM
    os.environ["GEMINI_API_KEY"] = gemini_api_key
    if hf_token:
        os.environ["HF_TOKEN"] = hf_token
    
    # Initialize the LiteLLM model
    model = LiteLLMModel(model_id="gemini/gemini-2.5-flash")
    
    # Initialize tools
    tools = [
        DuckDuckGoSearchTool(),
        VisitWebpageTool(),
        PythonInterpreterTool(),
        WikipediaSearchTool(),
    ]
    
    # Create and return the agent
    agent = CodeAgent(tools=tools, model=model)
    return agent


def process_query(prompt: str, file_input=None):
    """Process user query with optional file input"""
    try:
        # Initialize agent
        agent = initialize_agent()
        
        # Prepare the full prompt
        full_prompt = prompt
        
        # If file is provided, add file information to the prompt
        if file_input is not None:
            file_path = file_input.name if hasattr(file_input, 'name') else str(file_input)
            full_prompt += f"\n\nFile provided: {file_path}"
            
            # Try to read the file content if it's a text file
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    file_content = f.read()
                    # Limit file content to avoid token limits
                    if len(file_content) > 5000:
                        file_content = file_content[:5000] + "\n... (truncated)"
                    full_prompt += f"\n\nFile content:\n{file_content}"
            except Exception as e:
                full_prompt += f"\n\n(Could not read file content: {str(e)})"
        
        # Run the agent
        result = agent.run(full_prompt)
        
        return str(result)
    
    except Exception as e:
        return f"Error: {str(e)}"


def create_interface():
    """Create and configure the Gradio interface"""
    
    # Create the Gradio interface
    interface = gr.Interface(
        fn=process_query,
        inputs=[
            gr.Textbox(
                label="Your Prompt",
                placeholder="Ask me anything...",
                lines=5
            ),
            gr.File(
                label="Upload File (Optional)",
                type="filepath"
            )
        ],
        outputs=gr.Textbox(
            label="Agent Response",
            lines=10
        ),
        title="GGSAgent - AI Agent Assistant",
        description="""
        An AI agent powered by smolagents with multiple tools:
        - DuckDuckGo Search
        - Web Page Visitor
        - Python Interpreter
        - Wikipedia Search
        
        Ask questions, request web searches, code execution, or provide files for analysis.
        """,
        examples=[
            ["What is the capital of France?", None],
            ["Search the web for the latest news on AI", None],
            ["What does Wikipedia say about quantum computing?", None],
            ["Calculate the fibonacci sequence up to 10 numbers using Python", None],
        ],
    )
    
    return interface


def main():
    """Main entry point"""
    # Check for required environment variables
    if not os.getenv("GEMINI_API_KEY"):
        print("WARNING: GEMINI_API_KEY not found in environment variables.")
        print("Please set it in a .env file or as an environment variable.")
        print("Example: GEMINI_API_KEY=your_api_key_here")
        return
    
    # Create and launch the interface
    interface = create_interface()
    interface.launch(server_name="0.0.0.0", server_port=7860, share=False)


if __name__ == "__main__":
    main()
