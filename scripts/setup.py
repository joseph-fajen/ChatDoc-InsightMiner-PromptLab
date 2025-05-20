#!/usr/bin/env python3
"""
Setup script for the ChatDoc-InsightMiner-PromptLab

This script verifies and sets up the environment required for the toolkit to function.
It checks for required directories, Python packages, and configuration files.
"""

import os
import sys
import importlib.util
import subprocess
import shutil
from pathlib import Path
import re

# ANSI color codes for terminal output
GREEN = "\033[0;32m"
RED = "\033[0;31m"
YELLOW = "\033[0;33m"
BLUE = "\033[0;34m"
NC = "\033[0m"  # No color

def print_header(text):
    """Print a section header"""
    print(f"\n{BLUE}{'=' * 60}{NC}")
    print(f"{BLUE}# {text}{NC}")
    print(f"{BLUE}{'=' * 60}{NC}")

def print_status(label, status, message=None):
    """Print a status message with color"""
    if status == "OK":
        status_str = f"{GREEN}OK{NC}"
    elif status == "WARNING":
        status_str = f"{YELLOW}WARNING{NC}"
    elif status == "ERROR":
        status_str = f"{RED}ERROR{NC}"
    else:
        status_str = status
    
    print(f"{label:40} {status_str}")
    if message:
        print(f"  {message}")

def check_python_version():
    """Check if the Python version is supported"""
    import sys
    version = sys.version_info
    min_version = (3, 9)
    
    if version.major < min_version[0] or (version.major == min_version[0] and version.minor < min_version[1]):
        print_status("Python version", "ERROR", 
                    f"Python {min_version[0]}.{min_version[1]}+ required, found {version.major}.{version.minor}")
        return False
    else:
        print_status("Python version", "OK", f"Python {version.major}.{version.minor}.{version.micro}")
        return True

def check_package(package_name):
    """Check if a Python package is installed"""
    spec = importlib.util.find_spec(package_name)
    if spec is None:
        return False
    return True

def check_required_packages():
    """Check for required Python packages"""
    required_packages = [
        "pandas",
        "dotenv",
        "tqdm",
        "chromadb",
        "sentence_transformers",
        "numpy",
        "transformers",
        "anthropic",
        "openai",
        "google.generativeai",
        "aiohttp",
        "asyncio"
    ]
    
    all_packages_installed = True
    missing_packages = []
    
    for package in required_packages:
        try:
            # Special handling for modules with different import names
            if package == "dotenv":
                import_name = "dotenv"
                module_check = check_package("dotenv")
            elif package == "google.generativeai":
                import_name = "google.generativeai"
                try:
                    import google.generativeai
                    module_check = True
                except ImportError:
                    module_check = False
            else:
                import_name = package
                module_check = check_package(package)
                
            if module_check:
                print_status(f"Package: {import_name}", "OK")
            else:
                print_status(f"Package: {import_name}", "ERROR", "Not installed")
                missing_packages.append(package)
                all_packages_installed = False
        except Exception as e:
            print_status(f"Package: {package}", "ERROR", f"Error checking: {str(e)}")
            all_packages_installed = False
    
    if not all_packages_installed:
        print(f"\n{YELLOW}Some required packages are missing. Run:{NC}")
        print("  pip install -r requirements.txt")
    
    return all_packages_installed

def check_directories():
    """Check for required directories and create them if missing"""
    required_dirs = ["data", "docs", "logs", "outputs", "prompts", "vector_db"]
    root_dir = Path(__file__).parent.parent
    
    for dirname in required_dirs:
        dir_path = root_dir / dirname
        if dir_path.exists():
            print_status(f"Directory: {dirname}", "OK")
        else:
            print_status(f"Directory: {dirname}", "WARNING", "Creating directory")
            dir_path.mkdir(parents=True, exist_ok=True)

