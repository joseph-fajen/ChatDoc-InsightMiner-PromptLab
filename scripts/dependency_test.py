#!/usr/bin/env python3
"""
Dependency Test Script for ChatDoc-InsightMiner-PromptLab

This script verifies that all required dependencies are properly installed
and basic functionality is working. It's intended to help identify any
issues with the setup before running the full pipeline.
"""

import os
import sys
import importlib
import subprocess
import unittest
import tempfile
import json
from pathlib import Path

# ANSI color codes for terminal output
GREEN = "\033[0;32m"
RED = "\033[0;31m"
YELLOW = "\033[0;33m"
BLUE = "\033[0;34m"
NC = "\033[0m"  # No color

def print_header(text):
    """Print a section header"""
    print(f"\n{BLUE}{'=' * 70}{NC}")
    print(f"{BLUE}# {text}{NC}")
    print(f"{BLUE}{'=' * 70}{NC}")

def print_result(name, success, message=None):
    """Print a test result with appropriate color"""
    if success:
        print(f"{GREEN}✓ {name}: PASS{NC}")
    else:
        print(f"{RED}✗ {name}: FAIL{NC}")
        if message:
            print(f"  {message}")

def check_python_version():
    """Check if Python version is 3.9 or higher"""
    required_version = (3, 9)
    current_version = sys.version_info
    
    if current_version >= required_version:
        print_result("Python Version", True)
        return True
    else:
        print_result("Python Version", False, 
                   f"Required: 3.9 or higher, Found: {sys.version.split()[0]}")
        return False

def check_dependencies():
    """Check if all required packages are installed"""
    required_packages = {
        "pandas": "pandas",
        "python-dotenv": "dotenv",
        "tqdm": "tqdm",
        "chromadb": "chromadb",
        "sentence-transformers": "sentence_transformers",
        "anthropic": "anthropic",
        "openai": "openai",
        "google-generativeai": "google.generativeai",
        "aiohttp": "aiohttp",
        "asyncio": "asyncio"
    }
    
    all_installed = True
    
    for package_name, import_name in required_packages.items():
        try:
            module = importlib.import_module(import_name)
            if hasattr(module, '__version__'):
                version = module.__version__
            else:
                version = "Unknown"
            print_result(f"{package_name} ({version})", True)
        except ImportError as e:
            all_installed = False
            print_result(package_name, False, str(e))
    
    return all_installed

def check_directory_structure():
    """Check if the project directory structure is valid"""
    required_dirs = ["data", "docs", "prompts", "scripts", "tests", "outputs", "vector_db", "logs"]
    missing_dirs = []
    
    for dir_name in required_dirs:
        if not os.path.isdir(dir_name):
            missing_dirs.append(dir_name)
    
    if not missing_dirs:
        print_result("Directory Structure", True)
        return True
    else:
        print_result("Directory Structure", False, 
                   f"Missing directories: {', '.join(missing_dirs)}")
        return False

def check_env_file():
    """Check if .env file exists or can be created from template"""
    if os.path.exists(".env"):
        print_result("Environment File", True)
        return True
    elif os.path.exists(".env.example"):
        print(f"{YELLOW}Warning: .env file not found, but .env.example exists.{NC}")
        print(f"{YELLOW}Run 'cp .env.example .env' and add your API keys.{NC}")
        return True
    else:
        print_result("Environment File", False, 
                   "Neither .env nor .env.example files found.")
        return False

def check_sample_data():
    """Check if sample data files exist"""
    sample_files = {
        "Chat Data": "data/chat_data.csv",
        "Sample Markdown": "sample-markdown-file.md",
        "Documentation": "docs/monitoring-dashboard.md"
    }
    
    all_exist = True
    
    for name, path in sample_files.items():
        if os.path.exists(path):
            print_result(f"Sample {name}", True)
        else:
            all_exist = False
            print_result(f"Sample {name}", False, f"File not found: {path}")
    
    return all_exist

def create_test_files():
    """Create temporary test files for validation"""
    temp_dir = tempfile.gettempdir()
    
    # Create a simple markdown test file
    md_content = """
User1 — 01/15/24, 10:30 AM
This is a test message

User2 — 01/15/24, 10:35 AM
This is a response to the test message
"""
    md_file = os.path.join(temp_dir, "test_conversation.md")
    with open(md_file, "w") as f:
        f.write(md_content)
    
    return {"md_file": md_file}

def clean_test_files(files):
    """Clean up temporary test files"""
    for name, path in files.items():
        if os.path.exists(path):
            os.remove(path)

