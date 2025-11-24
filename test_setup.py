"""
Test script to verify the GGSAgent setup
"""
import os
import sys

def test_imports():
    """Test that all required modules can be imported"""
    print("Testing imports...")
    try:
        import gradio
        print("✓ gradio imported")
        
        import litellm
        print("✓ litellm imported")
        
        from smolagents import CodeAgent, LiteLLMModel
        print("✓ smolagents CodeAgent and LiteLLMModel imported")
        
        from smolagents import DuckDuckGoSearchTool, VisitWebpageTool, PythonInterpreterTool
        print("✓ smolagents tools imported")
        
        import wikipedia
        print("✓ wikipedia imported")
        
        from dotenv import load_dotenv
        print("✓ python-dotenv imported")
        
        return True
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False


def test_tool_initialization():
    """Test that all tools can be initialized"""
    print("\nTesting tool initialization...")
    try:
        from smolagents import DuckDuckGoSearchTool, VisitWebpageTool, PythonInterpreterTool
        from app import WikipediaSearchTool
        
        tools = [
            DuckDuckGoSearchTool(),
            VisitWebpageTool(),
            PythonInterpreterTool(),
            WikipediaSearchTool(),
        ]
        
        print(f"✓ All {len(tools)} tools initialized successfully:")
        for tool in tools:
            print(f"  - {tool.name}")
        
        return True
    except Exception as e:
        print(f"✗ Tool initialization error: {e}")
        return False


def test_gradio_interface():
    """Test that the Gradio interface can be created"""
    print("\nTesting Gradio interface creation...")
    try:
        os.environ['GEMINI_API_KEY'] = 'test_key'  # Set a dummy key for testing
        from app import create_interface
        
        interface = create_interface()
        print(f"✓ Gradio interface created successfully")
        print(f"  - Title: {interface.title}")
        print(f"  - Number of inputs: {len(interface.input_components)}")
        print(f"  - Number of outputs: {len(interface.output_components)}")
        print(f"  - Number of examples: {len(interface.examples)}")
        
        return True
    except Exception as e:
        print(f"✗ Gradio interface error: {e}")
        return False


def test_environment_setup():
    """Test environment variable configuration"""
    print("\nTesting environment setup...")
    from dotenv import load_dotenv
    
    # Load .env if it exists
    load_dotenv()
    
    gemini_key = os.getenv("GEMINI_API_KEY")
    hf_token = os.getenv("HF_TOKEN")
    
    if gemini_key and gemini_key != 'test_key':
        print(f"✓ GEMINI_API_KEY found (length: {len(gemini_key)})")
    else:
        print("⚠ GEMINI_API_KEY not set (you'll need to set it to run the agent)")
    
    if hf_token:
        print(f"✓ HF_TOKEN found (length: {len(hf_token)})")
    else:
        print("ℹ HF_TOKEN not set (optional)")
    
    return True


def main():
    """Run all tests"""
    print("=" * 60)
    print("GGSAgent Setup Verification")
    print("=" * 60)
    
    results = []
    
    results.append(("Imports", test_imports()))
    results.append(("Tool Initialization", test_tool_initialization()))
    results.append(("Gradio Interface", test_gradio_interface()))
    results.append(("Environment Setup", test_environment_setup()))
    
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    for test_name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{test_name}: {status}")
    
    all_passed = all(result[1] for result in results)
    
    if all_passed:
        print("\n✓ All tests passed! Your setup is ready.")
        print("\nTo run the application:")
        print("  1. Set your GEMINI_API_KEY in .env file")
        print("  2. Run: python app.py")
        print("  3. Open http://localhost:7860 in your browser")
        return 0
    else:
        print("\n✗ Some tests failed. Please check the errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
