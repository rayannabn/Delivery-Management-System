#!/usr/bin/env python3

import sys
sys.path.append('/home/rayan/Desktop/projects/assignment')

from database import db
from bson import ObjectId

print("=== CHECKING ORDERS IN DATABASE ===")

# Check total orders
total_orders = db.orders.count_documents({})
print(f"Total orders in database: {total_orders}")

# Check orders by status
pending_orders = db.orders.count_documents({'status': 'pending'})
assigned_orders = db.orders.count_documents({'status': 'assigned'})
deferred_orders = db.orders.count_documents({'status': 'deferred'})

print(f"Pending orders: {pending_orders}")
print(f"Assigned orders: {assigned_orders}")
print(f"Deferred orders: {deferred_orders}")

# Check assignments
total_assignments = db.assignments.count_documents({})
print(f"Total assignments: {total_assignments}")

# Show a sample order
sample_order = db.orders.find_one()
if sample_order:
    print(f"\nSample order:")
    print(f"  ID: {sample_order['_id']}")
    print(f"  Order ID: {sample_order['order_id']}")
    print(f"  Status: {sample_order['status']}")
    print(f"  Warehouse: {sample_order['warehouse_id']}")

# Show sample assignment
sample_assignment = db.assignments.find_one()
if sample_assignment:
    print(f"\nSample assignment:")
    print(f"  ID: {sample_assignment['_id']}")
    print(f"  Agent: {sample_assignment['agent_id']}")
    print(f"  Orders: {len(sample_assignment['order_ids'])}")
    print(f"  Date: {sample_assignment['assignment_date']}")
