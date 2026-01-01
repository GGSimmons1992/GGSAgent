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
from jobTools.resumeTool import ResumeTool
from jobTools.portfolioTool import PortfolioTool
from jobTools.linkedinTool import LinkedInTool
from jobTools.jobFinderTool import JobFinderTool
from jobTools.jobApplyTool import JobApplyTool


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
        ResumeTool(),
        PortfolioTool(),
        LinkedInTool(),
        JobFinderTool(),
        JobApplyTool(),
        PythonInterpreterTool(),
        WikipediaSearchTool(),
    ]

    # Create and return the agent
    agent = CodeAgent(tools=tools, model=model)
    return agent


def process_query(
    prompt,
    file_input=None,
    resume_text: str = "",
    portfolio_url: str = "",
    linkedin_url: str = "",
    preferred_job_title: str = "",
    preferred_job_location: str = "",
    applicant_name: str = "",
    history=None,
):
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
        # If file is provided, add file information to the prompt and extract text
        if file_input is not None:
            file_path = (
                file_input.name if hasattr(file_input, "name") else str(file_input)
            )
            full_prompt += f"\n\nFile provided: {file_path}"
            extracted_text = ""
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
                            extracted_text = pdf_text
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
                        extracted_text = file_content
                        full_prompt += f"\n\nFile content:\n{file_content}"
            except Exception as e:
                full_prompt += f"\n\n(Could not read file content: {str(e)})"

            # If resume_text was not provided in the paste box, populate it from the uploaded file
            try:
                if not resume_text and extracted_text:
                    resume_text = extracted_text
            except Exception:
                # keep original resume_text on any unexpected error
                pass
        result = agent.run(full_prompt)
        # Call job-related tools directly if inputs provided
        resume_summary = ""
        portfolio_summary = ""
        linkedin_summary = ""
        job_finder_results = ""
        job_apply_results = ""
        try:
            if resume_text:
                resume_summary = str(ResumeTool().forward(resume_text))
        except Exception as e:
            resume_summary = f"Error running resume tool: {str(e)}"
        try:
            if portfolio_url:
                portfolio_summary = str(PortfolioTool().forward(portfolio_url))
        except Exception as e:
            portfolio_summary = f"Error running portfolio tool: {str(e)}"
        try:
            if linkedin_url:
                linkedin_summary = str(LinkedInTool().forward(linkedin_url))
        except Exception as e:
            linkedin_summary = f"Error running LinkedIn tool: {str(e)}"
        # If user provided preferred job title, run the JobFinderTool and optionally apply
        try:
            if preferred_job_title:
                finder = JobFinderTool()
                found = str(finder.forward(preferred_job_title, preferred_job_location))
                job_finder_results = found

                # Parse results into (title, url) pairs
                lines = [l.strip() for l in found.splitlines() if l.strip()]
                parsed = []
                for l in lines:
                    # Expect format like: "Title - URL" or just a URL
                    if " - " in l:
                        title, url = l.rsplit(" - ", 1)
                        parsed.append((title.strip(), url.strip()))
                    else:
                        parsed.append(("", l))

                # Score similarity using simple substring matching and difflib ratio
                import difflib

                scored = []
                pref_title = preferred_job_title.lower()
                pref_loc = (preferred_job_location or "").lower()
                for title, url in parsed:
                    score = 0.0
                    t = (title or "").lower()
                    if pref_title and pref_title in t:
                        score += 0.6
                    else:
                        # fuzzy match title
                        if t:
                            score += (
                                difflib.SequenceMatcher(None, pref_title, t).ratio()
                                * 0.6
                            )
                    if pref_loc:
                        if pref_loc in (t + " " + url.lower()):
                            score += 0.4
                    scored.append((score, title, url))

                # Select top 3 candidates with score > 0.25
                scored = sorted(scored, key=lambda x: x[0], reverse=True)
                candidates = [s for s in scored if s[0] > 0.25][:3]

                # For each candidate, prepare application materials using JobApplyTool
                applier = JobApplyTool()
                apply_outs = []
                for score, title, url in candidates:
                    try:
                        app_res = applier.forward(
                            url,
                            resume_text=resume_text or "",
                            applicant_name=applicant_name or "",
                        )
                        apply_outs.append(f"=== {title} - {url} ===\n{app_res}")
                    except Exception as e:
                        apply_outs.append(
                            f"Failed preparing application for {url}: {str(e)}"
                        )

                if apply_outs:
                    job_apply_results = "\n\n".join(apply_outs)
                else:
                    if parsed:
                        job_apply_results = (
                            "No matching jobs found based on similarity threshold.\nFound jobs:\n"
                            + "\n".join([u for _, u in parsed])
                        )
                    else:
                        job_apply_results = "No jobs found."
        except Exception as e:
            job_finder_results = f"Error running job finder/apply: {str(e)}"
        # Update history
        history = history + [(prompt, str(result))]
        return (
            str(result),
            resume_summary,
            portfolio_summary,
            linkedin_summary,
            job_finder_results,
            job_apply_results,
            history,
        )
    except Exception as e:
        if history is None:
            history = []
        history = history + [(prompt, f"Error: {str(e)}")]
        return f"Error: {str(e)}", "", "", "", "", "", history


