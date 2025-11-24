# GGSAgent
My personal agentics agent powered by smolagents with Gradio interface

## Overview

GGSAgent is an AI-powered agent that uses smolagents' CodeAgent with multiple tools and a user-friendly Gradio interface. It leverages Google's Gemini model via LiteLLM to provide intelligent responses and execute various tasks.

## Features

- **Multiple Tools**: 
  - DuckDuckGo Search
  - Web Page Visitor
  - Python Interpreter
  - Wikipedia Search
  
- **Gradio Interface**: User-friendly web interface with:
  - Text prompt input
  - File upload capability
  - Example queries to get started

- **Powered by Gemini**: Uses Google's Gemini 2.0 Flash model via LiteLLM

## Setup

### Prerequisites

- Python 3.8 or higher
- Gemini API Key (get one from [Google AI Studio](https://makersuite.google.com/app/apikey))

### Installation

1. Clone the repository:
```bash
git clone https://github.com/GGSimmons1992/GGSAgent.git
cd GGSAgent
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. For Wikipedia search functionality, install the wikipedia package:
```bash
pip install wikipedia
```

4. Configure environment variables:
```bash
cp .env.example .env
```

Edit `.env` and add your API keys:
```
GEMINI_API_KEY=your_gemini_api_key_here
HF_TOKEN=your_hf_token_here  # Optional
```

## Usage

Run the application:
```bash
python app.py
```

The Gradio interface will launch at `http://localhost:7860`

### Example Queries

- "What is the capital of France?"
- "Search the web for the latest news on AI"
- "What does Wikipedia say about quantum computing?"
- "Calculate the fibonacci sequence up to 10 numbers using Python"

### File Upload

You can upload text files for the agent to analyze. The agent will read the file content and incorporate it into its response.

## Environment Variables

- `GEMINI_API_KEY` (Required): Your Gemini API key
- `HF_TOKEN` (Optional): HuggingFace token if needed

## License

See LICENSE file for details.
