#!/usr/bin/env python3
"""
Multi-LLM Combined Vector Database Analyzer

This script queries both the chat and documentation vector databases with a prompt template
and generates analysis using multiple LLM providers (OpenAI, Anthropic, and Google Gemini).
It allows for comprehensive analysis that leverages all available data sources.
"""

import os
import json
import logging
import argparse
import time
import asyncio
import aiohttp
from datetime import datetime
import chromadb
from chromadb.utils import embedding_functions
from dotenv import load_dotenv
import anthropic
import os

# Set environment variable to suppress tokenizers warning
os.environ["TOKENIZERS_PARALLELISM"] = "false"
import openai

# Set up logging
if not os.path.exists('logs'):
    os.makedirs('logs')
    
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join('logs', f'multi_llm_combined_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def ensure_directory(directory):
    """Ensure a directory exists"""
    if not os.path.exists(directory):
        os.makedirs(directory)
        logger.info(f"Created directory: {directory}")

def load_environment():
    """Load environment variables and validate required ones exist"""
    load_dotenv()
    required_vars = [
        'OPENAI_API_KEY', 
        'ANTHROPIC_API_KEY', 
        'GEMINI_API_KEY',
        'VECTOR_DB_PATH'
    ]
    
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
        return False
    return True

def load_prompt_from_file(prompt_file):
    """Load a prompt template from a file"""
    try:
        with open(prompt_file, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        logger.error(f"Error loading prompt file {prompt_file}: {e}")
        return None

async def query_openai(user_message, system_prompt=""):
    """Query the OpenAI API for analysis"""
    try:
        api_key = os.getenv("OPENAI_API_KEY")
        
        # Use the direct API call approach for consistency
        async with aiohttp.ClientSession() as session:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}"
            }
            
            model = os.getenv("OPENAI_MODEL", "gpt-4o")
            logger.info(f"Using OpenAI model: {model}")
            logger.info("Using direct API call for OpenAI")
            
            payload = {
                "model": model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                "temperature": 0.3,
                "max_tokens": 4000
            }
            
            async with session.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=payload
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    if "choices" in data and len(data["choices"]) > 0:
                        return data["choices"][0]["message"]["content"]
                    else:
                        logger.error(f"Unexpected OpenAI API response structure: {data}")
                        return "Error: Unexpected OpenAI API response structure"
                else:
                    error_text = await response.text()
                    logger.error(f"OpenAI API Error: {response.status} - {error_text}")
                    return f"Error generating OpenAI analysis: HTTP {response.status}"
        
    except Exception as e:
        logger.error(f"Error with OpenAI API: {e}")
        return f"Error generating OpenAI analysis: {str(e)}"

