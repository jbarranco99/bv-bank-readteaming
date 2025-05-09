"""
Database module for the Responsible AI Testing System.
Handles connections and operations with MongoDB.

This module provides a Database class that manages all interactions with MongoDB,
including storing and retrieving test results, prompt examples, and attack strategies.
"""

import os
from datetime import datetime
from typing import Dict, List, Any, Optional
from pymongo import MongoClient
from dotenv import load_dotenv
import random

# Load environment variables for database configuration
load_dotenv()

# MongoDB connection settings from environment variables
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
DB_NAME = os.getenv("MONGO_DB_NAME", "rai_testing")


class Database:
    """
    MongoDB database manager for the RAI Testing System.
    Handles all database operations including connections, queries, and data storage.
    """
    
    def __init__(self):
        """
        Initialize database connection and set up collection references.
        Uses environment variables for connection settings.
        """
        self.client = MongoClient(MONGO_URI)
        self.db = self.client[DB_NAME]
        
        # Collection references for different data types
        self.prompt_collection = self.db["prompt_examples_pp"]
        self.attack_strategy_collection = self.db["attack_types_pp"]
        self.test_result_collection = self.db["test_results_pp"]
                


    def get_active_prompts(self, attack_type: str, limit: int = 20) -> List[Dict]:
        """
        Retrieve active prompt examples for a specific attack type.
        
        Args:
            attack_type: Type of attack to filter prompts ('free' for random mix)
            limit: Maximum number of prompts to retrieve
            
        Returns:
            List of prompt documents matching the criteria
        """
        if attack_type == "free":
            # Aggregate random prompts across all active ones
            pipeline = [
                {"$match": {"active": True}},
                {"$sample": {"size": limit}}
            ]
            return list(self.prompt_collection.aggregate(pipeline))
        else:
            # Standard filtered query
            query = {"active": True, "attack_type": attack_type}
            return list(self.prompt_collection.find(query).limit(limit))

    
    def get_attack_strategy(self, attack_type: str, limit: int = 100) -> List[Dict]:
        """
        Retrieve the strategy document for a specific attack type.
        
        Args:
            attack_type: The type of attack to get strategy for
            limit: Maximum number of documents to retrieve
            
        Returns:
            Strategy document for the specified attack type
        """
        return self.attack_strategy_collection.find_one({"attack_type": attack_type})
    
    def save_test_result(
        self,
        attack_type: str,
        language: str,
        tester_instructions: str,
        strategy: str,
        prompt_examples: str,
        success: bool,
        success_reason: str,
        learnings: str,
        conversation: str,
        turns: int
        ) -> str:
        """
        Save a red teaming test result to the database.
        
        Args:
            attack_type: Type of attack tested
            language: Language used in test
            tester_instructions: Instructions given to tester
            strategy: Attack strategy used
            prompt_examples: Examples used for guidance
            success: Whether test was successful
            success_reason: Explanation of success/failure
            learnings: Insights gained from test
            conversation: Full conversation log
            turns: Number of conversation turns
            
        Returns:
            ID of the inserted document
        """

        result = {
            "attack_type": attack_type,
            "language": language,
            "tester_instructions": tester_instructions,
            "strategy": strategy,
            "prompt_examples": self.array_to_string(prompt_examples),
            "success": success,
            "success_reason": success_reason,
            "learnings": learnings,
            "conversation": self.array_to_string(conversation),
            "n_of_total_turns": turns,
            "date_created": datetime.utcnow()
        }

        inserted = self.test_result_collection.insert_one(result)
        return str(inserted.inserted_id)

    def close(self):
        """Close the MongoDB connection."""
        self.client.close()

    def get_previous_learnings(self, attack_type: str, limit: int = 20) -> str:
        """
        Retrieve learnings from previous tests of the same attack type.
        
        Args:
            attack_type: Type of attack to get learnings for
            limit: Maximum number of learning entries to retrieve
            
        Returns:
            Newline-separated string of learning insights
        """
        pipeline = [
            {"$match": {"attack_type": attack_type, "learnings": {"$ne": ""}}},
            {"$sample": {"size": limit}},
            {"$project": {"learnings": 1, "_id": 0}}
        ]

        results = self.test_result_collection.aggregate(pipeline)
        learnings = [doc["learnings"] for doc in results]

        return "\n".join(learnings) if learnings else None


    @staticmethod
    def array_to_string(messages: list) -> str:
        """
        Convert a list of conversation messages to a formatted string.
        
        Args:
            messages: List of dialogue turns
            
        Returns:
            Newline-joined string of messages
        """
        return "\n".join(messages)
    
def main():
    """Entry point for direct script execution."""
    if __name__ == "__main__":
        db = Database()

if __name__ == "__main__":
    main()