from pymongo import MongoClient
from config import Config

class Database:
    def __init__(self):
        self.client = MongoClient(Config.MONGODB_URI)
        self.db = self.client[Config.DB_NAME]
    
    def get_collection(self, collection_name):
        return self.db[collection_name]
    
    # Collections
    @property
    def warehouses(self):
        return self.db.warehouses
    
    @property
    def agents(self):
        return self.db.agents
    
    @property
    def orders(self):
        return self.db.orders
    
    @property
    def assignments(self):
        return self.db.assignments

# Global database instance
db = Database()