async def query_anthropic(user_message, system_prompt=""):
    """Query the Anthropic API for analysis"""
    try:
        api_key = os.getenv("ANTHROPIC_API_KEY")
        model = os.getenv("ANTHROPIC_MODEL", "claude-3-opus-20240229")
        logger.info(f"Using Anthropic model: {model}")
        
        # Use direct API call with a new session for each request
        logger.info("Using direct API call for Anthropic")
        connector = aiohttp.TCPConnector(ssl=False)
        async with aiohttp.ClientSession(connector=connector) as session:
            api_version = os.getenv("ANTHROPIC_API_VERSION", "2023-06-01")
            headers = {
                "Content-Type": "application/json",
                "x-api-key": api_key,
                "anthropic-version": api_version
            }
            
            payload = {
                "model": model,
                "max_tokens": 4000,
                "system": system_prompt,
                "messages": [
                    {"role": "user", "content": user_message}
                ]
            }
            
            async with session.post(
                "https://api.anthropic.com/v1/messages",
                headers=headers,
                json=payload,
                ssl=False
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    # Try different response formats
                    if "content" in data and len(data["content"]) > 0:
                        # New API format
                        if isinstance(data["content"][0], dict) and "text" in data["content"][0]:
                            return data["content"][0]["text"]
                        else:
                            # Try to extract text in other ways
                            return str(data["content"][0])
                    elif "completion" in data:
                        # Old API format
                        return data["completion"]
                    else:
                        # Last resort
                        return str(data)
                else:
                    error_text = await response.text()
                    logger.error(f"Anthropic API Error: {response.status} - {error_text}")
                    return f"Error generating Anthropic analysis: HTTP {response.status}"
                
    except Exception as e:
        logger.error(f"Error with Anthropic API: {e}")
        return f"Error generating Anthropic analysis: {str(e)}"

async def query_gemini(user_message, system_prompt=""):
    """Query the Google Gemini API for analysis"""
    try:
        api_key = os.getenv("GEMINI_API_KEY")
        
        # Use aiohttp for async HTTP requests
        async with aiohttp.ClientSession() as session:
            # Prepare the API request
            model = os.getenv("GEMINI_MODEL", "gemini-1.5-pro")
            logger.info(f"Using Gemini model: {model}")
            
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
            headers = {
                "Content-Type": "application/json"
            }
            
            # Construct the messages payload
            # Use Gemini's proper system prompt capability
            payload = {
                "contents": [
                    {"role": "user", "parts": [{"text": user_message}]}
                ],
                "system_instruction": {"parts": [{"text": system_prompt}]} if system_prompt else None,
                "generationConfig": {
                    "temperature": 0.3,
                    "maxOutputTokens": 4000,
                    "topP": 0.95
                }
            }
            
            # Remove None entries from contents
            payload["contents"] = [content for content in payload["contents"] if content is not None]
            
            # Add API key as query parameter
            params = {"key": api_key}
            
            # Send the request
            async with session.post(url, headers=headers, json=payload, params=params) as response:
                if response.status == 200:
                    response_data = await response.json()
                    
                    # Parse the response
                    if "candidates" in response_data and len(response_data["candidates"]) > 0:
                        generated_text = response_data["candidates"][0]["content"]["parts"][0]["text"]
                        return generated_text
                    else:
                        logger.error(f"Unexpected Gemini API response structure: {response_data}")
                        return "Error: Unexpected Gemini API response structure"
                else:
                    error_text = await response.text()
                    logger.error(f"Gemini API error: {response.status} - {error_text}")
                    return f"Error generating Gemini analysis: HTTP {response.status} - {error_text[:200]}"
                
    except Exception as e:
        logger.error(f"Error with Gemini API: {e}")
        return f"Error generating Gemini analysis: {str(e)}"

async def query_all_providers(user_message, system_prompt, providers=None):
    """Query selected LLM providers concurrently"""
    # Default to all providers if none specified
    if providers is None:
        providers = ["openai", "anthropic", "gemini"]
    
    # Map of provider names to their query functions
    provider_functions = {
        "openai": query_openai,
        "anthropic": query_anthropic,
        "gemini": query_gemini
    }
    
    # Create tasks for selected providers
    tasks = []
    selected_providers = []
    
    for provider in providers:
        if provider in provider_functions:
            tasks.append(provider_functions[provider](user_message, system_prompt))
            selected_providers.append(provider)
        else:
            logger.warning(f"Unknown provider: {provider}")
    
    if not tasks:
        logger.error("No valid providers selected")
        return {}
    
    # Run all tasks concurrently
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Convert exceptions to error messages
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            results[i] = f"Error: {str(result)}"
    
    # Combine results with provider names
    return dict(zip(selected_providers, results))

async def query_vector_database(prompt_template, k=30, output_dir="outputs", output_name=None):
    """Query the vector database with a prompt template and generate analyses using multiple LLMs"""
    # Load environment variables
    if not load_environment():
        return None
    
    db_path = os.getenv("VECTOR_DB_PATH")
    if not os.path.exists(db_path):
        logger.error(f"Vector database directory '{db_path}' not found")
        return None
    embedding_model = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
    
    # Ensure output directory exists
    ensure_directory(output_dir)
    
    try:
        # Set up the embedding function
        logger.info(f"Initializing embedding model: {embedding_model}")
        embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name=embedding_model
        )
        
        # Connect to the vector database
        logger.info(f"Connecting to vector database at: {db_path}")
        client = chromadb.PersistentClient(path=db_path)
        
        # Initialize containers for results
        all_documents = []
        all_metadata = []
        all_distances = []
        
        # Get the chat collection
        chat_collection_name = os.getenv("CHAT_COLLECTION_NAME", "chat_messages")
        logger.info(f"Using chat collection: {chat_collection_name}")
        try:
            chat_collection = client.get_collection(
                name=chat_collection_name,
                embedding_function=embedding_function
            )
            
            # Query the chat collection
            logger.info(f"Querying chat collection to find {k} relevant conversations...")
            chat_results = chat_collection.query(
                query_texts=[prompt_template],
                n_results=k,
                include=["documents", "metadatas", "distances"]
            )
            
            # Extract relevant conversations
            chat_documents = chat_results["documents"][0]
            chat_metadata = chat_results["metadatas"][0]
            chat_distances = chat_results["distances"][0]
            
            all_documents.extend(chat_documents)
            all_metadata.extend(chat_metadata)
            all_distances.extend(chat_distances)
            
            logger.info(f"Retrieved {len(chat_documents)} chat conversations")
            
        except Exception as e:
            logger.warning(f"Error accessing chat collection: {e}")
            logger.info("Chat collection may not exist. Make sure you've built the vector database using build_vector_db.py")
        
        # Get the Documentation collection
        docs_collection_name = os.getenv("DOCS_COLLECTION_NAME", "documentation")
        logger.info(f"Using Documentation collection: {docs_collection_name}")
        try:
            docs_collection = client.get_collection(
                name=docs_collection_name,
                embedding_function=embedding_function
            )
            
            # Query the Documentation collection
            logger.info(f"Querying Documentation collection to find {k} relevant documents...")
            docs_results = docs_collection.query(
                query_texts=[prompt_template],
                n_results=k,
                include=["documents", "metadatas", "distances"]
            )
            
            # Extract relevant documentation
            doc_documents = docs_results["documents"][0]
            doc_metadata = docs_results["metadatas"][0]
            doc_distances = docs_results["distances"][0]
            
            all_documents.extend(doc_documents)
            all_metadata.extend(doc_metadata)
            all_distances.extend(doc_distances)
            
            logger.info(f"Retrieved {len(doc_documents)} documentation chunks")
            
        except Exception as e:
            logger.warning(f"Error accessing Documentation collection: {e}")
            logger.info("Documentation collection may not exist. Make sure you've run add_docs_to_vector_db.py")
        
        if not all_documents:
            logger.error("No documents retrieved from any collection")
            return None
            
        # Sort all results by distance (similarity)
        sorted_results = sorted(zip(all_documents, all_metadata, all_distances), key=lambda x: x[2])
        
        # Unzip the sorted results
        sorted_documents, sorted_metadata, sorted_distances = zip(*sorted_results)
        
        # Use the sorted documents as our conversations
        conversations = sorted_documents
        metadata_list = sorted_metadata
        distances = sorted_distances
        
        logger.info(f"Retrieved {len(conversations)} total relevant chunks")
        
        # Format system prompt
        system_prompt = """
        You are an expert data analyst specializing in community feedback analysis and documentation.
        Your task is to analyze both official documentation and chat conversations to extract actionable insights.
        Focus on identifying patterns, categorizing issues, and providing concrete recommendations.
        
        When creating response documents:
        1. Prioritize information from official documentation over community conversations
        2. Use community conversations to identify common questions and pain points
        3. Format your output in a clear, structured manner with proper headings and sections
        4. For technical information, include code examples when relevant
        5. For command-line instructions, use proper formatting
        
        Use a professional, analytical tone and organize your findings clearly.
        """
        
        # Format each chunk with its source type (documentation or chat)
        formatted_chunks = []
        for i, (doc, meta) in enumerate(zip(conversations, metadata_list)):
            source_type = meta.get('source_type', '')
            if source_type == 'documentation':
                section = meta.get('section', 'Unknown Section')
                title = meta.get('title', 'Unknown Document')
                formatted_chunks.append(f"--- DOCUMENTATION: {title} - {section} ---\n{doc}")
            else:  # Chat or unknown
                formatted_chunks.append(f"--- CHAT CONVERSATION ---\n{doc}")
        
        # Manage token limits by truncating or chunking if needed
        # Estimate rough token count (approx 4 chars = 1 token)
        total_chars = sum(len(chunk) for chunk in formatted_chunks)
        estimated_tokens = total_chars / 4
        
        # If total estimated tokens exceeds a safe threshold (e.g., 12k tokens), truncate
        # This leaves room for prompt, system message, and model response
        max_tokens = int(os.getenv("MAX_INPUT_TOKENS", "12000"))
        
        if estimated_tokens > max_tokens:
            logger.warning(f"Content may exceed token limit ({estimated_tokens:.0f} est. tokens). Truncating.")
            
            # Truncate formatted chunks to fit within token limit
            token_budget = max_tokens
            selected_chunks = []
            for chunk in formatted_chunks:
                chunk_tokens = len(chunk) / 4
                if token_budget >= chunk_tokens:
                    selected_chunks.append(chunk)
                    token_budget -= chunk_tokens
                else:
                    # If we can't fit more complete chunks, break
                    break
            
            # Replace formatted chunks with truncated set
            formatted_chunks = selected_chunks
            logger.info(f"Reduced to {len(selected_chunks)}/{len(conversations)} chunks")
        
        # Join chunks with proper spacing
        content_text = "\n\n".join(formatted_chunks)
        
        # Format user message with conversations
        user_message = f"""
        The following are relevant chunks from documentation and chat conversations:

        {content_text}

        {prompt_template}
        """
        
        # Query all LLM providers
        logger.info("Sending requests to multiple LLM providers...")
        analyses = await query_all_providers(user_message, system_prompt)
        
        # Save the results
        if output_name is None:
            # Generate a more distinct name using first 20 chars + hash
            prompt_snippet = prompt_template.split("\n")[0][:20].strip()
            prompt_snippet = "".join(c if c.isalnum() else "_" for c in prompt_snippet)
            # Add a short hash for uniqueness
            import hashlib
            prompt_hash = hashlib.md5(prompt_template.encode()).hexdigest()[:6]
            output_name = f"multi_llm_{prompt_snippet}_{prompt_hash}"
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_base = os.path.join(output_dir, f"{output_name}_{timestamp}")
        
        # Save individual text analyses
        output_files = {}
        for provider, analysis in analyses.items():
            text_file = f"{output_base}_{provider}.txt"
            with open(text_file, "w", encoding="utf-8") as f:
                f.write(analysis)
            output_files[provider] = text_file
            
            # Print preview
            print(f"\n{provider.upper()} Analysis Preview:")
            print("=" * 80)
            preview = analysis[:300] + "..." if len(analysis) > 300 else analysis
            print(preview)
            print("=" * 80)
        
        # Save the full results with metadata
        json_file = f"{output_base}_combined.json"
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump({
                "prompt": prompt_template,
                "analyses": analyses,
                "sources": {
                    "documentation": sum(1 for m in sorted_metadata if m.get('source_type') == 'documentation'),
                    "chat": sum(1 for m in sorted_metadata if m.get('source_type') == 'chat')
                },
                "documents": list(sorted_documents),
                "metadata": [dict(m) for m in sorted_metadata],
                "distances": list(sorted_distances)
            }, f, indent=2)
        
        logger.info(f"Results saved to {json_file} and individual text files")
        print(f"\nFull results saved to: {json_file}")
        
        # Create a comparison markdown file
        comparison_file = f"{output_base}_comparison.md"
        with open(comparison_file, "w", encoding="utf-8") as f:
            f.write(f"# Multi-LLM Analysis Comparison\n\n")
            f.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"## Prompt\n\n```\n{prompt_template}\n```\n\n")
            
            for provider, analysis in analyses.items():
                f.write(f"## {provider.capitalize()} Analysis\n\n")
                f.write(f"```\n{analysis[:1000]}...\n```\n\n")
                f.write(f"[View full {provider} analysis](./{os.path.basename(output_files[provider])})\n\n")
        
        logger.info(f"Comparison saved to {comparison_file}")
        print(f"Comparison file: {comparison_file}")
        
        return {
            "json": json_file,
            "comparison": comparison_file,
            "text_files": output_files
        }
        
    except Exception as e:
        logger.error(f"Error querying vector database: {e}", exc_info=True)
        return None

