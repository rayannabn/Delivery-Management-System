import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
    DB_NAME = os.getenv('DB_NAME', 'delivery_management')
    
    # Business constraints
    MAX_WORKING_HOURS_PER_DAY = 15  # hours (very relaxed for demo)
    MAX_TRAVEL_DISTANCE_PER_DAY = 200  # km (very relaxed for demo)
    MINUTES_PER_KM = 3  # travel time per km (faster travel for demo)
    
    # Payment tiers
    MIN_DAILY_EARNING = 50  # rupees (reduced from 500 for demo)
    TIER_1_ORDERS = 15  # orders per day (reduced from 25)
    TIER_1_PAYMENT = 35  # rupees per order
    TIER_2_ORDERS = 30  # orders per day (reduced from 50)
    TIER_2_PAYMENT = 42  # rupees per order
    DEFAULT_PAYMENT = 30  # rupees per order for <15 orders
