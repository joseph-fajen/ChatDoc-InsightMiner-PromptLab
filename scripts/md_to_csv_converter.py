#!/usr/bin/env python3
"""
Markdown to CSV Converter

This script converts a formatted markdown file with chat-like content into a CSV file.
The markdown file should have records separated by triple newlines, with each record
starting with a username and timestamp separated by an em dash (—).

Example format:
User1 — 12/30/24, 11:16 AM
Message content here

User2 — 12/30/24, 11:50 AM
Another message here
"""

import csv
import re
import os
import sys
import argparse
from datetime import datetime
from pathlib import Path

def parse_timestamp(timestamp_str):
    """Try different timestamp formats."""
    formats = [
        ('%m/%d/%y, %I:%M %p', '%Y-%m-%d %H:%M:%S'),  # "2/25/25, 11:35 AM"
        ('%m/%d/%y at %I:%M %p', '%Y-%m-%d %H:%M:%S'),  # "3/20/25 at 10:41 PM"
        ('%I:%M %p', '%H:%M:%S')  # "2:28 AM" (no date, use current)
    ]
    
    for input_format, output_format in formats:
        try:
            # For timestamps with no date, we'll use a placeholder date
            if input_format == '%I:%M %p':
                # Parse just the time
                time_only = datetime.strptime(timestamp_str, input_format)
                # Use current date (or you could set a specific date)
                placeholder_date = datetime.now().replace(
                    hour=time_only.hour, 
                    minute=time_only.minute, 
                    second=0
                )
                return placeholder_date.strftime('%Y-%m-%d %H:%M:%S')
            else:
                dt = datetime.strptime(timestamp_str, input_format)
                return dt.strftime(output_format)
        except ValueError:
            continue
    
    # If no format matched, return the original string and log a warning
    print(f"Warning: Could not parse timestamp: {timestamp_str}")
    return timestamp_str

def convert_markdown_to_csv(input_file, output_file, track_source=False):
    """Convert a formatted markdown file to CSV."""
    # Read the entire file content
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Split the content by triple newlines to get individual records
    records = content.split('\n\n\n')
    print(f"Found {len(records)} records in file")
    
    # Prepare data for CSV
    data = []
    source_name = os.path.basename(input_file).replace('.md', '')
    
    for idx, record in enumerate(records):
        record = record.strip()
        if not record:  # Skip empty records
            continue
        
        # Print a few records to debug if needed
        if idx < 3:
            print(f"Debug - Record {idx}:\n{record}")
        
        # Process the record
        lines = record.split('\n')
        if not lines:
            continue
            
        first_line = lines[0]
        
        # Check if the line contains the em dash
        if ' — ' in first_line:
            parts = first_line.split(' — ')
            if len(parts) >= 2:
                username = parts[0]
                timestamp_str = parts[1]
                
                # Convert timestamp to standard format
                timestamp = parse_timestamp(timestamp_str)
                
                # Extract message (everything after the first line)
                if len(lines) > 1:
                    message = ' '.join(lines[1:])
                else:
                    message = ""
                
                # Add to data
                if track_source:
                    data.append([timestamp, username, message, source_name])
                else:
                    data.append([timestamp, username, message])
                
                if idx < 3:
                    print(f"Successfully processed: {username} - {timestamp}")
            else:
                if idx < 3:
                    print(f"Line has em dash but couldn't split properly: {first_line}")
        else:
            if idx < 3:
                print(f"No em dash found in: {first_line}")
    
    # Write to CSV
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        if track_source:
            writer.writerow(['timestamp', 'username', 'message', 'source'])
        else:
            writer.writerow(['timestamp', 'username', 'message'])
        writer.writerows(data)
    
    print(f"Wrote {len(data)} messages to {output_file}")
    if len(data) > 0:
        print("Data sample:")
        for i, row in enumerate(data[:3]):
            if track_source:
                print(f"{i+1}. [{row[3]}] {row[1]} ({row[0]}): {row[2][:50]}...")
            else:
                print(f"{i+1}. {row[1]} ({row[0]}): {row[2][:50]}...")
    
    return len(data)

def convert_multiple_markdown_files(input_files, output_file, track_source=False):
    """Convert multiple markdown files to a single CSV."""
    all_data = []
    total_records = 0
    
    if track_source:
        headers = ['timestamp', 'username', 'message', 'source']
    else:
        headers = ['timestamp', 'username', 'message']
    
    # Process each input file
    for file_path in input_files:
        print(f"Reading file: {file_path}")
        source_name = os.path.basename(file_path).replace('.md', '')
        
        # Read the entire file content
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Split the content by triple newlines to get individual records
        records = content.split('\n\n\n')
        records = [r.strip() for r in records if r.strip()]
        print(f"  Found {len(records)} records")
        total_records += len(records)
        
        # Process records
        file_data = []
        for record in records:
            lines = record.split('\n')
            if not lines:
                continue
                
            first_line = lines[0]
            
            # Check if the line contains the em dash
            if ' — ' in first_line:
                parts = first_line.split(' — ')
                if len(parts) >= 2:
                    username = parts[0]
                    timestamp_str = parts[1]
                    
                    # Convert timestamp to standard format
                    timestamp = parse_timestamp(timestamp_str)
                    
                    # Extract message (everything after the first line)
                    if len(lines) > 1:
                        message = ' '.join(lines[1:])
                    else:
                        message = ""
                    
                    # Add to data
                    if track_source:
                        file_data.append([timestamp, username, message, source_name])
                    else:
                        file_data.append([timestamp, username, message])
        
        print(f"  Successfully processed {len(file_data)} records")
        all_data.extend(file_data)
    
    # Sort all data by timestamp
    try:
        all_data.sort(key=lambda x: x[0])
        print("  Records sorted chronologically")
    except:
        print("Warning: Could not sort by timestamp due to format inconsistencies")
    
    # Write to CSV
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(all_data)
    
    print(f"\nTotal found records across all files: {total_records}")
    print(f"Successfully processed and wrote {len(all_data)} records to {output_file}")
    if all_data:
        print("\nData sample:")
        for i, row in enumerate(all_data[:3]):
            if track_source:
                print(f"{i+1}. [{row[3]}] {row[1]} ({row[0]}): {row[2][:50]}...")
            else:
                print(f"{i+1}. {row[1]} ({row[0]}): {row[2][:50]}...")
    
    return len(all_data)

def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description="Convert formatted markdown files to CSV",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument('--input', type=str, nargs='+', required=True,
                       help="Path(s) to input markdown file(s)")
    parser.add_argument('--output', type=str, required=True,
                       help="Path to output CSV file")
    parser.add_argument('--track-source', action='store_true',
                       help="Add source column to CSV to track which file each record came from")
    
    args = parser.parse_args()
    
    if len(args.input) == 1:
        # Single file conversion
        input_file = args.input[0]
        if not os.path.exists(input_file):
            print(f"Error: Input file {input_file} not found.")
            return 1
        
        print(f"Converting single markdown file: {input_file}")
        count = convert_markdown_to_csv(input_file, args.output, args.track_source)
        print(f"Conversion complete. {count} records written to {args.output}")
    else:
        # Multiple file conversion
        for file_path in args.input:
            if not os.path.exists(file_path):
                print(f"Error: Input file {file_path} not found.")
                return 1
        
        print(f"Converting multiple markdown files: {', '.join(args.input)}")
        count = convert_multiple_markdown_files(args.input, args.output, args.track_source)
        print(f"Conversion complete. {count} records written to {args.output}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())