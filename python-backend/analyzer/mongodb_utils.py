"""
MongoDB connection utilities for the Startup Analyzer.
Provides singleton client and collection accessors.
"""

from pymongo import MongoClient
from django.conf import settings

_client = None


def get_mongo_client():
    """Get or create MongoDB client singleton."""
    global _client
    if _client is None:
        _client = MongoClient(settings.MONGO_URI)
    return _client


def get_database():
    """Get the startup_analyzer database."""
    return get_mongo_client()[settings.MONGO_DB_NAME]


def get_users_collection():
    """Get the users collection."""
    db = get_database()
    users = db['users']
    # Ensure email index exists
    users.create_index('email', unique=True)
    return users


def get_projects_collection():
    """Get the projects collection."""
    db = get_database()
    projects = db['projects']
    # Ensure user_id index for faster queries
    projects.create_index('user_id')
    projects.create_index('created_at')
    return projects
