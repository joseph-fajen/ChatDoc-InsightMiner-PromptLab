# ChatDoc InsightMiner PromptLab

A versatile Python toolkit for analyzing multiple data sources (chat messages and documentation) using vector databases and comparative LLM evaluation.

## Overview

This toolkit allows you to:

1. Build vector databases from chat message data (CSV format)
2. Add documentation (Markdown/MDX) to the vector database
3. Query the vector database with specialized prompts
4. Compare results from multiple LLMs (OpenAI, Anthropic, and Google Gemini)
5. Generate comprehensive analyses and insights

## Key Features

- **Multiple Data Sources**: Combine chat messages and documentation in a unified vector database
- **Comparative LLM Analysis**: Query three leading LLMs simultaneously for diverse perspectives
- **Specialized Prompts**: Use domain-specific prompts for targeted insights
- **Visualization**: Generate side-by-side comparisons of LLM outputs
- **Batch Processing**: Run multiple analyses in sequence for comprehensive results
- **Simplified Interface**: Use the all-in-one script for streamlined workflow

## Directory Structure

```
MultiSource-TriLLM-Toolkit/
├── README.md
├── QUICKSTART.md
├── requirements.txt
├── .env.example                # Template for API keys and settings
├── scripts/
│   ├── toolkit.py              # All-in-one script for all functionality
│   ├── setup.py                # Environment setup and verification
│   ├── build_vector_db.py      # Build vector DB from chat data
│   ├── add_docs_to_vector_db.py  # Add documentation to vector DB
│   ├── multi_llm_combined_analyzer.py  # Query sources with multiple LLMs
│   └── run_demo.py             # Run a complete demo workflow
├── data/
│   └── chat_data.csv           # Sample chat data
├── docs/                       # Documentation directory
│   └── monitoring-dashboard.md # Sample documentation
├── prompts/                    # Prompt templates directory
│   ├── analysis_prompts/       # Analysis-focused prompts
│   └── question_prompts/       # Question-focused prompts
├── outputs/                    # Analysis outputs directory
└── logs/                       # Log files directory
```

## Getting Started

### Prerequisites

- Python 3.9+
- API keys for OpenAI, Anthropic, and Google Gemini (for multi-LLM features)
- Basic knowledge of command-line usage

### Installation

1. Clone this repository
2. Install requirements:
   ```
   pip install -r requirements.txt
   ```
3. Create a `.env` file from the template:
   ```
   cp .env.example .env
   ```
4. Add your API keys and customize settings in the `.env` file

### Quick Setup with the Interactive Wizard

The easiest way to get started is to use the interactive wizard:

```
python scripts/toolkit.py wizard
```

The wizard will guide you through:
- Verifying your environment
- Setting up API keys
- Building the vector database
- Adding documentation
- Running your first analysis

### Basic Usage

#### All-in-One Script (Recommended)

Use the all-in-one script for a simplified workflow:

```bash
# Set up the environment
python scripts/toolkit.py setup

# Build the vector database
python scripts/toolkit.py build

# Add documentation to the vector database
python scripts/toolkit.py docs

# Run analysis with all LLMs
python scripts/toolkit.py analyze --prompt prompts/analysis_prompts/technical_issues.txt

# Run with a single LLM (if you don't have all API keys)
python scripts/toolkit.py fallback --prompt prompts/analysis_prompts/technical_issues.txt --provider openai

# Run the complete demo
python scripts/toolkit.py demo
```

#### Individual Scripts (Legacy)

You can also use the individual scripts:

1. Prepare your chat data in CSV format with columns: timestamp, username, message
2. Add documentation files in Markdown format to the docs directory
3. Build the vector database:
   ```
   python scripts/build_vector_db.py
   ```
4. Add documentation to the vector database:
   ```
   python scripts/add_docs_to_vector_db.py
   ```
5. Run a multi-LLM analysis with a prompt:
   ```
   python scripts/multi_llm_combined_analyzer.py --prompt prompts/analysis_prompts/technical_issues.txt
   ```

## Using the Toolkit with Limited API Keys

The toolkit works best with all three LLM providers (OpenAI, Anthropic, and Google Gemini). However, you can still use it with just one provider by using the fallback mode:

```bash
python scripts/toolkit.py fallback --prompt prompts/your_prompt.txt --provider [openai|anthropic|gemini]
```

Choose the provider for which you have an API key.

## Troubleshooting

If you encounter issues:

1. Run the setup script to verify your environment:
   ```
   python scripts/setup.py
   ```

2. Check the log files in the `logs/` directory for detailed error messages

3. Ensure your API keys are correctly set in the `.env` file

4. Verify that your input data (chat data and documentation) is in the correct format

## License

This project is licensed under the MIT License - see the LICENSE file for details.