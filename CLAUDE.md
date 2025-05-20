# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

ChatDoc InsightMiner PromptLab is a Python toolkit for analyzing multiple data sources (chat messages and documentation) using vector databases and comparative LLM evaluation. The toolkit builds vector databases from chat data and documentation, queries them with specialized prompts, and compares responses from multiple LLMs (OpenAI, Anthropic, and Google Gemini).

## Prerequisites

- Python 3.9+
- API keys for OpenAI, Anthropic, and Google Gemini (for multi-LLM features)

## Commands

### Setting Up

```bash
# Install requirements
pip install -r requirements.txt

# Create .env file (if you don't have one)
cp .env.example .env

# Verify environment setup
python scripts/toolkit.py setup

# Run the interactive setup wizard
python scripts/toolkit.py wizard
```

### Building Vector Databases

```bash
# Build vector database from chat data
python scripts/toolkit.py build

# Add documentation to vector database
python scripts/toolkit.py docs

# Force rebuild of vector database
python scripts/toolkit.py build --force
```

### Converting Markdown to CSV

```bash
# Convert a single markdown file to CSV
python scripts/toolkit.py md2csv --input sample-markdown-file.md --output data/output.csv

# Convert multiple markdown files to a single CSV
python scripts/toolkit.py md2csv --input file1.md file2.md --output data/combined.csv

# Track source of each message when combining multiple files
python scripts/toolkit.py md2csv --input file1.md file2.md --output data/combined.csv --track-source
```

### Running Analysis

```bash
# Run analysis with all LLMs
python scripts/toolkit.py analyze --prompt prompts/analysis_prompts/technical_issues.txt

# Run with a single LLM (if you don't have all API keys)
python scripts/toolkit.py fallback --prompt prompts/analysis_prompts/technical_issues.txt --provider openai

# Run all prompts in a directory in batch mode
python scripts/toolkit.py analyze --batch --prompts-dir prompts/analysis_prompts

# Run the complete demo
python scripts/toolkit.py demo
```

#### Fallback Mode for Missing API Keys

If you don't have all three API keys, you can use fallback mode with a single provider:

```bash
# OpenAI fallback
python scripts/toolkit.py fallback --prompt prompts/analysis_prompts/technical_issues.txt --provider openai

# Anthropic fallback
python scripts/toolkit.py fallback --prompt prompts/analysis_prompts/technical_issues.txt --provider anthropic

# Gemini fallback
python scripts/toolkit.py fallback --prompt prompts/analysis_prompts/technical_issues.txt --provider gemini
```

The toolkit will use the model specified in your `.env` file for the selected provider:
- `OPENAI_MODEL` defaults to "gpt-4o"
- `ANTHROPIC_MODEL` defaults to "claude-3-opus-20240229"
- `GEMINI_MODEL` defaults to "gemini-1.5-pro"

### Creating Custom Prompts

You can create your own custom prompts by adding text files to the appropriate directories:

1. Create a new `.txt` file in one of the prompt directories:
   - `prompts/analysis_prompts/` for general analysis
   - `prompts/creative_discovery_prompts/` for exploratory analysis
   - `prompts/faq_prompts/` for FAQ generation
   - `prompts/prompt_for_specific_question/` for targeted inquiries

2. Structure your prompt with clear instructions for the LLMs

3. Use the `{conversations}` placeholder to reference retrieved content

4. Run your analysis:
   ```bash
   python scripts/toolkit.py analyze --prompt path/to/your/prompt.txt
   ```

## Architecture

The project has a modular architecture with the following key components:

1. **Vector Database Management**
   - `build_vector_db.py`: Builds vector DB from chat CSV data
   - `add_docs_to_vector_db.py`: Processes and adds docs to vector DB

2. **LLM Integration**
   - Multi-model support for OpenAI, Anthropic, and Google Gemini
   - Async/concurrent API calls
   - Fallback mode for single-LLM operation

3. **Analysis Pipeline**
   - `multi_llm_combined_analyzer.py`: Core analysis engine
   - Vector search for relevant content from both sources
   - Prompt templating
   - Comparison of LLM responses

4. **Unified Interface**
   - `toolkit.py`: All-in-one script for all operations
   - Command-line interface with subcommands

## Data Flow

1. Chat data (CSV) and documentation (Markdown) are processed and stored in vector databases
2. A prompt template is used to query the vector databases
3. Relevant chunks are retrieved from both sources
4. Multiple LLMs are queried with the prompt + retrieved chunks
5. Results are saved and compared in the outputs directory

## Development Tips

1. **API Keys**: OpenAI, Anthropic, and Google Gemini API keys are required for full functionality
2. **Chat Data Format**: CSV with columns: timestamp, username, message
3. **Documentation Format**: Markdown/MDX files with sections
4. **Output Files**: Results are saved to the outputs/ directory

## Testing

Run all tests in the project:
```bash
python tests/run_tests.py
```

Run a specific test file:
```bash
python tests/test_md_to_csv_converter.py
```

Run a specific test case:
```bash
python -m unittest tests.test_md_to_csv_converter.TestMarkdownToCsvConverter.test_single_file_conversion
```

## Troubleshooting

If you encounter issues:
1. Check the log files in the `logs/` directory for detailed error messages
2. Ensure all API keys are correctly set in the `.env` file
3. Verify that input data (chat data and documentation) is in the correct format