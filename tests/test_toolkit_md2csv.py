#!/usr/bin/env python3
"""
Integration tests for the markdown to CSV conversion toolkit command.
"""

import os
import sys
import csv
import unittest
import tempfile
import shutil
import subprocess
from pathlib import Path

class TestToolkitMd2CsvCommand(unittest.TestCase):
    """Integration test cases for the md2csv command in toolkit.py."""
    
    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
        self.project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        
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
    
    def test_md2csv_single_file(self):
        """Test the md2csv command with a single file."""
        # Run the command
        cmd = [
            sys.executable, 
            os.path.join(self.project_root, "scripts/toolkit.py"),
            "md2csv",
            "--input", self.test_md_file,
            "--output", self.output_csv
        ]
        
        try:
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            
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
        
        except subprocess.CalledProcessError as e:
            self.fail(f"Command failed with return code {e.returncode}: {e.stderr}")
    
    def test_md2csv_multiple_files(self):
        """Test the md2csv command with multiple files."""
        # Run the command
        cmd = [
            sys.executable, 
            os.path.join(self.project_root, "scripts/toolkit.py"),
            "md2csv",
            "--input", self.test_md_file, self.test_md_file2,
            "--output", self.output_combined_csv,
            "--track-source"
        ]
        
        try:
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            
            # Check CSV file exists
            self.assertTrue(os.path.exists(self.output_combined_csv))
            
            # Check CSV file content
            with open(self.output_combined_csv, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                headers = next(reader)
                rows = list(reader)
            
            # Check headers include source
            self.assertEqual(headers, ['timestamp', 'username', 'message', 'source'])
            
            # Check row count
            self.assertEqual(len(rows), 5)
            
            # Check content of rows
            usernames = [row[1] for row in rows]
            self.assertIn('User1', usernames)
            self.assertIn('User2', usernames)
            self.assertIn('Support', usernames)
            self.assertIn('User3', usernames)
            self.assertIn('User4', usernames)
            
            # Check sources
            sources = [row[3] for row in rows]
            self.assertTrue(any('test' in s for s in sources))
            self.assertTrue(any('test2' in s for s in sources))
        
        except subprocess.CalledProcessError as e:
            self.fail(f"Command failed with return code {e.returncode}: {e.stderr}")

if __name__ == '__main__':
    unittest.main()