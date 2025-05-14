#!/usr/bin/env python3
"""
MultiSource-TriLLM-Toolkit - All-in-one script

This script provides a unified interface to all toolkit functionality:
- Setting up the environment
- Building vector databases from chat data
- Adding documentation to vector databases
- Running analyses with multiple LLMs

It simplifies the user experience by consolidating multiple scripts into one.
"""

import os
import sys
import argparse
import logging
import json
import subprocess
import time
import asyncio
import re
from datetime import datetime
from pathlib import Path

# Setup logging
if not os.path.exists('logs'):
    os.makedirs('logs')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join('logs', f'toolkit_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

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

def run_command(command, description):
    """Run a Python module as a subprocess"""
    print_header(description)
    print(f"Running: {command}\n")
    try:
        # If command is a module path, import and run it
        if command.startswith("scripts."):
            module_name = command
            # Convert to subprocess format
            cmd_parts = ["python", "-m", module_name]
            if len(command.split()) > 1:
                cmd_parts += command.split()[1:]
            
            result = subprocess.run(cmd_parts, check=True)
            return True
        else:
            # Otherwise run as shell command
            result = subprocess.run(command, shell=True, check=True, 
                                 stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                 universal_newlines=True)
            print(result.stdout)
            return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Error running command: {e}")
        if hasattr(e, 'stdout'):
            print(e.stdout)
        return False

def ensure_directory(directory):
    """Ensure a directory exists"""
    if not os.path.exists(directory):
        os.makedirs(directory)
        logger.info(f"Created directory: {directory}")

def check_setup():
    """Check if the environment is properly set up"""
    print_header("Checking environment setup")
    
    # Check if setup.py exists
    setup_script = os.path.join("scripts", "setup.py")
    if not os.path.exists(setup_script):
        logger.error(f"Setup script not found: {setup_script}")
        print(f"{RED}Setup script not found: {setup_script}{NC}")
        return False
    
    # Make executable
    os.chmod(setup_script, 0o755)
    
    # Run the setup script
    try:
        result = subprocess.run([sys.executable, setup_script], check=True)
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Setup failed: {e}")
        return False

def build_vector_db(args):
    """Build the chat vector database"""
    cmd = [sys.executable, "scripts/build_vector_db.py"]
    
    if args.csv:
        cmd.extend(["--csv", args.csv])
    if args.collection:
        cmd.extend(["--collection", args.collection])
    if args.force:
        cmd.append("--force")
    
    try:
        result = subprocess.run(cmd, check=True)
        print(f"{GREEN}Vector database built successfully!{NC}")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to build vector database: {e}")
        print(f"{RED}Failed to build vector database. Check the logs for details.{NC}")
        return False

def add_docs_to_vector_db(args):
    """Add documentation to the vector database"""
    cmd = [sys.executable, "scripts/add_docs_to_vector_db.py"]
    
    if args.docs_dir:
        cmd.extend(["--docs-dir", args.docs_dir])
    if args.collection:
        cmd.extend(["--collection", args.collection])
    if args.min_chunk:
        cmd.extend(["--min-chunk", str(args.min_chunk)])
    if args.max_chunk:
        cmd.extend(["--max-chunk", str(args.max_chunk)])
    if args.force:
        cmd.append("--force")
    
    try:
        result = subprocess.run(cmd, check=True)
        print(f"{GREEN}Documentation added to vector database successfully!{NC}")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to add documentation to vector database: {e}")
        print(f"{RED}Failed to add documentation to vector database. Check the logs for details.{NC}")
        return False

def run_analyzer(args):
    """Run the multi-LLM combined analyzer"""
    cmd = [sys.executable, "scripts/multi_llm_combined_analyzer.py"]
    
    if args.prompt:
        cmd.extend(["--prompt", args.prompt])
    if args.k:
        cmd.extend(["--k", str(args.k)])
    if args.output:
        cmd.extend(["--output", args.output])
    if args.batch:
        cmd.append("--batch")
    if args.prompts_dir:
        cmd.extend(["--prompts-dir", args.prompts_dir])
    if args.providers:
        cmd.extend(["--providers", args.providers])
    
    try:
        result = subprocess.run(cmd, check=True)
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to run analysis: {e}")
        print(f"{RED}Failed to run analysis. Check the logs for details.{NC}")
        return False

def run_single_llm_fallback(prompt_file, provider):
    """
    Run analysis with a single LLM provider as fallback when not all API keys are available
    """
    print_header(f"Running single-LLM analysis with {provider}")
    
    # Extract prompt content
    with open(prompt_file, 'r') as f:
        prompt_content = f.read()
    
    # Output setup
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = "outputs"
    ensure_directory(output_dir)
    
    prompt_name = os.path.basename(prompt_file).replace('.txt', '')
    output_file = os.path.join(output_dir, f"single_llm_{provider}_{prompt_name}_{timestamp}.txt")
    
    # Import specific modules based on provider
    if provider == "openai":
        try:
            import openai
            from dotenv import load_dotenv
            load_dotenv()
            
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                print(f"{RED}OpenAI API key not found in .env file{NC}")
                return False
                
            client = openai.OpenAI(api_key=api_key)
            
            model = os.getenv("OPENAI_MODEL", "gpt-4o")
            print(f"Using OpenAI model: {model}")
            
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are an expert data analyst."},
                    {"role": "user", "content": prompt_content}
                ],
                temperature=0.3,
                max_tokens=4000
            )
            
            analysis = response.choices[0].message.content
            
            with open(output_file, 'w') as f:
                f.write(analysis)
                
            print(f"{GREEN}Analysis complete! Results saved to {output_file}{NC}")
            return True
            
        except Exception as e:
            logger.error(f"Error with OpenAI API: {e}")
            print(f"{RED}Error generating OpenAI analysis: {str(e)}{NC}")
            return False
            
    elif provider == "anthropic":
        try:
            import anthropic
            from dotenv import load_dotenv
            load_dotenv()
            
            api_key = os.getenv("ANTHROPIC_API_KEY")
            if not api_key:
                print(f"{RED}Anthropic API key not found in .env file{NC}")
                return False
                
            client = anthropic.Anthropic(api_key=api_key)
            
            model = os.getenv("ANTHROPIC_MODEL", "claude-3-opus-20240229")
            print(f"Using Anthropic model: {model}")
            
            response = client.messages.create(
                model=model,
                max_tokens=4000,
                system="You are an expert data analyst.",
                messages=[
                    {"role": "user", "content": prompt_content}
                ]
            )
            
            analysis = response.content[0].text
            
            with open(output_file, 'w') as f:
                f.write(analysis)
                
            print(f"{GREEN}Analysis complete! Results saved to {output_file}{NC}")
            return True
            
        except Exception as e:
            logger.error(f"Error with Anthropic API: {e}")
            print(f"{RED}Error generating Anthropic analysis: {str(e)}{NC}")
            return False
            
    elif provider == "gemini":
        try:
            import google.generativeai as genai
            from dotenv import load_dotenv
            load_dotenv()
            
            api_key = os.getenv("GEMINI_API_KEY")
            if not api_key:
                print(f"{RED}Gemini API key not found in .env file{NC}")
                return False
                
            genai.configure(api_key=api_key)
            
            model_name = os.getenv("GEMINI_MODEL", "gemini-1.5-pro")
            print(f"Using Gemini model: {model_name}")
            
            model = genai.GenerativeModel(model_name)
            
            response = model.generate_content(
                contents=[prompt_content],
                generation_config={
                    "temperature": 0.3,
                    "max_output_tokens": 4000,
                    "top_p": 0.95
                },
            )
            
            analysis = response.text
            
            with open(output_file, 'w') as f:
                f.write(analysis)
                
            print(f"{GREEN}Analysis complete! Results saved to {output_file}{NC}")
            return True
            
        except Exception as e:
            logger.error(f"Error with Gemini API: {e}")
            print(f"{RED}Error generating Gemini analysis: {str(e)}{NC}")
            return False
    
    else:
        print(f"{RED}Unknown provider: {provider}{NC}")
        return False

