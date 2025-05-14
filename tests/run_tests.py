#!/usr/bin/env python3
"""
Test runner for ChatDoc InsightMiner PromptLab.
"""

import unittest
import os
import sys

def main():
    """Discover and run all tests."""
    # Get the directory containing this script
    test_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Add the parent directory to sys.path
    sys.path.insert(0, os.path.abspath(os.path.join(test_dir, '..')))
    
    # Discover and run tests
    loader = unittest.TestLoader()
    suite = loader.discover(test_dir, pattern="test_*.py")
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Return non-zero exit code if any tests failed
    return 0 if result.wasSuccessful() else 1

if __name__ == "__main__":
    sys.exit(main())