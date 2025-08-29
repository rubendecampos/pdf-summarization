import sys
import os
from dotenv import load_dotenv
from pathlib import Path

# Load .env file
load_dotenv()

def test_imports():
    """Test if all required packages can be imported"""
    print("Testing imports...")
    
    try:
        import langchain
        print("o langchain imported successfully")
    except ImportError as e:
        print(f"X langchain import failed: {e}")
        return False
    
    try:
        import openai
        print("o openai imported successfully")
    except ImportError as e:
        print(f"X openai import failed: {e}")
        return False
    
    try:
        import pypdf
        print("o pypdf imported successfully")
    except ImportError as e:
        print(f"X pypdf import failed: {e}")
        return False
    
    try:
        import faiss
        print("o faiss imported successfully")
    except ImportError as e:
        print(f"X faiss import failed: {e}")
        return False
    
    try:
        from main import PDFAnalyzer
        print("o PDFAnalyzer class imported successfully")
    except ImportError as e:
        print(f"X PDFAnalyzer import failed: {e}")
        return False
    
    return True

def test_folders():
    """Test if required folders exist"""
    print("\nTesting folder structure...")
    
    pdf_inputs = Path("pdf-inputs")
    outputs = Path("outputs")
    
    if pdf_inputs.exists():
        print("o pdf-inputs folder exists")
    else:
        print("X pdf-inputs folder missing")
        return False
    
    if outputs.exists():
        print("o outputs folder exists")
    else:
        print("X outputs folder missing")
        return False
    
    return True

def test_api_key():
    """Test if OpenAI API key is configured"""
    print("\nTesting API key configuration...")
    
    api_key = os.getenv('OPENAI_API_KEY')
    if api_key:
        print("o OPENAI_API_KEY environment variable is set")
        if api_key.startswith('sk-'):
            print("o API key format looks correct")
        else:
            print("Warning: API key format may be incorrect (should start with 'sk-')")
        return True
    else:
        print("Warning: OPENAI_API_KEY environment variable not set")
        print("  Set it with: export OPENAI_API_KEY='your-api-key-here'")
        print("  Or create a .env file with your API key")
        return False

def test_basic_functionality():
    """Test basic PDFAnalyzer functionality"""
    print("\nTesting basic functionality...")
    
    try:
        from main import PDFAnalyzer
        analyzer = PDFAnalyzer()
        print("o PDFAnalyzer instance created successfully")
        
        # Test folder creation
        if analyzer.input_folder.exists() and analyzer.output_folder.exists():
            print("o Analyzer folders initialized correctly")
        else:
            print("X Analyzer folder initialization failed")
            return False
        
        return True
    except Exception as e:
        print(f"X Basic functionality test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("PDF Analyzer Setup Test")
    print("=" * 30)
    
    tests = [
        ("Import Test", test_imports),
        ("Folder Structure Test", test_folders),
        ("API Key Test", test_api_key),
        ("Basic Functionality Test", test_basic_functionality)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"X {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 30)
    print("Test Results Summary:")
    print("=" * 30)
    
    all_passed = True
    for test_name, passed in results:
        status = "PASS" if passed else "FAIL"
        print(f"{test_name}: {status}")
        if not passed:
            all_passed = False
    
    print("\n" + "=" * 30)
    if all_passed:
        print("All tests passed!\n")
        print("Next steps:")
        print("1. Add PDF file to the 'pdf-inputs' folder")
        print("2. Run: python main.py")
    else:
        print("Some tests failed.\n")
        print("Common fixes:")
        print("1. Install dependencies: pip install -r requirements.txt")
        print("2. Set OpenAI API key: expot OPENAI_API_KEY='your-key'")
        print("3. Ensure using Python 3.8 or higher")

if __name__ == "__main__":
    main()