def run_wizard():
    """Run an interactive setup wizard"""
    print_header("MultiSource-TriLLM-Toolkit Setup Wizard")
    print("This wizard will guide you through setting up and using the toolkit.")
    
    # Check environment setup
    print("\nStep 1: Checking environment setup...")
    if not check_setup():
        print(f"{RED}Environment setup failed. Please fix the issues and try again.{NC}")
        return False
    
    # Check for API keys
    from dotenv import load_dotenv
    load_dotenv()
    
    api_keys = {
        "OpenAI": os.getenv("OPENAI_API_KEY"),
        "Anthropic": os.getenv("ANTHROPIC_API_KEY"),
        "Gemini": os.getenv("GEMINI_API_KEY")
    }
    
    missing_keys = [name for name, key in api_keys.items() if not key or "your_" in key]
    
    if missing_keys:
        print(f"\n{YELLOW}Warning: Missing or default API keys for: {', '.join(missing_keys)}{NC}")
        print("You can continue, but some functionality will be limited.")
        
        answer = input("Would you like to add these API keys now? (y/n): ")
        if answer.lower() == 'y':
            env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")
            
            if "OpenAI" in missing_keys:
                openai_key = input("Enter your OpenAI API key (or press Enter to skip): ")
                if openai_key.strip():
                    with open(env_path, "r") as f:
                        content = f.read()
                    content = re.sub(r'OPENAI_API_KEY=.*', f'OPENAI_API_KEY={openai_key}', content)
                    with open(env_path, "w") as f:
                        f.write(content)
            
            if "Anthropic" in missing_keys:
                anthropic_key = input("Enter your Anthropic API key (or press Enter to skip): ")
                if anthropic_key.strip():
                    with open(env_path, "r") as f:
                        content = f.read()
                    content = re.sub(r'ANTHROPIC_API_KEY=.*', f'ANTHROPIC_API_KEY={anthropic_key}', content)
                    with open(env_path, "w") as f:
                        f.write(content)
            
            if "Gemini" in missing_keys:
                gemini_key = input("Enter your Gemini API key (or press Enter to skip): ")
                if gemini_key.strip():
                    with open(env_path, "r") as f:
                        content = f.read()
                    content = re.sub(r'GEMINI_API_KEY=.*', f'GEMINI_API_KEY={gemini_key}', content)
                    with open(env_path, "w") as f:
                        f.write(content)
            
            # Reload .env file
            load_dotenv(override=True)
            
            # Explicitly set environment variables
            if "OpenAI" in missing_keys and 'openai_key' in locals() and openai_key.strip():
                os.environ["OPENAI_API_KEY"] = openai_key
            if "Anthropic" in missing_keys and 'anthropic_key' in locals() and anthropic_key.strip():
                os.environ["ANTHROPIC_API_KEY"] = anthropic_key
            if "Gemini" in missing_keys and 'gemini_key' in locals() and gemini_key.strip():
                os.environ["GEMINI_API_KEY"] = gemini_key
    
    # Check for chat data
    print("\nStep 2: Checking for chat data...")
    chat_data_path = os.path.join("data", "chat_data.csv")
    
    if os.path.exists(chat_data_path):
        print(f"{GREEN}Found chat data at {chat_data_path}{NC}")
    else:
        print(f"{YELLOW}No chat data found at {chat_data_path}{NC}")
        print("You need chat data to build the vector database.")
        return False
    
    # Ask to build vector database
    print("\nStep 3: Building the vector database...")
    answer = input("Would you like to build/rebuild the vector database from chat data? (y/n): ")
    if answer.lower() == 'y':
        if build_vector_db(argparse.Namespace(csv=None, collection=None, force=False)):
            print(f"{GREEN}Vector database built successfully!{NC}")
        else:
            print(f"{RED}Failed to build vector database.{NC}")
            return False
    
    # Check for documentation
    print("\nStep 4: Checking for documentation...")
    docs_dir = "docs"
    doc_files = list(Path(docs_dir).glob("**/*.md")) + list(Path(docs_dir).glob("**/*.mdx"))
    
    if doc_files:
        print(f"{GREEN}Found {len(doc_files)} documentation file(s) in {docs_dir}{NC}")
        
        answer = input("Would you like to add documentation to the vector database? (y/n): ")
        if answer.lower() == 'y':
            if add_docs_to_vector_db(argparse.Namespace(docs_dir=docs_dir, collection=None, 
                                                      min_chunk=None, max_chunk=None, force=False)):
                print(f"{GREEN}Documentation added to vector database successfully!{NC}")
            else:
                print(f"{RED}Failed to add documentation to vector database.{NC}")
    else:
        print(f"{YELLOW}No documentation files found in {docs_dir}{NC}")
        print("You need documentation files to get the full benefit of the toolkit.")
    
    # List available prompts
    print("\nStep 5: Running analysis...")
    prompts_dir = "prompts"
    
    # Check available prompt files
    all_prompt_files = []
    for root, dirs, files in os.walk(prompts_dir):
        for file in files:
            if file.endswith('.txt'):
                prompt_path = os.path.join(root, file)
                all_prompt_files.append(prompt_path)
    
    if all_prompt_files:
        print(f"Available prompt templates:")
        for i, prompt_file in enumerate(all_prompt_files, 1):
            print(f"  {i}. {prompt_file}")
        
        try:
            prompt_index = int(input("\nSelect a prompt template (number): ")) - 1
            if 0 <= prompt_index < len(all_prompt_files):
                selected_prompt = all_prompt_files[prompt_index]
                print(f"Selected: {selected_prompt}")
                
                # Check which API keys are available
                available_providers = []
                if os.getenv("OPENAI_API_KEY") and "your_" not in os.getenv("OPENAI_API_KEY"):
                    available_providers.append("openai")
                if os.getenv("ANTHROPIC_API_KEY") and "your_" not in os.getenv("ANTHROPIC_API_KEY"):
                    available_providers.append("anthropic")
                if os.getenv("GEMINI_API_KEY") and "your_" not in os.getenv("GEMINI_API_KEY"):
                    available_providers.append("gemini")
                
                if len(available_providers) >= 3:
                    print("Running multi-LLM analysis with all providers...")
                    run_analyzer(argparse.Namespace(prompt=selected_prompt, k=30, output=None, 
                                                 batch=False, prompts_dir=None, providers=None))
                elif len(available_providers) > 0:
                    print(f"{YELLOW}Not all API keys are available. Using single-LLM fallback mode.{NC}")
                    provider_options = ", ".join(available_providers)
                    
                    if len(available_providers) == 1:
                        selected_provider = available_providers[0]
                    else:
                        provider_input = input(f"Select a provider ({provider_options}): ").lower()
                        if provider_input in available_providers:
                            selected_provider = provider_input
                        else:
                            selected_provider = available_providers[0]
                    
                    print(f"Using {selected_provider} for analysis...")
                    run_single_llm_fallback(selected_prompt, selected_provider)
                else:
                    print(f"{RED}No valid API keys found. Cannot run analysis.{NC}")
                    return False
            else:
                print(f"{RED}Invalid selection.{NC}")
        except ValueError:
            print(f"{RED}Invalid input. Please enter a number.{NC}")
    else:
        print(f"{RED}No prompt templates found in {prompts_dir}{NC}")
        return False
    
    print(f"\n{GREEN}Wizard completed successfully!{NC}")
    print("Check the outputs/ directory for results.")
    return True