def check_md_to_csv_conversion(test_files):
    """Test the markdown to CSV conversion functionality"""
    md_file = test_files["md_file"]
    output_csv = os.path.join(tempfile.gettempdir(), "test_output.csv")
    
    try:
        result = subprocess.run(
            [sys.executable, "scripts/md_to_csv_converter.py", "--input", md_file, "--output", output_csv],
            check=True,
            capture_output=True,
            text=True
        )
        
        if os.path.exists(output_csv):
            # Clean up the output file
            os.remove(output_csv)
            print_result("Markdown to CSV Conversion", True)
            return True
        else:
            print_result("Markdown to CSV Conversion", False, "Output file not created")
            return False
            
    except subprocess.CalledProcessError as e:
        print_result("Markdown to CSV Conversion", False, 
                   f"Command failed with error: {e.stderr}")
        return False

def check_toolkit_module():
    """Test that the main toolkit script can be imported"""
    try:
        import scripts.toolkit
        print_result("Toolkit Module", True)
        return True
    except ImportError as e:
        print_result("Toolkit Module", False, str(e))
        return False

def check_test_suite():
    """Check if the test suite runs without errors"""
    try:
        loader = unittest.TestLoader()
        test_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tests")
        suite = loader.discover(test_dir, pattern="test_*.py")
        
        runner = unittest.TextTestRunner(verbosity=0)
        result = runner.run(suite)
        
        if result.wasSuccessful():
            print_result("Test Suite", True)
            return True
        else:
            print_result("Test Suite", False, 
                       f"Failed tests: {len(result.failures)}, Errors: {len(result.errors)}")
            return False
    except Exception as e:
        print_result("Test Suite", False, str(e))
        return False

def check_api_keys():
    """Check if any API keys are configured"""
    # Try to load .env file
    try:
        from dotenv import load_dotenv
        load_dotenv()
        
        api_keys = {
            "OpenAI": os.getenv("OPENAI_API_KEY"),
            "Anthropic": os.getenv("ANTHROPIC_API_KEY"),
            "Gemini": os.getenv("GEMINI_API_KEY")
        }
        
        valid_keys = {name: (key and not key.startswith("your_")) 
                     for name, key in api_keys.items()}
        
        if any(valid_keys.values()):
            valid_providers = [name for name, is_valid in valid_keys.items() if is_valid]
            print_result("API Keys", True, 
                       f"Found valid keys for: {', '.join(valid_providers)}")
            return True
        else:
            print_result("API Keys", False, 
                       "No valid API keys found. Add at least one key to .env file.")
            return False
            
    except ImportError:
        print_result("API Keys", False, "Could not load dotenv module")
        return False

def run_validation_tests():
    """Run all validation tests and return overall success status"""
    print_header("ChatDoc-InsightMiner-PromptLab Validation Tests")
    
    # Track validation status
    validation_results = {}
    
    # Basic environment checks
    validation_results["python_version"] = check_python_version()
    validation_results["dependencies"] = check_dependencies()
    validation_results["directory_structure"] = check_directory_structure()
    validation_results["env_file"] = check_env_file()
    validation_results["sample_data"] = check_sample_data()
    
    # Create temporary test files
    test_files = create_test_files()
    
    # Functional tests
    validation_results["toolkit_module"] = check_toolkit_module()
    validation_results["md_to_csv"] = check_md_to_csv_conversion(test_files)
    validation_results["test_suite"] = check_test_suite()
    validation_results["api_keys"] = check_api_keys()
    
    # Clean up test files
    clean_test_files(test_files)
    
    # Calculate overall success
    all_passed = all(validation_results.values())
    some_passed = any(validation_results.values())
    
    # Print summary
    print_header("Validation Summary")
    
    for test_name, result in validation_results.items():
        formatted_name = " ".join(word.capitalize() for word in test_name.split("_"))
        print_result(formatted_name, result)
    
    # Print overall status
    if all_passed:
        print(f"\n{GREEN}All validation tests passed! The toolkit is ready to use.{NC}")
    elif some_passed:
        print(f"\n{YELLOW}Some validation tests failed. Review the errors above before proceeding.{NC}")
    else:
        print(f"\n{RED}All validation tests failed. The toolkit is not properly set up.{NC}")
    
    # Print next steps
    print_header("Next Steps")
    
    if all_passed:
        print("1. Run a full end-to-end test with:")
        print("   python scripts/toolkit.py demo")
    else:
        print("1. Fix the failed validation tests")
        print("2. Run this validation script again")
        print("3. Check the TESTING.md file for more detailed testing instructions")
    
    return all_passed

if __name__ == "__main__":
    # Ensure we're running from the project root directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(os.path.dirname(script_dir))
    
    # Run all validation tests
    success = run_validation_tests()
    
    # Exit with appropriate status code
    sys.exit(0 if success else 1)