from typing import Dict, List, Any
from pymongo import MongoClient
from rich.progress import track
import concurrent.futures
import sys
import os

# Add two levels up from the current script's directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))  # Get script directory
parent_dir = os.path.dirname(current_dir)  # Go up two levels

if parent_dir not in sys.path:
    sys.path.append(parent_dir)
    
from utils.colored_prints import ColoredPrint
from utils.logging_module import get_logger


class MongoAbstractor:
    
    def __init__(self, db_name:str, host:str='localhost', port:int=27017):

        self.client = MongoClient(host=host, port=port)
        self.db = self.client[db_name]
        self.colored_print = ColoredPrint()
        self.logger = get_logger(__name__, log_file='logs/data_acquisition.log')

    def get_collection_names(self):
        """
        Get all collection names in the database.
        
        Returns:
            list: List of collection names
        """
        return self.db.list_collection_names()

    def get_collections_content_count(self):
        """
        Get the document count for each collection.
        
        Returns:
            dict: Dictionary with collection names as keys and their document counts as values
        """
        collections = self.get_collection_names()
        content_counts = {}
        
        for collection in collections:
            count = self.db[collection].count_documents({})
            content_counts[collection] = count
            
        return content_counts
    
    def get_collections_unique_counts(self, field:str="id"):
        """
        For each collection, get a tuple of (document count, unique value count for the given field).

        Args:
            field (str): Field name to count unique values for

        Returns:
            dict: {collection_name: (entry_count, unique_count)}
        """
        result = {}
        content_counts = self.get_collections_content_count()
        for collection, entry_count in content_counts.items():
            try:
                unique_values = self.db[collection].distinct(field)
                unique_count = len(unique_values)
            except Exception as e:
                self.colored_print.error(f"Error getting unique count for {field} in {collection}: {str(e)}")
                self.logger.error(f"Error getting unique count for {field} in {collection}: {str(e)}")
                unique_count = None
            result[collection] = (entry_count, unique_count)
        return result

    def get_unique_count(self, collection_name:str, field:str):
        """
        Get the number of unique values for a given field in a collection.

        Args:
            collection_name (str): Name of the collection to query
            field (str): Field name to count unique values for

        Returns:
            int: Number of unique values for the specified field
        """
        try:
            unique_values = self.db[collection_name].distinct(field)
            return len(unique_values)
        except Exception as e:
            self.colored_print.error(f"Error getting unique count for {field} in {collection_name}: {str(e)}")
            self.logger.error(f"Error getting unique count for {field} in {collection_name}: {str(e)}")
            return 0
        
    def get_all_documents(self, collection_name:str):
        """
        Get all documents from a specified collection.
        
        Args:
            collection_name (str): Name of the collection to query
            
        Returns:
            list: List of all documents in the collection
        """
        try:
            documents = list(self.db[collection_name].find({}))
            return documents
        except Exception as e:
            self.colored_print.error(f"Error retrieving documents from {collection_name}: {str(e)}")
            self.logger.error(f"Error retrieving documents from {collection_name}: {str(e)}")
            return []

    def insert_one(self, collection_name:str, data:Dict):
        """
        Insert a single document into a collection.
        Note: This is kept for internal use. Use safe_insert_one() for new insertions.
        """
        return self.db[collection_name].insert_one(data)

    def find_one(self, collection_name:str, query:Dict):
        """
        Find a document in a collection that match the given query.
        Args:
            collection_name (str): Name of the collection to query
            query (dict): MongoDB query dictionary to filter documents
        Returns:
            dict: The first matching document, or None if no match is found
        """
        return self.db[collection_name].find_one(query)

    def find_all(self, collection_name:str, query:Dict, projection=None):
        """
        Find all documents in a collection that match the given query.
        
        Args:
            collection_name (str): Name of the collection to query
            query (dict): MongoDB query dictionary to filter documents
            projection (dict, optional): Fields to include or exclude in the results
            
        Returns:
            list: List of matching documents, empty list if error occurs
        """
        try:
            return list(self.db[collection_name].find(query, projection))
        except Exception as e:
            self.colored_print.error(f"Error querying {collection_name}: {str(e)}")
            self.logger.error(f"Error querying {collection_name}: {str(e)}")
            return []

    def update_one(self, collection_name:str, query:Dict, update_data:Dict):
        return self.db[collection_name].update_one(query, {'$set': update_data})

    def delete_one(self, collection_name:str, query:Dict):
        return self.db[collection_name].delete_one(query)

    def delete_many(self, collection_name:str, query:Dict):
        return self.db[collection_name].delete_many(query)

    def exists(self, collection_name:str, query:Dict):
        """
        Check if a document exists in the collection.
        
        Args:
            collection_name (str): Name of the collection to query
            query (dict): MongoDB query dictionary to check existence
            
        Returns:
            bool: True if document exists, False otherwise
        """
        try:
            return self.db[collection_name].count_documents(query, limit=1) > 0
        except Exception as e:
            self.colored_print.error(f"Error checking existence in {collection_name}: {str(e)}")
            self.logger.error(f"Error checking existence in {collection_name}: {str(e)}")
            return False

    def safe_insert_one(self, collection_name:str, data:Dict):
        """
        Safely insert a document only if an identical document doesn't already exist.
        
        Args:
            collection_name (str): Name of the collection
            data (dict): Document to insert
            
        Returns:
            pymongo.results.InsertOneResult: Result of insertion if successful
            None: If document already exists or error occurs
        """
        try:
            # Check if exact same document exists
            if self.db[collection_name].find_one(data):
                return None
                
            # Insert document if it doesn't exist
            result = self.insert_one(collection_name, data)
            return result
        
        except Exception as e:
            self.colored_print.error(f"Error in safe insert to {collection_name}: {str(e)}")
            self.logger.error(f"Error in safe insert to {collection_name}: {str(e)}")
            return None

    def safe_insert_llm_output(self, collection_name: str, data: Dict, field: str):
        """
        Safely insert a document only if a document with the same field value doesn't already exist.
        
        Args:
            collection_name (str): Name of the collection
            data (dict): Document to insert
            field (str): Field to check for duplicates (e.g., "review_id")
            
        Returns:
            pymongo.results.InsertOneResult: Result of insertion if successful
            None: If a document with the same field value already exists or error occurs
        """
        try:
            # Check if a document with the same field value exists
            if field in data and self.db[collection_name].find_one({field: data[field]}):
                return None  # Document with the same field value already exists
                
            # Insert document if no match is found
            result = self.insert_one(collection_name, data)
            return result
        
        except Exception as e:
            self.colored_print.error(f"Error in safe insert to {collection_name}: {str(e)}")
            self.logger.error(f"Error in safe insert to {collection_name}: {str(e)}")
            return None
    
    def get_all_submission_data(self, forum_id: str):
        """
        Retrieve all documents related to a submission by forum_id using MongoDB aggregation.

        Args:
            forum_id (str): The forum ID of the submission.

        Returns:
            Optional[Dict[str, Any]]: Dictionary containing all related documents grouped by collection.
        """
        try:
            pipeline = [
                {"$match": {"forum": forum_id}},
                {"$lookup": {
                    "from": "decisions",
                    "localField": "forum",
                    "foreignField": "forum",
                    "as": "decisions"
                }},
                {"$lookup": {
                    "from": "reviews",
                    "localField": "forum",
                    "foreignField": "forum",
                    "as": "reviews"
                }},
                {"$lookup": {
                    "from": "meta_reviews",
                    "localField": "forum",
                    "foreignField": "forum",
                    "as": "meta_reviews"
                }},
                {"$lookup": {
                    "from": "official_comments",
                    "localField": "forum",
                    "foreignField": "forum",
                    "as": "official_comments"
                }},                
            ]

            result = list(self.db["submissions"].aggregate(pipeline))

            if not result:
                return None

            # Format: collection_name -> list of docs
            submission_data = result[0]
            return submission_data

        except Exception as e:
            self.colored_print.error(f"Error in get_all_data_of_submission for forum {forum_id}: {str(e)}")
            self.logger.error(f"Error in get_all_data_of_submission for forum {forum_id}: {str(e)}")
            return None
        
    
    def find_value_counts(self, collection_name: str, field_name: str) -> List[Dict[str, Any]]:
        """
        Finds unique values for a field, counts their occurrences, and sorts the
        results in descending order of frequency.

        Args:
            collection_name (str): The name of the MongoDB collection to query.
            field_name (str): The name of the field for which to count values.

        Returns:
            List[Dict[str, Any]]: A sorted list of dictionaries, where each dictionary
                                  contains the 'value' and its 'count'.
                                  Example: [{'value': 'Accept', 'count': 150}, {'value': 'Reject', 'count': 95}]
                                  Returns an empty list if an error occurs.
        """
        try:
            # Dynamically create the field reference (e.g., "$decision")
            field_to_group = f"${field_name}"

            pipeline = [
                # Stage 1: Group by the unique values and count occurrences
                {
                    "$group": {
                        "_id": field_to_group,
                        "count": {"$sum": 1}  # For each document in a group, add 1 to the count
                    }
                },
                
                # Stage 2: Sort the results by the 'count' field in descending order (-1)
                {
                    "$sort": {"count": -1}
                },

                # Stage 3 (Optional but recommended): Reshape the output for clarity
                {
                    "$project": {
                        "_id": 0,  # Exclude the default '_id' field
                        "value": "$_id",  # Rename '_id' to 'value'
                        "count": "$count"  # Keep the 'count' field
                    }
                }
            ]

            collection = self.db[collection_name]
            result = list(collection.aggregate(pipeline))
            return result

        except Exception as e:
            error_msg = f"Error finding value counts for field '{field_name}' from collection '{collection_name}': {str(e)}"
            self.colored_print.error(error_msg)
            self.logger.error(error_msg)
            return []

    def pull_all_submission_data_multithreadded(self, forums:list,  MAX_WORKERS:int=10, ignore_submissions_with_no_decisions=True):
        """
        Pull all submission data for a list of forum IDs using multithreading.
        Args:
            forums (list): List of forum IDs to process
            MAX_WORKERS (int): Maximum number of threads to use
        """
        # ### Create All Submission Charts in Single Document (Multithreaded)

        # A list to hold the results from all threads
        submission_complete_data = []
         # Adjust this number based on your system and DB capacity

        # The 'with' block ensures all threads are cleaned up properly
        with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            # 1. Submit all tasks to the executor. 
            # executor.submit schedules the function to be run and returns a "future" object.
            # We pass the function and its arguments here.
            future_to_forum = {
                executor.submit(self.get_all_submission_data, forum_id=forum): forum 
                for forum in forums
            }

            # 2. Create a progress bar that tracks the completion of the futures.
            # concurrent.futures.as_completed() is an iterator that yields futures as they finish.
            desc = f"Pulling data with {MAX_WORKERS} threads..."
            for future in track(concurrent.futures.as_completed(future_to_forum), 
                                description=desc, 
                                total=len(forums)):
                try:
                    # 3. Get the result from the completed future
                    data = future.result()
                    if data: # Ensure data was actually returned
                        submission_complete_data.append(data)
                except Exception as exc:
                    # 4. Handle any errors that occurred inside the thread
                    forum_id = future_to_forum[future]
                    print(f'Forum {forum_id} generated an exception: {exc}')
        
        if ignore_submissions_with_no_decisions:
            submission_complete_data_with_decisions=[submission for submission in submission_complete_data if len(submission["decisions"]) != 0]
            submission_complete_data = submission_complete_data_with_decisions   

        return submission_complete_data

if __name__ == '__main__':
    mongo_abstractor = MongoAbstractor(db_name='openreview_db')
    forum_id = 'zzqn5G9fjn'  # Example forum ID
    domain = 'ICLR.cc/2024/Conference'
    
    submission_data = mongo_abstractor.find_one(collection_name="submissions", query={"forum": forum_id, "domain": domain})

    if submission_data:
        print(f"Title: {submission_data['title']}")
    else:
        print(f"No submission found for forum ID {forum_id} in domain {domain}.")