def run_demo(args):
    """Run the demo workflow"""
    # Record start time
    start_time = time.time()
    
    print_header("MultiSource-TriLLM-Toolkit Demo")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Verify environment
    if not args.skip_setup:
        if not check_setup():
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
        if not build_vector_db(argparse.Namespace(csv=None, collection=None, force=False)):
            print("Failed to build chat vector database.")
            return False
        
        if not add_docs_to_vector_db(argparse.Namespace(docs_dir="docs", collection=None, 
                                                     min_chunk=None, max_chunk=None, force=False)):
            print("Failed to add documentation to vector database.")
            return False
    
    # Run analysis
    prompt_path = f"prompts/{args.prompt}"
    if not os.path.exists(prompt_path):
        print(f"Error: Prompt file {prompt_path} not found.")
        return False
    
    if not run_analyzer(argparse.Namespace(prompt=prompt_path, k=None, output=None, 
                                        batch=False, prompts_dir=None, providers=None)):
        print("Analysis failed.")
        return False
    
    # Calculate elapsed time
    elapsed_time = time.time() - start_time
    minutes, seconds = divmod(elapsed_time, 60)
    
    print_header("Demo Completed Successfully")
    print(f"Total time: {int(minutes)} minutes, {int(seconds)} seconds")
    print("Check the outputs/ directory for results.")
    
    return True

