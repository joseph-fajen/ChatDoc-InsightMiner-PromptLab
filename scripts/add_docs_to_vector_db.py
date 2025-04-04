#!/usr/bin/env python3
"""
Add documentation to the vector database
"""

import os
import re
import logging
import uuid
import json
import argparse
from pathlib import Path
from datetime import datetime
import chromadb
from chromadb.utils import embedding_functions
from dotenv import load_dotenv

# Set up logging
# Ensure logs directory exists
if not os.path.exists('logs'):
    os.makedirs('logs')
    
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join('logs', f'add_docs_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')),
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
    """Load environment variables"""
    load_dotenv()
    return True

def process_mdx_frontmatter(content):
    """Remove frontmatter and import statements from MDX files"""
    # Remove frontmatter (between --- delimiters)
    content = re.sub(r'^---\n.*?---\n', '', content, flags=re.DOTALL | re.MULTILINE)
    
    # Remove import statements
    content = re.sub(r'^import.*?from.*?;?\n', '', content, flags=re.MULTILINE)
    
    return content

def extract_metadata_from_file(file_path):
    """Extract basic metadata from file path and name"""
    filename = file_path.name
    parent_dir = file_path.parent.name
    
    # Convert kebab-case to space-separated title case
    title = ' '.join(word.capitalize() for word in filename.replace('.md', '').replace('.mdx', '').split('-'))
    
    # Identify document type
    doc_type = 'documentation'
    if 'guide' in str(file_path) or 'tutorial' in str(file_path):
        doc_type = 'guide'
    elif 'api' in str(file_path) or 'reference' in str(file_path):
        doc_type = 'api_reference'
    elif 'faq' in str(file_path):
        doc_type = 'faq'
    
    return {
        'title': title,
        'section': parent_dir,
        'filename': filename,
        'path': str(file_path),
        'doc_type': doc_type,
        'source_type': 'documentation',  # Mark as documentation for combined queries
        'priority': 'high',  # Documentation is high priority
    }

