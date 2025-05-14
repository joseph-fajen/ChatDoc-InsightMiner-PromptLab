# ChatDoc InsightMiner PromptLab Quick Start Guide

This guide will help you get started with the ChatDoc InsightMiner PromptLab, a versatile system for analyzing multiple data sources (chat messages and documentation) using vector databases and comparative LLM evaluation.

## Prerequisites

- Python 3.9 or later
- API keys for OpenAI, Anthropic, and Google Gemini (for multi-LLM features)
- Basic knowledge of command-line usage

## Installation

1. Clone or download this repository
2. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```
3. Copy the example environment file and update it with your API keys:
   ```bash
   cp .env.example .env
   # Edit .env with your favorite text editor to add API keys
   ```

## Quickest Start: Interactive Wizard

For the easiest setup experience, use the interactive wizard:

```bash
python scripts/toolkit.py wizard
```

The wizard will guide you through each step of the process, including:
- Verifying your environment
- Setting up API keys
- Building the vector database
- Adding documentation
- Running your first analysis

## Verify Installation

Run the setup script to check your environment:

```bash
python scripts/toolkit.py setup
```

This will verify that all required components are installed and correctly configured.

## Basic Workflow

### 1. Prepare Your Data

- **Chat Data**: Place your chat data in CSV format in the `data/` directory
  - Required columns: timestamp, username, message
  - Sample file provided: `data/chat_data.csv`
  - If your data is in markdown format, you can convert it to CSV:
    ```bash
    python scripts/toolkit.py md2csv --input yourfile.md --output data/converted_chat_data.csv
    ```

- **Documentation**: Add your documentation files in Markdown format to the `docs/` directory
  - Sample file provided: `docs/monitoring-dashboard.md`

### 1.1 Converting Markdown Files to CSV

If you have chat data in markdown format (with timestamp and username information), you can easily convert it:

```bash
# Convert a single markdown file
python scripts/toolkit.py md2csv --input sample-markdown-file.md --output data/output.csv

# Combine multiple markdown files
python scripts/toolkit.py md2csv --input file1.md file2.md --output data/combined.csv

# Track which file each message came from
python scripts/toolkit.py md2csv --input file1.md file2.md --output data/combined.csv --track-source
```

The markdown files should follow this format:
```
Username — MM/DD/YY, HH:MM AM/PM
Message content here


Another Username — MM/DD/YY, HH:MM AM/PM
Their message content here
```

### 2. Build Vector Databases

Build the vector database from your chat data:

```bash
python scripts/toolkit.py build
```

Add documentation to the vector database:

```bash
python scripts/toolkit.py docs
```

### 3. Run Analysis with a Prompt

Choose from the various prompt types based on your analysis needs:

#### Analysis Prompts
For general analytical insights:
```bash
python scripts/toolkit.py analyze --prompt prompts/analysis_prompts/technical_issues.txt
```

#### Creative Discovery Prompts
For deeper, more exploratory analysis:
```bash
python scripts/toolkit.py analyze --prompt prompts/creative_discovery_prompts/knowledge_graph_extraction.txt
```

#### FAQ Generation
To create comprehensive FAQs from conversations:
```bash
python scripts/toolkit.py analyze --prompt prompts/faq_prompts/faq_creator.txt
```

#### Specific Questions
For targeted, precise answers:
```bash
python scripts/toolkit.py analyze --prompt prompts/prompt_for_specific_question/identify_node.txt
```

### 4. Examine Results

Results will be saved in the `outputs/` directory, including:
- Individual text files with each LLM's response
- A JSON file with full results and metadata
- A Markdown comparison file for easy side-by-side viewing

## Using with Limited API Keys

If you don't have API keys for all three LLM providers, you can use the fallback mode with just one:

```bash
python scripts/toolkit.py fallback --prompt prompts/analysis_prompts/technical_issues.txt --provider openai
```

Replace `openai` with `anthropic` or `gemini` depending on which API key you have.

## Custom Prompts

You can create your own prompt templates in the following directories based on your needs:

- **Analysis Prompts**: `prompts/analysis_prompts/` for general analysis tasks
- **Creative Discovery**: `prompts/creative_discovery_prompts/` for exploratory analysis
- **FAQ Generation**: `prompts/faq_prompts/` for creating documentation
- **Specific Questions**: `prompts/prompt_for_specific_question/` for targeted inquiries

When creating prompts, use the `{conversations}` placeholder to reference the retrieved content from the vector database.

## Batch Processing

To run multiple prompts in sequence:

```bash
# Run all analysis prompts
python scripts/toolkit.py analyze --batch --prompts-dir prompts/analysis_prompts

# Run all creative discovery prompts
python scripts/toolkit.py analyze --batch --prompts-dir prompts/creative_discovery_prompts
```

## Run the Complete Demo

To see the full workflow in action, run the demo script:

```bash
python scripts/toolkit.py demo
```

## Troubleshooting

If you encounter issues:
1. Check the log files in the `logs/` directory
2. Ensure your API keys are correctly set in the `.env` file
3. Verify that the data format meets the required specifications
4. Make sure all Python dependencies are installed correctly

For more details, see the full README.md file.