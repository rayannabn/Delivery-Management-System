from datetime import datetime, date
from typing import List, Dict, Optional
from database import db
from bson import ObjectId

class Warehouse:
    def __init__(self, name: str, latitude: float, longitude: float, city: str):
        self.name = name
        self.latitude = latitude
        self.longitude = longitude
        self.city = city
        self.created_at = datetime.utcnow()
    
    def to_dict(self):
        return {
            'name': self.name,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'city': self.city,
            'created_at': self.created_at
        }
    
    @classmethod
    def create(cls, warehouse_data):
        return db.warehouses.insert_one(warehouse_data)
    
    @classmethod
    def get_all(cls):
        return list(db.warehouses.find())
    
    @classmethod
    def get_by_id(cls, warehouse_id):
        return db.warehouses.find_one({'_id': ObjectId(warehouse_id)})

class Agent:
    def __init__(self, name: str, warehouse_id: str, phone: str):
        self.name = name
        self.warehouse_id = warehouse_id
        self.phone = phone
        self.is_checked_in = False
        self.checked_in_at = None
        self.created_at = datetime.utcnow()
    
    def to_dict(self):
        return {
            'name': self.name,
            'warehouse_id': self.warehouse_id,
            'phone': self.phone,
            'is_checked_in': self.is_checked_in,
            'checked_in_at': self.checked_in_at,
            'created_at': self.created_at
        }
    
    @classmethod
    def create(cls, agent_data):
        return db.agents.insert_one(agent_data)
    
    @classmethod
    def get_all(cls):
        return list(db.agents.find())
    
    @classmethod
    def get_checked_in_agents(cls):
        return list(db.agents.find({'is_checked_in': True}))
    
    @classmethod
    def check_in(cls, agent_id):
        return db.agents.update_one(
            {'_id': ObjectId(agent_id)},
            {
                '$set': {
                    'is_checked_in': True,
                    'checked_in_at': datetime.utcnow()
                }
            }
        )
    
    @classmethod
    def check_out_all(cls):
        return db.agents.update_many(
            {'is_checked_in': True},
            {
                '$set': {
                    'is_checked_in': False,
                    'checked_in_at': None
                }
            }
        )

class Order:
    def __init__(self, order_id: str, customer_name: str, customer_phone: str, 
                 delivery_address: str, latitude: float, longitude: float, 
                 warehouse_id: str, order_date: date = None):
        self.order_id = order_id
        self.customer_name = customer_name
        self.customer_phone = customer_phone
        self.delivery_address = delivery_address
        self.latitude = latitude
        self.longitude = longitude
        self.warehouse_id = warehouse_id
        self.order_date = order_date or date.today()
        self.status = 'pending'  # pending, assigned, delivered, deferred
        self.assigned_agent_id = None
        self.assigned_at = None
        self.created_at = datetime.utcnow()
    
    def to_dict(self):
        return {
            'order_id': self.order_id,
            'customer_name': self.customer_name,
            'customer_phone': self.customer_phone,
            'delivery_address': self.delivery_address,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'warehouse_id': self.warehouse_id,
            'order_date': self.order_date.isoformat() if self.order_date else None,
            'status': self.status,
            'assigned_agent_id': self.assigned_agent_id,
            'assigned_at': self.assigned_at,
            'created_at': self.created_at
        }
    
    @classmethod
    def create(cls, order_data):
        return db.orders.insert_one(order_data)
    
    @classmethod
    def get_pending_orders(cls):
        return list(db.orders.find({'status': 'pending'}))
    
    @classmethod
    def get_by_warehouse(cls, warehouse_id):
        return list(db.orders.find({'warehouse_id': warehouse_id, 'status': 'pending'}))
    
    @classmethod
    def assign_to_agent(cls, order_id, agent_id):
        return db.orders.update_one(
            {'_id': ObjectId(order_id)},
            {
                '$set': {
                    'status': 'assigned',
                    'assigned_agent_id': agent_id,
                    'assigned_at': datetime.utcnow()
                }
            }
        )
    
    @classmethod
    def defer_orders(cls, order_ids):
        return db.orders.update_many(
            {'_id': {'$in': [ObjectId(oid) for oid in order_ids]}},
            {
                '$set': {
                    'status': 'deferred',
                    'assigned_agent_id': None,
                    'assigned_at': None
                }
            }
        )

class Assignment:
    def __init__(self, agent_id: str, order_ids: List[str], assignment_date: date):
        self.agent_id = agent_id
        self.order_ids = order_ids
        self.assignment_date = assignment_date
        self.total_distance = 0  # km
        self.total_time = 0  # hours
        total_orders = len(order_ids)
        self.earning_per_order = self._calculate_payment_rate(total_orders)
        self.total_earning = total_orders * self.earning_per_order
        self.created_at = datetime.utcnow()
    
    def _calculate_payment_rate(self, total_orders: int) -> int:
        from config import Config
        if total_orders >= Config.TIER_2_ORDERS:
            return Config.TIER_2_PAYMENT
        elif total_orders >= Config.TIER_1_ORDERS:
            return Config.TIER_1_PAYMENT
        else:
            return Config.DEFAULT_PAYMENT
    
    def to_dict(self):
        return {
            'agent_id': self.agent_id,
            'order_ids': self.order_ids,
            'assignment_date': self.assignment_date.isoformat(),
            'total_distance': self.total_distance,
            'total_time': self.total_time,
            'earning_per_order': self.earning_per_order,
            'total_earning': self.total_earning,
            'created_at': self.created_at
        }
    
    @classmethod
    def create(cls, assignment_data):
        return db.assignments.insert_one(assignment_data)
    
    @classmethod
    def get_by_date(cls, assignment_date: date):
        return list(db.assignments.find({'assignment_date': assignment_date.isoformat()}))
    
    @classmethod
    def get_by_agent(cls, agent_id: str, assignment_date: date):
        return db.assignments.find_one({
            'agent_id': agent_id,
            'assignment_date': assignment_date.isoformat()
        })
