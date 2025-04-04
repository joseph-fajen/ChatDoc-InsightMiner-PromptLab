#!/usr/bin/env python3
"""
Build a vector database from chat message CSV data
"""

import os
import uuid
import logging
import argparse
import pandas as pd
import chromadb
from chromadb.utils import embedding_functions
from tqdm import tqdm
from dotenv import load_dotenv

# Set up logging
# Ensure logs directory exists
if not os.path.exists('logs'):
    os.makedirs('logs')
    
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join('logs', f'build_db_{pd.Timestamp.now().strftime("%Y%m%d_%H%M%S")}.log')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def ensure_directory(directory):
    """Ensure a directory exists"""
    if not os.path.exists(directory):
        os.makedirs(directory)
        logger.info(f"Created directory: {directory}")

def load_csv_data(file_path):
    """Load and validate CSV data"""
    try:
        df = pd.read_csv(file_path)
        required_columns = ["timestamp", "username", "message"]
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            logger.error(f"CSV is missing required columns: {missing_columns}")
            return None
            
        logger.info(f"Successfully loaded {len(df)} rows from {file_path}")
        return df
    except Exception as e:
        logger.error(f"Error loading CSV file: {e}")
        return None

def build_vector_database(csv_file=None, collection_name=None, force_rebuild=False):
    """Build a vector database from chat CSV data"""
    # Load environment variables
    load_dotenv()
    db_path = os.getenv("VECTOR_DB_PATH", "./vector_db")
    embedding_model = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
    default_collection = os.getenv("CHAT_COLLECTION_NAME", "chat_messages")
    
    # Use default collection name if not specified
    if collection_name is None:
        collection_name = default_collection
    
    # Use default CSV path if not specified
    if csv_file is None:
        csv_file = os.path.join("data", "chat_data.csv")
    
    # Create necessary directories
    ensure_directory("logs")
    ensure_directory(db_path)
    
    # Check if CSV file exists
    if not os.path.exists(csv_file):
        logger.error(f"Data file {csv_file} not found")
        logger.info("Please ensure your CSV file is in the correct location")
        return False
    
    df = load_csv_data(csv_file)
    if df is None:
        return False
    
    try:
        # Set up the embedding function (using Sentence Transformers locally)
        logger.info(f"Initializing embedding model: {embedding_model}")
        embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name=embedding_model
        )
        
        # Initialize the persistent vector database
        logger.info(f"Initializing vector database at: {db_path}")
        client = chromadb.PersistentClient(path=db_path)
        
        # Create or get collection
        collection = client.get_or_create_collection(
            name=collection_name,
            embedding_function=embedding_function,
            metadata={"description": "Chat conversations"}
        )
        
        # Check if the collection already has documents
        existing_count = collection.count()
        if existing_count > 0:
            logger.warning(f"Collection already contains {existing_count} documents")
            
            # Auto-rebuild if force_rebuild is True
            if force_rebuild:
                rebuild = True
                logger.info("Force rebuild enabled - will delete existing collection")
            else:
                # Ask user for input
                user_input = input("Do you want to delete existing data and rebuild? (y/n): ")
                rebuild = user_input.lower() == 'y'
                
            if rebuild:
                logger.info(f"Deleting existing collection: {collection_name}")
                client.delete_collection(collection_name)
                collection = client.create_collection(
                    name=collection_name,
                    embedding_function=embedding_function,
                    metadata={"description": "Chat conversations"}
                )
            else:
                logger.info("Keeping existing data, adding new records...")
        
        # Prepare data for ingestion
        logger.info("Preparing data for vectorization...")
        ids = []
        documents = []
        metadatas = []
        
        for _, row in tqdm(df.iterrows(), total=len(df), desc="Processing messages"):
            # Create a unique ID
            doc_id = str(uuid.uuid4())
            ids.append(doc_id)
            
            # Format the message
            document = f"[{row['timestamp']}] {row['username']}: {row['message']}"
            documents.append(document)
            
            # Add metadata
            metadata = {
                "timestamp": str(row.get("timestamp", "")),
                "username": str(row.get("username", "")),
                "topic": str(row.get("topic", "")),
                "source_type": "chat"  # Mark as chat for combined queries
            }
            metadatas.append(metadata)
        
        # Add data to the collection (in batches if needed)
        batch_size = 100  # Adjust based on your memory constraints
        total_batches = (len(documents) + batch_size - 1) // batch_size
        
        logger.info(f"Adding {len(documents)} documents to vector database in {total_batches} batches...")
        for i in tqdm(range(0, len(documents), batch_size), desc="Adding to vector database"):
            end_idx = min(i + batch_size, len(documents))
            batch_ids = ids[i:end_idx]
            batch_documents = documents[i:end_idx]
            batch_metadatas = metadatas[i:end_idx]
            
            collection.add(
                ids=batch_ids,
                documents=batch_documents,
                metadatas=batch_metadatas
            )
        
        # Verify the database was created successfully
        final_count = collection.count()
        logger.info(f"Vector database built successfully with {final_count} documents")
        return True
        
    except Exception as e:
        logger.error(f"Error building vector database: {e}", exc_info=True)
        return False

def main():
    """Parse command-line arguments and build the vector database"""
    parser = argparse.ArgumentParser(description="Build a vector database from chat message CSV data")
    parser.add_argument('--csv', type=str, help="Path to CSV file containing chat messages")
    parser.add_argument('--collection', type=str, help="Name for the vector database collection")
    parser.add_argument('--force', action='store_true', help="Force rebuild if collection already exists")
    args = parser.parse_args()
    
    if build_vector_database(args.csv, args.collection, args.force):
        print("\nVector database built successfully!")
        print("You can now add documentation with add_docs_to_vector_db.py")
        print("or run analysis with toolkit.py or multi_llm_combined_analyzer.py")
    else:
        print("\nFailed to build vector database. Check the logs for details.")

if __name__ == "__main__":
    main()