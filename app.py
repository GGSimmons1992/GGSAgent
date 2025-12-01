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
from seleniumWebpageTool.seleniumWebpageTool import SeleniumWebpageTool
from wikipediaSearchTool.wikipediaSearchTool import WikipediaSearchTool


# Load environment variables
load_dotenv()

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
        SeleniumWebpageTool(),
        PythonInterpreterTool(),
        WikipediaSearchTool(),
    ]

    # Create and return the agent
    agent = CodeAgent(tools=tools, model=model)
    return agent


def process_query(prompt, file_input=None, history=None):
    """Process user query with optional file input and conversation history"""
    try:
        agent = initialize_agent()
        if history is None:
            history = []
        # Build conversation context
        conversation = ""
        for user_msg, agent_msg in history:
            conversation += f"User: {user_msg}\nAgent: {agent_msg}\n"
        conversation += f"User: {prompt}\nAgent:"
        full_prompt = conversation
        # If file is provided, add file information to the prompt
        if file_input is not None:
            file_path = (
                file_input.name if hasattr(file_input, "name") else str(file_input)
            )
            full_prompt += f"\n\nFile provided: {file_path}"
            try:
                if file_path.lower().endswith(".pdf"):
                    try:
                        import PyPDF2

                        with open(file_path, "rb") as f:
                            reader = PyPDF2.PdfReader(f)
                            pdf_text = ""
                            for page in reader.pages:
                                pdf_text += page.extract_text() or ""
                            if len(pdf_text) > 5000:
                                pdf_text = pdf_text[:5000] + "\n... (truncated)"
                            full_prompt += (
                                f"\n\nPDF content (extracted text):\n{pdf_text}"
                            )
                    except Exception as e:
                        full_prompt += f"\n\n(Could not extract PDF text: {str(e)})"
                else:
                    with open(file_path, "r", encoding="utf-8") as f:
                        file_content = f.read()
                        if len(file_content) > 5000:
                            file_content = file_content[:5000] + "\n... (truncated)"
                        full_prompt += f"\n\nFile content:\n{file_content}"
            except Exception as e:
                full_prompt += f"\n\n(Could not read file content: {str(e)})"
        result = agent.run(full_prompt)
        # Update history
        history = history + [(prompt, str(result))]
        return str(result), history
    except Exception as e:
        if history is None:
            history = []
        history = history + [(prompt, f"Error: {str(e)}")]
        return f"Error: {str(e)}", history


def create_interface():
    """Create and configure the Gradio interface"""

    # Create the Gradio interface with conversational memory
    interface = gr.Interface(
        fn=process_query,
        inputs=[
            gr.Textbox(label="Your Prompt", placeholder="Ask me anything...", lines=5),
            gr.File(label="Upload File (Optional)", type="filepath"),
            gr.State(),
        ],
        outputs=[gr.Textbox(label="Agent Response", lines=10), gr.State()],
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
            ["What is the capital of France?", None, None],
            ["Search the web for the latest news on AI", None, None],
            ["What does Wikipedia say about quantum computing?", None, None],
            [
                "Calculate the fibonacci sequence up to 10 numbers using Python",
                None,
                None,
            ],
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