async def run_all_prompts(prompts_dir="prompts"):
    """Run all prompts with multiple LLMs"""
    # Create necessary directories
    ensure_directory("logs")
    
    # Create a timestamp for this batch run
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    batch_dir = f"outputs/multi_llm_batch_{timestamp}"
    ensure_directory(batch_dir)
    
    # Get list of all prompt files
    if not os.path.exists(prompts_dir):
        logger.error(f"Prompts directory '{prompts_dir}' not found")
        return
    
    prompt_files = [f for f in os.listdir(prompts_dir) if f.endswith('.txt')]
    if not prompt_files:
        logger.error(f"No prompt files found in '{prompts_dir}'")
        return
    
    logger.info(f"Starting multi-LLM batch analysis with {len(prompt_files)} prompt templates")
    print(f"Starting multi-LLM batch analysis with {len(prompt_files)} prompt templates")
    print(f"Results will be saved to {batch_dir}")
    
    # Track results for summary
    results = []
    
    # Process each prompt
    for i, prompt_file in enumerate(sorted(prompt_files), 1):
        prompt_path = os.path.join(prompts_dir, prompt_file)
        output_name = f"multi_llm_{prompt_file.replace('.txt', '')}"
        
        logger.info(f"[{i}/{len(prompt_files)}] Running multi-LLM analysis with {prompt_file}...")
        print(f"\n[{i}/{len(prompt_files)}] Running multi-LLM analysis with {prompt_file}...")
        
        # Load the prompt
        prompt_template = load_prompt_from_file(prompt_path)
        if not prompt_template:
            logger.error(f"Failed to load prompt from {prompt_path}")
            results.append({
                "prompt": prompt_file,
                "status": "Failed",
                "error": "Failed to load prompt"
            })
            continue
        
        # Query the vector database
        try:
            output_files = await query_vector_database(
                prompt_template=prompt_template,
                output_dir=batch_dir,
                output_name=output_name
            )
            
            if output_files:
                results.append({
                    "prompt": prompt_file,
                    "status": "Success",
                    "outputs": output_files
                })
            else:
                logger.warning(f"No output files returned for {prompt_file}")
                results.append({
                    "prompt": prompt_file,
                    "status": "Failed",
                    "error": "No output files returned"
                })
        except Exception as e:
            logger.error(f"Error processing {prompt_file}: {e}", exc_info=True)
            results.append({
                "prompt": prompt_file,
                "status": "Failed",
                "error": str(e)
            })
        
        # Small delay to avoid rate limiting
        if i < len(prompt_files):
            delay = int(os.getenv("BATCH_DELAY_SECONDS", "5"))
            logger.info(f"Waiting {delay} seconds before next prompt...")
            print(f"Completed. Waiting {delay} seconds before next prompt...")
            await asyncio.sleep(delay)
    
    # Create a README for the batch run
    readme_path = os.path.join(batch_dir, "README.md")
    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(f"# Multi-LLM Combined Vector Analysis Batch Run\n\n")
        f.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write(f"This batch run analyzed data using multiple LLM providers:\n")
        f.write(f"- OpenAI (GPT-4o or similar)\n")
        f.write(f"- Anthropic (Claude 3 Opus or similar)\n")
        f.write(f"- Google Gemini API\n\n")
        
        f.write(f"## Summary\n\n")
        f.write(f"- Total prompts processed: {len(prompt_files)}\n")
        f.write(f"- Successful: {sum(1 for r in results if r['status'] == 'Success')}\n")
        f.write(f"- Failed: {sum(1 for r in results if r['status'] == 'Failed')}\n\n")
        
        f.write("## Results\n\n")
        for r in results:
            prompt_name = r['prompt'].replace('.txt', '')
            f.write(f"### {prompt_name}\n\n")
            f.write(f"- Status: {r['status']}\n")
            if r['status'] == 'Success':
                f.write(f"- Comparison: [{os.path.basename(r['outputs']['comparison'])}]({os.path.basename(r['outputs']['comparison'])})\n")
                f.write(f"- Full JSON: [{os.path.basename(r['outputs']['json'])}]({os.path.basename(r['outputs']['json'])})\n")
                f.write(f"- Individual analyses:\n")
                for provider, file_path in r['outputs']['text_files'].items():
                    f.write(f"  - [{provider.capitalize()}]({os.path.basename(file_path)})\n")
                f.write("\n")
            else:
                f.write(f"- Error: {r.get('error', 'Unknown error')}\n\n")
    
    logger.info(f"Multi-LLM batch processing complete!")
    print(f"\nMulti-LLM batch processing complete!")
    print(f"Results are saved in: {os.path.abspath(batch_dir)}")
    print(f"Summary available in: {os.path.abspath(readme_path)}")

