#!/usr/bin/env python3
"""
Tests for the markdown to CSV conversion functionality.
"""

import os
import sys
import csv
import unittest
import tempfile
import shutil
from pathlib import Path

# Add the parent directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import the module to test
from scripts.md_to_csv_converter import convert_markdown_to_csv, convert_multiple_markdown_files, parse_timestamp

class TestMarkdownToCsvConverter(unittest.TestCase):
    """Test cases for markdown to CSV converter functions."""
    
    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
        
        # Create test markdown files
        self.test_md_file = os.path.join(self.test_dir, "test.md")
        with open(self.test_md_file, 'w', encoding='utf-8') as f:
            f.write("""User1 — 12/30/24, 11:16 AM
Hi all! New here. Just exploring your product.


User2 — 12/30/24, 11:50 AM
Can I do this via the free plan?


Support — 1/2/25, 10:32 AM
@team-member1 Could you answer this? ^""")
        
        self.test_md_file2 = os.path.join(self.test_dir, "test2.md")
        with open(self.test_md_file2, 'w', encoding='utf-8') as f:
            f.write("""User3 — 1/5/25, 1:46 AM
Hi, I have a question regarding your APIs.


User4 — 1/6/25, 2:30 PM
How do I get started with your SDK?""")
        
        # Output files
        self.output_csv = os.path.join(self.test_dir, "output.csv")
        self.output_combined_csv = os.path.join(self.test_dir, "combined.csv")
    
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.test_dir)
    
    def test_parse_timestamp(self):
        """Test timestamp parsing function."""
        # Test standard format
        self.assertTrue(parse_timestamp("12/30/24, 11:16 AM").startswith("2024-12-30"))
        
        # Test alternate format
        self.assertTrue(parse_timestamp("12/30/24 at 11:16 AM").startswith("2024-12-30"))
        
        # Test time-only format
        time_result = parse_timestamp("11:16 AM")
        self.assertIn("11:16:00", time_result)
    
    def test_single_file_conversion(self):
        """Test converting a single markdown file to CSV."""
        record_count = convert_markdown_to_csv(self.test_md_file, self.output_csv)
        
        # Check number of records
        self.assertEqual(record_count, 3)
        
        # Check CSV file exists
        self.assertTrue(os.path.exists(self.output_csv))
        
        # Check CSV file content
        with open(self.output_csv, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            headers = next(reader)
            rows = list(reader)
        
        # Check headers
        self.assertEqual(headers, ['timestamp', 'username', 'message'])
        
        # Check row count
        self.assertEqual(len(rows), 3)
        
        # Check content of rows
        usernames = [row[1] for row in rows]
        self.assertIn('User1', usernames)
        self.assertIn('User2', usernames)
        self.assertIn('Support', usernames)
    
    def test_multiple_file_conversion(self):
        """Test converting multiple markdown files to a single CSV."""
        record_count = convert_multiple_markdown_files(
            [self.test_md_file, self.test_md_file2], 
            self.output_combined_csv
        )
        
        # Check number of records
        self.assertEqual(record_count, 5)
        
        # Check CSV file exists
        self.assertTrue(os.path.exists(self.output_combined_csv))
        
        # Check CSV file content
        with open(self.output_combined_csv, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            headers = next(reader)
            rows = list(reader)
        
        # Check headers
        self.assertEqual(headers, ['timestamp', 'username', 'message'])
        
        # Check row count
        self.assertEqual(len(rows), 5)
        
        # Check content of rows
        usernames = [row[1] for row in rows]
        self.assertIn('User1', usernames)
        self.assertIn('User2', usernames)
        self.assertIn('Support', usernames)
        self.assertIn('User3', usernames)
        self.assertIn('User4', usernames)
    
    def test_multiple_file_conversion_with_source(self):
        """Test converting multiple markdown files with source tracking."""
        record_count = convert_multiple_markdown_files(
            [self.test_md_file, self.test_md_file2], 
            self.output_combined_csv,
            track_source=True
        )
        
        # Check number of records
        self.assertEqual(record_count, 5)
        
        # Check CSV file content
        with open(self.output_combined_csv, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            headers = next(reader)
            rows = list(reader)
        
        # Check headers include source
        self.assertEqual(headers, ['timestamp', 'username', 'message', 'source'])
        
        # Check sources
        sources = [row[3] for row in rows]
        self.assertIn('test', sources)
        self.assertIn('test2', sources)

if __name__ == '__main__':
    unittest.main()