#!/usr/bin/env python3

import sys
sys.path.append('/home/rayan/Desktop/projects/assignment')

from models import Agent, Order, Assignment
from utils import AssignmentUtils
from database import db
from datetime import date, datetime
from bson import ObjectId

print("=== TESTING MANUAL ASSIGNMENT WITHOUT AUTO ALLOCATION ===")

# Reset orders first
print("Resetting orders...")
result = db.orders.update_many(
    {'status': 'deferred'},
    {
        '$set': {
            'status': 'pending',
            'assigned_agent_id': None,
            'assigned_at': None
        }
    }
)
print(f"Reset {result.modified_count} orders")

# Get a checked-in agent
agents = list(db.agents.find({'is_checked_in': True}).limit(1))
agent = agents[0]
agent_id = str(agent['_id'])
print(f"Using agent: {agent['name']}")

# Get some orders for the same warehouse
warehouse_id = str(agent['warehouse_id'])
orders = list(db.orders.find({'warehouse_id': warehouse_id, 'status': 'pending'}).limit(10))

print(f"Found {len(orders)} pending orders for warehouse {warehouse_id}")

if orders:
    # Test if agent can accept these orders
    can_accept, metrics = AssignmentUtils.can_agent_accept_orders(agent_id, orders)
    print(f"Can accept orders: {can_accept}")
    print(f"Metrics: {metrics}")
    
    if can_accept:
        # Create assignment manually
        assignment_data = {
            'agent_id': agent_id,
            'order_ids': [str(order['_id']) for order in orders],
            'assignment_date': date.today().isoformat(),
            'total_distance': metrics['total_distance'],
            'total_time': metrics['total_time'],
            'earning_per_order': metrics['earning_per_order'],
            'total_earning': metrics['total_earning'],
            'created_at': datetime.utcnow()
        }
        
        print("Creating assignment...")
        result = Assignment.create(assignment_data)
        print(f"Assignment created: {result.inserted_id}")
        
        # Update orders
        for order in orders:
            Order.assign_to_agent(str(order['_id']), agent_id)
        
        print(f"Updated {len(orders)} orders to 'assigned' status")
        
        # Verify
        assignment = db.assignments.find_one({'_id': result.inserted_id})
        print(f"Assignment verified: {assignment is not None}")
    else:
        print("Cannot create assignment - constraints not met")
else:
    print("No orders found")
