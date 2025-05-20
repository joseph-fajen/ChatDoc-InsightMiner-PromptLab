# Testing Guide for ChatDoc-InsightMiner-PromptLab

This guide covers both automated and manual testing procedures to verify that ChatDoc-InsightMiner-PromptLab works correctly. Follow these steps systematically to ensure all functionality is operational before sharing with colleagues.

## Automated Testing

The project includes automated tests to verify core functionality. These tests can be run as follows:

```bash
# Run all tests
python tests/run_tests.py

# Run a specific test file
python tests/test_md_to_csv_converter.py

# Run a specific test case
python -m unittest tests.test_md_to_csv_converter.TestMarkdownToCsvConverter.test_single_file_conversion
```

### Current Test Coverage

1. **Markdown to CSV Conversion**
   - Tests basic conversion functionality 
   - Tests source tracking feature
   - Tests error handling

2. **Toolkit CLI Commands**
   - Tests the command-line interface for md2csv conversion

### Creating New Tests

When adding new features, create corresponding test cases in the `tests/` directory:

1. Create a new test file named `test_<module_name>.py`
2. Implement test cases using Python's `unittest` framework
3. Run your tests to verify functionality

## Manual Testing Guide

## Prerequisites

Ensure you have:
- Python 3.9+ installed
- Git access to the repository
- API keys for at least one LLM provider (OpenAI, Anthropic, or Google Gemini)

## Step 1: Create a Clean Test Environment

```bash
# Navigate to the project directory
cd /Users/josephfajen/git/ChatDoc-InsightMiner-PromptLab

# Create a new virtual environment
python -m venv test_env

# Activate the environment
# On macOS/Linux:
source test_env/bin/activate
# On Windows:
# test_env\Scripts\activate

# Install updated dependencies
pip install -r requirements.txt
```

## Step 2: Run the Dependency Test Script

This comprehensive validation script checks all aspects of the toolkit setup:

```bash
# Make the script executable (if needed)
chmod +x scripts/dependency_test.py

# Run the dependency test
python scripts/dependency_test.py
```

The script will test:
- Python version and required package dependencies
- Project directory structure and required files
- Sample data availability
- Basic functionality (markdown conversion)
- Test suite execution
- API key configuration

Review the output to ensure all checks pass. The script provides detailed error messages and next steps if any issues are found.

## Step 3: Basic Environment Verification

```bash
# Verify that the setup script works
python scripts/toolkit.py setup
```

You should see successful verification of your environment.

## Step 4: Test Markdown to CSV Conversion

```bash
# Convert the sample markdown file to CSV
python scripts/toolkit.py md2csv --input sample-markdown-file.md --output data/test_output.csv

# Verify the CSV was created
ls -l data/test_output.csv

# Optional: Examine the CSV content
head data/test_output.csv
```

This tests a core utility function without requiring API access.

## Step 5: Test Vector Database Construction

```bash
# Build the vector database from chat data
python scripts/toolkit.py build

# Verify the vector database was created
ls -l vector_db/
```

This verifies that the ChromaDB integration and sentence-transformers are working correctly.

## Step 6: Test Documentation Integration

```bash
# Add documentation to the vector database
python scripts/toolkit.py docs

# Verify the documentation was added
# (This command should report success and show the correct collection)
```

This tests the documentation processing functionality.

## Step 7: Test LLM Integration (Based on Available API Keys)

Choose the appropriate test based on which API keys you have available:

### Option A: Test with OpenAI

```bash
# Ensure your OpenAI API key is in .env
python scripts/toolkit.py fallback --prompt prompts/analysis_prompts/technical_issues.txt --provider openai
```

### Option B: Test with Anthropic

```bash
# Ensure your Anthropic API key is in .env
python scripts/toolkit.py fallback --prompt prompts/analysis_prompts/technical_issues.txt --provider anthropic
```

### Option C: Test with Google Gemini

```bash
# Ensure your Google Gemini API key is in .env
python scripts/toolkit.py fallback --prompt prompts/analysis_prompts/technical_issues.txt --provider gemini
```

Verify that analysis results are generated in the outputs directory.

## Step 8: Test the Interactive Wizard (Optional)

```bash
# Run the interactive wizard
python scripts/toolkit.py wizard
```

Follow the prompts to test the wizard functionality.

## Step 9: Test Batch Processing (Optional)

```bash
# Run batch analysis on a directory of prompts
python scripts/toolkit.py analyze --batch --prompts-dir prompts/analysis_prompts
```

This is a more comprehensive test of functionality.

## Step 10: Cleanup

```bash
# Deactivate the virtual environment
deactivate

# Optional: Remove the test environment if desired
# rm -rf test_env
```

## Troubleshooting Common Issues

### Issue: Package Import Errors
- **Solution**: Verify the package is installed with `pip list | grep package_name`
- **Solution**: Try reinstalling with `pip install -U package_name`

### Issue: API Key Authentication Failures
- **Solution**: Verify API keys are correctly set in .env file
- **Solution**: Check API key format and remove any trailing spaces

### Issue: Sentence-Transformers Model Download Failures
- **Solution**: Ensure internet connectivity is stable
- **Solution**: Check for sufficient disk space

### Issue: ChromaDB Errors
- **Solution**: Make sure the vector_db directory is writeable
- **Solution**: Try deleting the vector_db directory and rebuild

### Issue: Memory Errors
- **Solution**: Free up system memory or reduce batch sizes in vector operations

## What Success Looks Like

After completing all tests:
1. All dependencies import without errors
2. Vector database builds successfully with chat data
3. Documentation is added to the vector database
4. LLM queries return meaningful analysis results
5. Output files are created in the outputs directory

If you encounter any issues, check the logs in the `logs/` directory for detailed error messages.

## End-to-End Verification

To verify the entire pipeline works correctly, run the following end-to-end test:

```bash
# Create a clean environment first
python -m venv test_env
source test_env/bin/activate
pip install -r requirements.txt

# Run the toolkit with sample data
cp .env.example .env  # Make sure to add at least one API key
python scripts/toolkit.py build  # Build vector DB from sample data
python scripts/toolkit.py docs   # Add sample docs
python scripts/toolkit.py fallback --prompt prompts/analysis_prompts/technical_issues.txt --provider openai  # Replace with your available provider

# Check outputs
ls -l outputs/
```

This end-to-end test verifies that all components work together with the sample data.

## Next Steps

If all tests pass, the toolkit is ready to be shared with colleagues. Consider:
1. Creating example outputs to showcase functionality
2. Preparing a quick demonstration for colleagues
3. Documenting any specific API key requirements 
4. Adding more automated tests for critical components