def create_interface():
    """Create and configure the Gradio interface"""

    # Create the Gradio interface with conversational memory
    interface = gr.Interface(
        fn=process_query,
        inputs=[
            gr.Textbox(label="Your Prompt", placeholder="Ask me anything...", lines=5),
            gr.File(label="Upload File (Optional)", type="filepath"),
            gr.Textbox(
                label="Paste Resume Text (Optional)",
                placeholder="Paste resume or CV text here",
                lines=8,
            ),
            gr.Textbox(
                label="Portfolio URL (Optional)",
                placeholder="https://your-portfolio.com",
            ),
            gr.Textbox(
                label="LinkedIn URL (Optional)",
                placeholder="https://www.linkedin.com/in/yourprofile",
            ),
            gr.Textbox(
                label="Preferred Job Title (Optional)",
                placeholder="e.g. Backend Engineer, Data Scientist",
            ),
            gr.Textbox(
                label="Preferred Job Location (Optional)",
                placeholder="e.g. Remote, San Francisco, NY",
            ),
            gr.Textbox(
                label="Applicant Name (Optional)",
                placeholder="Your full name for cover letters",
            ),
            gr.State(),
        ],
        outputs=[
            gr.Textbox(label="Agent Response", lines=10),
            gr.Textbox(label="Resume Summary", lines=6),
            gr.Textbox(label="Portfolio Summary", lines=6),
            gr.Textbox(label="LinkedIn Summary", lines=6),
            gr.Textbox(label="Found Jobs", lines=6),
            gr.Textbox(label="Application Outputs", lines=12),
            gr.State(),
        ],
        title="GGSAgent - AI Agent Assistant",
        description="""
        An AI agent powered by smolagents with multiple tools:
        - DuckDuckGo Search
        - Web Page Visitor
        - Python Interpreter
        - Wikipedia Search
        - Resume / Portfolio / LinkedIn summarizers
        
        Ask questions, request web searches, code execution, or provide files for analysis.
        """,
        examples=[
            [
                "What is the capital of France?",
                None,
                None,
                None,
                None,
                None,
                None,
                None,
            ],
            [
                "Search the web for the latest news on AI",
                None,
                None,
                None,
                None,
                None,
                None,
                None,
            ],
            [
                "What does Wikipedia say about quantum computing?",
                None,
                None,
                None,
                None,
                None,
                None,
                None,
            ],
            [
                "Calculate the fibonacci sequence up to 10 numbers using Python",
                None,
                None,
                None,
                None,
                None,
                None,
                None,
            ],
            [
                "Summarize this resume",
                None,
                "John Doe\nEmail: john@example.com\nSkills: Python, AWS, Docker\nExperience: Worked on backend systems",
                None,
                None,
                None,
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