def main():
    """Parse command line arguments and run the query"""
    parser = argparse.ArgumentParser(description='Multi-LLM Combined Vector Database Analyzer')
    parser.add_argument('--prompt', type=str, help='Path to the prompt template file')
    parser.add_argument('--k', type=int, default=30, help='Number of documents to retrieve from each source (default: 30)')
    parser.add_argument('--output', type=str, help='Name for the output file (without extension)')
    parser.add_argument('--list-prompts', action='store_true', help='List available prompt templates')
    parser.add_argument('--batch', action='store_true', help='Run all prompts in batch mode')
    parser.add_argument('--prompts-dir', type=str, default='prompts', help='Directory containing prompt templates')
    parser.add_argument('--providers', type=str, help='Comma-separated list of LLM providers to use (options: openai,anthropic,gemini)')
    args = parser.parse_args()
    
    # Create logs directory if it doesn't exist
    ensure_directory("logs")
    
    # List available prompts if requested
    if args.list_prompts:
        prompts_dir = args.prompts_dir
        if os.path.exists(prompts_dir) and os.path.isdir(prompts_dir):
            print("\nAvailable prompt templates:")
            for prompt_file in sorted(os.listdir(prompts_dir)):
                if prompt_file.endswith('.txt'):
                    print(f"  - {prompt_file}")
            print("\nUse with: python multi_llm_combined_analyzer.py --prompt prompts/template_name.txt")
        else:
            print("Prompts directory not found.")
        return
    
    # Run batch mode if requested
    if args.batch:
        asyncio.run(run_all_prompts(args.prompts_dir))
        return
    
    # Check if a prompt was specified
    if not args.prompt:
        parser.print_help()
        return
    
    # Check if the prompt file exists
    if not os.path.exists(args.prompt):
        logger.error(f"Prompt file {args.prompt} not found")
        return
    
    # Load the prompt template
    prompt_template = load_prompt_from_file(args.prompt)
    if not prompt_template:
        return
    
    # Parse providers if specified
    providers = None
    if args.providers:
        providers = [p.strip() for p in args.providers.split(',')]
        logger.info(f"Using specified providers: {providers}")
    
    # Query the vector database
    asyncio.run(query_vector_database(
        prompt_template=prompt_template,
        k=args.k,
        output_name=args.output
    ))

if __name__ == "__main__":
    main()