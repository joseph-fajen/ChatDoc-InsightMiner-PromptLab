#!/usr/bin/env python3
"""
Demo script to showcase the ChatDoc-InsightMiner-PromptLab
"""

import os
import sys
import subprocess
import time
import argparse
from datetime import datetime

def print_header(text):
    """Print a section header"""
    print("\n" + "=" * 80)
    print(f" {text}")
    print("=" * 80)

def run_command(command, description):
    """Run a shell command and print its output"""
    print_header(description)
    print(f"Running: {command}\n")
    try:
        result = subprocess.run(command, shell=True, check=True, 
                              stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                              universal_newlines=True)
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {e}")
        print(e.stdout)
        return False

def main():
    """Run a complete demo of the MultiSource-TriLLM-Toolkit"""
    parser = argparse.ArgumentParser(description="Run a demo of the MultiSource-TriLLM-Toolkit")
    parser.add_argument('--skip-setup', action='store_true', help="Skip setup steps (use if already set up)")
    parser.add_argument('--prompt', type=str, default="analysis_prompts/technical_issues.txt", 
                        help="Prompt to use for the demo (default: analysis_prompts/technical_issues.txt)")
    
    args = parser.parse_args()
    
    # Record start time
    start_time = time.time()
    
    # Ensure we're in the right directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(os.path.dirname(script_dir))  # Go to parent directory
    
    print_header("MultiSource-TriLLM-Toolkit Demo")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Working directory: {os.getcwd()}")
    
    # Verify environment
    if not args.skip_setup:
        print_header("Verifying setup")
        if not os.path.exists("scripts/verify_setup.sh"):
            print("Error: verify_setup.sh not found. Are you in the correct directory?")
            return False
        
        os.chmod("scripts/verify_setup.sh", 0o755)  # Make executable
        if not run_command("scripts/verify_setup.sh", "Verifying environment setup"):
            print("Setup verification failed. Please fix the issues and try again.")
            return False
    
    # Check for .env file
    if not os.path.exists(".env"):
        print("Warning: .env file not found. Creating from example...")
        if os.path.exists(".env.example"):
            with open(".env.example", "r") as src, open(".env", "w") as dst:
                dst.write(src.read())
            print("Created .env file from .env.example. Please edit it to add your API keys.")
        else:
            print("Error: .env.example not found. Please create a .env file with your API keys.")
            return False
    
    # Build vector databases
    if not args.skip_setup:
        if not run_command("python scripts/build_vector_db.py", "Building chat vector database"):
            print("Failed to build chat vector database.")
            return False
        
        if not run_command("python scripts/add_docs_to_vector_db.py", "Adding documentation to vector database"):
            print("Failed to add documentation to vector database.")
            return False
    
    # Run analysis
    prompt_path = f"prompts/{args.prompt}"
    if not os.path.exists(prompt_path):
        print(f"Error: Prompt file {prompt_path} not found.")
        return False
    
    if not run_command(f"python scripts/multi_llm_combined_analyzer.py --prompt {prompt_path}", 
                    f"Running analysis with prompt: {args.prompt}"):
        print("Analysis failed.")
        return False
    
    # Calculate elapsed time
    elapsed_time = time.time() - start_time
    minutes, seconds = divmod(elapsed_time, 60)
    
    print_header("Demo Completed Successfully")
    print(f"Total time: {int(minutes)} minutes, {int(seconds)} seconds")
    print("Check the outputs/ directory for results.")
    
    return True

if __name__ == "__main__":
    sys.exit(0 if main() else 1)