def convert_markdown(args):
    """Convert markdown file(s) to CSV"""
    cmd = [sys.executable, "scripts/md_to_csv_converter.py"]
    
    cmd.extend(["--input"] + args.input)
    cmd.extend(["--output", args.output])
    if args.track_source:
        cmd.append("--track-source")
    
    try:
        result = subprocess.run(cmd, check=True)
        print(f"{GREEN}Markdown file(s) converted to CSV successfully!{NC}")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to convert markdown to CSV: {e}")
        print(f"{RED}Failed to convert markdown to CSV. Check the logs for details.{NC}")
        return False

def main():
    """Main entry point for the toolkit"""
    parser = argparse.ArgumentParser(
        description="MultiSource-TriLLM-Toolkit - All-in-one interface",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Setup command
    setup_parser = subparsers.add_parser("setup", help="Set up the environment")
    
    # Wizard command
    wizard_parser = subparsers.add_parser("wizard", help="Run the interactive setup wizard")
    
    # Build vector database command
    build_parser = subparsers.add_parser("build", help="Build vector database from chat data")
    build_parser.add_argument('--csv', type=str, help="Path to CSV file containing chat messages")
    build_parser.add_argument('--collection', type=str, help="Name for the vector database collection")
    build_parser.add_argument('--force', action='store_true', help="Force rebuild if collection already exists")
    
    # Add docs command
    docs_parser = subparsers.add_parser("docs", help="Add documentation to vector database")
    docs_parser.add_argument('--docs-dir', type=str, help="Directory containing documentation files")
    docs_parser.add_argument('--collection', type=str, help="Name for the documentation collection")
    docs_parser.add_argument('--min-chunk', type=int, help="Minimum chunk size in characters")
    docs_parser.add_argument('--max-chunk', type=int, help="Maximum chunk size in characters")
    docs_parser.add_argument('--force', action='store_true', help="Force rebuild if collection already exists")
    
    # Analyze command
    analyze_parser = subparsers.add_parser("analyze", help="Run multi-LLM analysis")
    analyze_parser.add_argument('--prompt', type=str, help="Path to the prompt template file")
    analyze_parser.add_argument('--k', type=int, help="Number of documents to retrieve from each source")
    analyze_parser.add_argument('--output', type=str, help="Name for the output file (without extension)")
    analyze_parser.add_argument('--batch', action='store_true', help="Run all prompts in batch mode")
    analyze_parser.add_argument('--prompts-dir', type=str, help="Directory containing prompt templates")
    analyze_parser.add_argument('--providers', type=str, help="Comma-separated list of LLM providers to use")
    
    # Single-LLM fallback command
    fallback_parser = subparsers.add_parser("fallback", help="Run with a single LLM (fallback mode)")
    fallback_parser.add_argument('--prompt', type=str, required=True, help="Path to the prompt template file")
    fallback_parser.add_argument('--provider', type=str, required=True, 
                              choices=["openai", "anthropic", "gemini"],
                              help="LLM provider to use")
    
    # Markdown to CSV conversion command
    md2csv_parser = subparsers.add_parser("md2csv", help="Convert markdown file(s) to CSV")
    md2csv_parser.add_argument('--input', type=str, nargs='+', required=True, 
                             help="Path(s) to input markdown file(s)")
    md2csv_parser.add_argument('--output', type=str, required=True,
                             help="Path to output CSV file")
    md2csv_parser.add_argument('--track-source', action='store_true',
                             help="Add source column to CSV to track which file each record came from")
    
    # Demo command
    demo_parser = subparsers.add_parser("demo", help="Run the demo workflow")
    demo_parser.add_argument('--skip-setup', action='store_true', help="Skip setup steps")
    demo_parser.add_argument('--prompt', type=str, default="analysis_prompts/technical_issues.txt",
                          help="Prompt to use for the demo")
    
    # Parse arguments
    args = parser.parse_args()
    
    # If no arguments, print help
    if not args.command:
        parser.print_help()
        return 0
    
    # Ensure correct working directory
    # Get the directory containing this script, then go to parent directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(os.path.dirname(script_dir))
    
    # Create necessary directories
    ensure_directory("logs")
    ensure_directory("outputs")
    
    # Handle commands
    if args.command == "setup":
        success = check_setup()
    elif args.command == "wizard":
        success = run_wizard()
    elif args.command == "build":
        success = build_vector_db(args)
    elif args.command == "docs":
        success = add_docs_to_vector_db(args)
    elif args.command == "analyze":
        success = run_analyzer(args)
    elif args.command == "fallback":
        success = run_single_llm_fallback(args.prompt, args.provider)
    elif args.command == "md2csv":
        success = convert_markdown(args)
    elif args.command == "demo":
        success = run_demo(args)
    else:
        print(f"Unknown command: {args.command}")
        parser.print_help()
        return 1
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())