def get_file_content(file_path):
    """Get the content of a file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
            # Process MDX content
            if str(file_path).endswith('.mdx'):
                content = process_mdx_frontmatter(content)
            
            return content
    except Exception as e:
        logger.error(f"Error reading file {file_path}: {e}")
        return None

def chunk_document_by_sections(content, metadata, min_chunk_size=150, max_chunk_size=1500):
    """
    Split document into chunks based on headers
    Returns list of (chunk_text, chunk_metadata) tuples
    """
    # Split by headers
    header_pattern = r'(#{1,6}\s+.*?)(?:\n|$)'
    sections = re.split(header_pattern, content)
    
    chunks = []
    current_section = "Introduction"
    current_text = ""
    current_headers = []
    
    for i, section in enumerate(sections):
        # Skip empty sections
        if not section.strip():
            continue
            
        if re.match(r'^#{1,6}\s+', section):  # This is a header
            # Save the previous section if it's not empty
            if current_text and len(current_text.strip()) > min_chunk_size:
                chunk_metadata = metadata.copy()
                chunk_metadata['section_headers'] = current_headers.copy()
                chunk_metadata['section'] = current_section
                chunks.append((current_text.strip(), chunk_metadata))
                current_text = ""
            
            # Update the current section header
            header_level = len(re.match(r'^(#+)', section).group(1))
            current_section = section.strip('# \n')
            
            # Update headers list (remove any at the current level or deeper)
            current_headers = [h for h in current_headers if h['level'] < header_level]
            current_headers.append({'level': header_level, 'text': current_section})
        else:
            # This is content, add it to the current section
            current_text += section
            
            # If the section is too large, split it further
            if len(current_text) > max_chunk_size:
                # Try to split at paragraph boundaries
                paragraphs = re.split(r'\n\s*\n', current_text)
                
                # Build chunks from paragraphs
                temp_chunk = ""
                for para in paragraphs[:-1]:  # Process all but the last paragraph
                    if len(temp_chunk) + len(para) <= max_chunk_size:
                        temp_chunk += para + "\n\n"
                    else:
                        if temp_chunk and len(temp_chunk.strip()) > min_chunk_size:
                            chunk_metadata = metadata.copy()
                            chunk_metadata['section_headers'] = current_headers.copy()
                            chunk_metadata['section'] = current_section
                            chunks.append((temp_chunk.strip(), chunk_metadata))
                        temp_chunk = para + "\n\n"
                
                # Keep the last paragraph and any new content for the next iteration
                current_text = temp_chunk + paragraphs[-1]
    
    # Don't forget the last section
    if current_text and len(current_text.strip()) > min_chunk_size:
        chunk_metadata = metadata.copy()
        chunk_metadata['section_headers'] = current_headers.copy()
        chunk_metadata['section'] = current_section
        chunks.append((current_text.strip(), chunk_metadata))
    
    return chunks

def process_documentation_directory(docs_dir, min_chunk_size=150, max_chunk_size=1500):
    """
    Process all documentation files in a directory and return chunks
    """
    logger.info(f"Processing documentation files in: {docs_dir}")
    
    all_chunks = []
    file_count = 0
    
    # Get all .md and .mdx files
    doc_files = list(Path(docs_dir).glob('**/*.md')) + list(Path(docs_dir).glob('**/*.mdx'))
    
    if not doc_files:
        logger.warning(f"No .md or .mdx files found in {docs_dir}")
        return all_chunks
    
    logger.info(f"Found {len(doc_files)} documentation files")
    
    # Process each file
    for file_path in doc_files:
        try:
            # Get file content
            content = get_file_content(file_path)
            if not content:
                continue
                
            # Extract metadata
            metadata = extract_metadata_from_file(file_path)
            
            # Chunk the document
            chunks = chunk_document_by_sections(
                content, 
                metadata,
                min_chunk_size=min_chunk_size,
                max_chunk_size=max_chunk_size
            )
            
            # Add to the result
            all_chunks.extend(chunks)
            file_count += 1
            
            logger.info(f"Processed {file_path.name}: generated {len(chunks)} chunks")
            
        except Exception as e:
            logger.error(f"Error processing {file_path}: {e}", exc_info=True)
    
    logger.info(f"Processed {file_count} files and generated {len(all_chunks)} total chunks")
    return all_chunks

def add_to_vector_database(chunks, db_path=None, collection_name=None, force_rebuild=False):
    """
    Add chunks to vector database
    """
    # Load environment
    load_environment()
    
    # Set default values from environment if not provided
    if db_path is None:
        db_path = os.getenv("VECTOR_DB_PATH", "./vector_db")
    
    if collection_name is None:
        collection_name = os.getenv("DOCS_COLLECTION_NAME", "documentation")
    
    try:
        # Set up the embedding function
        embedding_model = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
        logger.info(f"Initializing embedding model: {embedding_model}")
        
        embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name=embedding_model
        )
        
        # Connect to the vector database
        logger.info(f"Connecting to vector database at: {db_path}")
        client = chromadb.PersistentClient(path=db_path)
        
        # Check if collection exists and handle force_rebuild
        try:
            if force_rebuild and collection_name in [c.name for c in client.list_collections()]:
                logger.info(f"Force rebuild enabled - deleting existing collection: {collection_name}")
                client.delete_collection(collection_name)
                collection = client.create_collection(
                    name=collection_name,
                    embedding_function=embedding_function,
                    metadata={"description": "Documentation contents"}
                )
                logger.info(f"Created new collection: {collection_name}")
            else:
                # Get or create the collection
                collection = client.get_or_create_collection(
                    name=collection_name,
                    embedding_function=embedding_function,
                    metadata={"description": "Documentation contents"}
                )
                logger.info(f"Using collection: {collection_name}")
        except Exception as e:
            logger.error(f"Error with collection: {e}")
            collection = client.create_collection(
                name=collection_name,
                embedding_function=embedding_function,
                metadata={"description": "Documentation contents"}
            )
            logger.info(f"Created new collection: {collection_name}")
        
        # Prepare data for adding to the collection
        documents = []
        metadatas = []
        ids = []
        
        for i, (text, metadata) in enumerate(chunks):
            # Generate a unique ID
            doc_id = f"doc_{uuid.uuid4().hex}"
            
            # Fix metadata - convert non-string values so Chroma doesn't complain
            json_safe_metadata = {}
            for k, v in metadata.items():
                if isinstance(v, (str, int, float, bool)) or v is None:
                    json_safe_metadata[k] = v
                else:
                    # Convert complex objects to strings
                    json_safe_metadata[k] = json.dumps(v)
            
            documents.append(text)
            metadatas.append(json_safe_metadata)
            ids.append(doc_id)
        
        # Add in batches to avoid memory issues
        batch_size = 100
        for i in range(0, len(documents), batch_size):
            end = min(i + batch_size, len(documents))
            logger.info(f"Adding batch {i//batch_size + 1}/{(len(documents) + batch_size - 1)//batch_size}: items {i} to {end-1}")
            
            collection.add(
                documents=documents[i:end],
                metadatas=metadatas[i:end],
                ids=ids[i:end]
            )
        
        logger.info(f"Successfully added {len(documents)} chunks to collection {collection_name}")
        return True
        
    except Exception as e:
        logger.error(f"Error adding to vector database: {e}", exc_info=True)
        return False

def main():
    """Process documentation and add to vector database"""
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Add documentation to vector database")
    parser.add_argument('--docs-dir', type=str, default="docs", 
                        help="Directory containing documentation files (default: docs)")
    parser.add_argument('--collection', type=str, 
                        help="Name for the documentation collection")
    parser.add_argument('--min-chunk', type=int, default=150,
                        help="Minimum chunk size in characters (default: 150)")
    parser.add_argument('--max-chunk', type=int, default=1500,
                        help="Maximum chunk size in characters (default: 1500)")
    parser.add_argument('--force', action='store_true',
                        help="Force rebuild if collection already exists")
    args = parser.parse_args()
    
    # Create necessary directories
    ensure_directory("logs")
    
    # Process documentation directory
    docs_dir = args.docs_dir
    if not os.path.exists(docs_dir):
        logger.error(f"Documentation directory '{docs_dir}' not found.")
        return
    
    # Process documentation files
    chunks = process_documentation_directory(
        docs_dir, 
        min_chunk_size=args.min_chunk,
        max_chunk_size=args.max_chunk
    )
    
    if not chunks:
        logger.error("No chunks generated from documentation files")
        return
    
    # Add to vector database
    if add_to_vector_database(chunks, collection_name=args.collection, force_rebuild=args.force):
        logger.info("Successfully added documentation to vector database")
        print("\nDocumentation successfully added to vector database!")
        print("You can now use it in your queries.")
    else:
        logger.error("Failed to add documentation to vector database")
        print("\nFailed to add documentation to vector database")

if __name__ == "__main__":
    print("Adding Documentation to Vector Database")
    print("======================================")
    main()