#!/usr/bin/env python3

import sys
sys.path.append('/home/rayan/Desktop/projects/assignment')

from database import db
from bson import ObjectId

print("=== DEBUGGING WAREHOUSE MATCHING ===")

# Get a checked-in agent
agents = list(db.agents.find({'is_checked_in': True}).limit(1))
agent = agents[0]

print(f"Agent: {agent['name']}")
print(f"Agent warehouse_id: {agent['warehouse_id']} (type: {type(agent['warehouse_id'])})")

# Check orders with that warehouse ID
warehouse_id = agent['warehouse_id']
orders = list(db.orders.find({'warehouse_id': warehouse_id, 'status': 'pending'}).limit(5))

print(f"Orders found with exact warehouse_id: {len(orders)}")

# Try with ObjectId
warehouse_obj_id = ObjectId(warehouse_id)
orders_obj = list(db.orders.find({'warehouse_id': warehouse_obj_id, 'status': 'pending'}).limit(5))

print(f"Orders found with ObjectId: {len(orders_obj)}")

# Show all distinct warehouse IDs in orders
order_warehouses = db.orders.distinct('warehouse_id')
agent_warehouses = db.agents.distinct('warehouse_id')

print(f"\nDistinct warehouse IDs in orders: {len(order_warehouses)}")
print(f"Distinct warehouse IDs in agents: {len(agent_warehouses)}")

# Check if they match
if str(order_warehouses[0]) in [str(w) for w in agent_warehouses]:
    print("✓ Warehouse IDs match between orders and agents")
else:
    print("✗ Warehouse IDs don't match!")
    print(f"Sample order warehouse: {order_warehouses[0]}")
    print(f"Sample agent warehouse: {agent_warehouses[0]}")
