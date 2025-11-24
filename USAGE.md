# Usage Guide for GGSAgent

## Quick Start

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Environment**
   
   Create a `.env` file in the project root:
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` and add your Gemini API key:
   ```
   GEMINI_API_KEY=your_actual_api_key_here
   ```

3. **Verify Setup**
   
   Run the setup verification test:
   ```bash
   python test_setup.py
   ```
   
   You should see all tests pass.

4. **Launch the Application**
   ```bash
   python app.py
   ```
   
   The Gradio interface will be available at `http://localhost:7860`

## Using the Interface

### Text Prompt
The main input field allows you to ask questions or give instructions to the agent. The agent has access to multiple tools:

- **DuckDuckGo Search**: For web searches
- **Web Page Visitor**: To visit and extract content from web pages
- **Python Interpreter**: To execute Python code
- **Wikipedia Search**: To search Wikipedia articles

### Example Queries

1. **Simple Questions**
   ```
   What is the capital of France?
   ```

2. **Web Search**
   ```
   Search the web for the latest news on artificial intelligence
   ```

3. **Wikipedia Lookup**
   ```
   What does Wikipedia say about quantum computing?
   ```

4. **Code Execution**
   ```
   Calculate the fibonacci sequence up to 10 numbers using Python
   ```

5. **Complex Tasks**
   ```
   Search for information about the Mars Rover mission, 
   then write a Python script to calculate the distance from Earth to Mars
   ```

### File Upload

You can upload text files (e.g., .txt, .py, .md, .csv) for the agent to analyze:

1. Click the "Upload File" button
2. Select your file
3. In the prompt, describe what you want the agent to do with the file

Example prompts with files:
- "Analyze this Python code and suggest improvements"
- "Summarize this document"
- "Find and fix any bugs in this code"
- "Create a visualization from this CSV data"

## Features

### Multi-Tool Agent
The CodeAgent can use multiple tools in sequence to accomplish complex tasks. For example:
- Search the web for information
- Visit specific web pages to get details
- Process the information with Python
- Look up additional facts on Wikipedia

### Conversation Memory
The agent maintains context within a single session, allowing for follow-up questions and iterative refinement.

### File Processing
When you upload a file, the agent can:
- Read and analyze the content
- Execute code if it's a script
- Process data files
- Generate reports or summaries

## Troubleshooting

### API Key Issues
If you see "GEMINI_API_KEY not found", make sure:
1. You created a `.env` file
2. The API key is correctly set in the `.env` file
3. The `.env` file is in the same directory as `app.py`

### Import Errors
If you get import errors, reinstall dependencies:
```bash
pip install -r requirements.txt --force-reinstall
```

### Gradio Not Starting
If Gradio fails to start:
1. Check if port 7860 is already in use
2. Try a different port by editing `app.py` and changing `server_port=7860`

### Tool Errors
If a specific tool fails:
- **DuckDuckGo Search**: Check your internet connection
- **Web Page Visitor**: Some websites may block automated access
- **Python Interpreter**: Ensure the code is valid Python
- **Wikipedia Search**: Check internet connection and query spelling

## Advanced Usage

### Custom Port
To run on a different port, modify `app.py`:
```python
interface.launch(server_name="0.0.0.0", server_port=8080, share=False)
```

### Public Sharing
To create a public link (useful for demos):
```python
interface.launch(server_name="0.0.0.0", server_port=7860, share=True)
```

### Environment Variables
You can set environment variables directly instead of using `.env`:
```bash
export GEMINI_API_KEY=your_key_here
export HF_TOKEN=your_token_here  # optional
python app.py
```

## Model Information

This application uses the **Gemini 2.5 Flash** model via LiteLLM. This model provides:
- Fast response times
- Good reasoning capabilities
- Support for multiple languages
- Cost-effective API calls

## Tips for Best Results

1. **Be Specific**: Provide clear, detailed instructions
2. **Use Tools**: Mention specific tools when needed (e.g., "search the web for...")
3. **Iterate**: Ask follow-up questions to refine results
4. **Check Output**: Always verify code execution results
5. **File Size**: Keep uploaded files under 5000 characters for best results

## Security Notes

- Never commit your `.env` file to version control
- Keep your API keys confidential
- Be cautious when executing code from untrusted sources
- Review any code before running it in production environments