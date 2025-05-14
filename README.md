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
- **Markdown to CSV Conversion**: Convert chat data from markdown format to CSV for processing
- **Comparative LLM Analysis**: Query three leading LLMs simultaneously for diverse perspectives
- **Specialized Prompts**: Use domain-specific prompts for targeted insights
- **Visualization**: Generate side-by-side comparisons of LLM outputs
- **Batch Processing**: Run multiple analyses in sequence for comprehensive results
- **Simplified Interface**: Use the all-in-one script for streamlined workflow

## Directory Structure

```
ChatDoc-InsightMiner-PromptLab/
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
│   ├── md_to_csv_converter.py  # Convert markdown files to CSV format
│   └── run_demo.py             # Run a complete demo workflow
├── data/
│   └── chat_data.csv           # Sample chat data
├── docs/                       # Documentation directory
│   └── monitoring-dashboard.md # Sample documentation
├── prompts/                    # Prompt templates directory
│   ├── analysis_prompts/       # Analysis-focused prompts
│   │   ├── documentation_gaps.txt
│   │   ├── feature_demand_analysis.txt
│   │   ├── sentiment_analysis.txt
│   │   ├── technical_issues.txt
│   │   └── user_journey_analysis.txt
│   ├── creative_discovery_prompts/  # Creative analysis prompts
│   │   ├── community_dynamics.txt
│   │   ├── competitive_intelligence.txt
│   │   ├── future_prediction.txt
│   │   ├── knowledge_graph_extraction.txt
│   │   ├── linguistic_patterns.txt
│   │   ├── technical_issues_map.txt
│   │   └── user_persona_development.txt
│   ├── faq_prompts/            # FAQ generation prompts
│   │   ├── blockfrost_icebreakers_faq_enhancement_prompt.txt
│   │   └── faq_creator.txt
│   └── prompt_for_specific_question/  # Targeted question prompts
│       └── identify_node.txt
├── tests/                      # Test suite
│   ├── run_tests.py            # Test runner
│   ├── test_md_to_csv_converter.py  # Unit tests for conversion
│   └── test_toolkit_md2csv.py  # Integration tests for CLI
├── outputs/                    # Analysis outputs directory
├── vector_db/                  # Vector database storage
└── logs/                       # Log files directory
```

## Starter Sample Prompts

The toolkit comes with a variety of pre-built prompts for different analytical purposes:

### Analysis Prompts
General-purpose analytical prompts for extracting insights:
- **Technical Issues Analysis**: Identify common technical problems and solutions
- **User Journey Analysis**: Map the typical user experience and pain points
- **Documentation Gaps**: Find missing or incomplete documentation areas
- **Feature Demand Analysis**: Discover the most requested features
- **Sentiment Analysis**: Gauge user sentiment around specific topics

### Creative Discovery Prompts
Advanced prompts for deeper insights and creative exploration:
- **Knowledge Graph Extraction**: Build a comprehensive domain knowledge map
- **User Persona Development**: Create detailed user personas from conversations
- **Community Dynamics**: Analyze community interactions and relationships
- **Future Prediction**: Forecast upcoming trends and potential issues
- **Competitive Intelligence**: Extract information about competitors

### FAQ Generation
Tools for creating helpful documentation:
- **FAQ Creator**: Generate comprehensive FAQ documents from conversations
- **FAQ Enhancement**: Improve existing FAQs with new content

### Specific Question Prompts
Targeted prompts for answering specific user questions:
- **Identify Node**: Step-by-step guide for identifying nodes in monitoring dashboards

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

# Convert markdown file(s) to CSV
python scripts/toolkit.py md2csv --input sample-markdown-file.md --output data/output.csv

# Convert multiple markdown files with source tracking
python scripts/toolkit.py md2csv --input file1.md file2.md --output data/combined.csv --track-source

# Run batch analysis on all prompts in a directory
python scripts/toolkit.py analyze --batch --prompts-dir prompts/analysis_prompts

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

## Creating Custom Prompts

You can create your own custom prompts by adding text files to the appropriate directories:

1. Create a new `.txt` file in one of the prompt directories
2. Structure your prompt with clear instructions for the LLMs
3. Use the `{conversations}` placeholder to reference retrieved content
4. Run your analysis:
   ```
   python scripts/toolkit.py analyze --prompt path/to/your/prompt.txt
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

## Testing

The toolkit includes a test suite to validate its functionality:

```bash
# Run all tests
python tests/run_tests.py

# Run a specific test file
python tests/test_md_to_csv_converter.py

# Run a specific test case
python -m unittest tests.test_md_to_csv_converter.TestMarkdownToCsvConverter.test_single_file_conversion
```

The test suite includes:
- Unit tests for the markdown to CSV conversion logic
- Integration tests for the toolkit command line interface

## License

This project is licensed under the MIT License - see the LICENSE file for details.