def check_env_file():
    """Check for .env file and create from .env.example if missing"""
    root_dir = Path(__file__).parent.parent
    env_path = root_dir / ".env"
    env_example_path = root_dir / ".env.example"
    
    if env_path.exists():
        print_status("Config: .env file", "OK")
        # Check if API keys are set
        with open(env_path, "r") as f:
            env_content = f.read()
            
        # Check for API keys
        api_keys = {
            "OPENAI_API_KEY": re.search(r'OPENAI_API_KEY\s*=\s*([^\s]+)', env_content),
            "ANTHROPIC_API_KEY": re.search(r'ANTHROPIC_API_KEY\s*=\s*([^\s]+)', env_content),
            "GEMINI_API_KEY": re.search(r'GEMINI_API_KEY\s*=\s*([^\s]+)', env_content)
        }
        
        missing_keys = []
        default_keys = []
        
        for key, match in api_keys.items():
            if not match:
                missing_keys.append(key)
            elif "your_" in match.group(1) or match.group(1) == "":
                default_keys.append(key)
        
        if missing_keys:
            print_status("API Keys", "WARNING", f"Missing keys in .env file: {', '.join(missing_keys)}")
        elif default_keys:
            print_status("API Keys", "WARNING", f"Default/placeholder keys detected: {', '.join(default_keys)}")
        else:
            print_status("API Keys", "OK", "All required API keys are set")
            
    elif env_example_path.exists():
        print_status("Config: .env file", "WARNING", "Creating .env from .env.example")
        shutil.copy(env_example_path, env_path)
        print(f"\n{YELLOW}Please edit the .env file to add your API keys.{NC}")
    else:
        print_status("Config: .env file", "ERROR", "Neither .env nor .env.example found")
        # Create a basic .env file
        with open(env_path, "w") as f:
            f.write("""# API Keys for LLM services
OPENAI_API_KEY=your_openai_key_here
ANTHROPIC_API_KEY=your_anthropic_key_here
GEMINI_API_KEY=your_gemini_key_here

# Vector database settings
VECTOR_DB_PATH=./vector_db
CHAT_COLLECTION_NAME=chat_messages
DOCS_COLLECTION_NAME=documentation
""")
        print(f"\n{YELLOW}Created a basic .env file. Please edit it to add your API keys.{NC}")

def check_sample_data():
    """Check for sample data files"""
    root_dir = Path(__file__).parent.parent
    
    # Check for chat data
    chat_data_path = root_dir / "data" / "chat_data.csv"
    if chat_data_path.exists():
        print_status("Sample data: chat_data.csv", "OK")
    else:
        print_status("Sample data: chat_data.csv", "WARNING", "No sample chat data found")
    
    # Check for documentation files
    docs_path = root_dir / "docs"
    doc_files = list(docs_path.glob("**/*.md")) + list(docs_path.glob("**/*.mdx"))
    
    if doc_files:
        print_status("Sample docs", "OK", f"Found {len(doc_files)} documentation file(s)")
    else:
        print_status("Sample docs", "WARNING", "No documentation files found")

def setup_environment():
    """Perform the complete environment setup"""
    print_header("MultiSource-TriLLM-Toolkit Setup")
    
    # Check Python version
    python_ok = check_python_version()
    if not python_ok:
        print(f"\n{RED}Error: Unsupported Python version{NC}")
        print("Please install Python 3.9 or later")
        return False
    
    # Check and create directories
    check_directories()
    
    # Check configuration files
    check_env_file()
    
    # Check sample data files
    check_sample_data()
    
    # Check required packages
    packages_ok = check_required_packages()
    
    # Display next steps
    print_header("Setup Results")
    
    if not packages_ok:
        print(f"{YELLOW}⚠️  Some packages are missing. Please install them using:{NC}")
        print("  pip install -r requirements.txt")
    
    print(f"\n{BLUE}Next steps:{NC}")
    print("1. Ensure your .env file contains valid API keys")
    print("2. Build the vector database:")
    print("   python scripts/build_vector_db.py")
    print("3. Add documentation to the vector database:")
    print("   python scripts/add_docs_to_vector_db.py")
    print("4. Run your first analysis:")
    print("   python scripts/multi_llm_combined_analyzer.py --prompt prompts/analysis_prompts/technical_issues.txt")
    print("\nOr run the demo script to see the full workflow:")
    print("   python scripts/run_demo.py")
    
    return True

if __name__ == "__main__":
    setup_environment()