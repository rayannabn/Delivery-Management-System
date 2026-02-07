#!/usr/bin/env python3

import sys
sys.path.append('/home/rayan/Desktop/projects/assignment')

from models import Agent, Order, Assignment
from utils import AssignmentUtils
from database import db
from datetime import date, datetime
from bson import ObjectId
import random

print("=== POPULATING DASHBOARD WITH MORE AGENTS ===")

# Get multiple checked-in agents
agents = list(db.agents.find({'is_checked_in': True}).limit(10))
print(f"Found {len(agents)} checked-in agents")

assignments_created = 0
total_orders_assigned = 0
total_distance = 0
total_cost = 0

for i, agent in enumerate(agents):
    agent_id = str(agent['_id'])
    warehouse_id = str(agent['warehouse_id'])
    
    print(f"\n--- Processing Agent {i+1}: {agent['name']} ---")
    
    # Get pending orders for this agent's warehouse
    orders = list(db.orders.find({'warehouse_id': warehouse_id, 'status': 'pending'}))
    
    if not orders:
        print(f"No pending orders for warehouse {warehouse_id}")
        continue
    
    # Try different order counts to find a feasible assignment
    feasible_orders = []
    
    for order_count in [15, 12, 10, 8, 6, 5]:
        if order_count > len(orders):
            continue
            
        test_orders = orders[:order_count]
        can_accept, metrics = AssignmentUtils.can_agent_accept_orders(agent_id, test_orders)
        
        if can_accept:
            feasible_orders = test_orders
            print(f"✓ Can accept {order_count} orders")
            print(f"  Distance: {metrics['total_distance']:.1f} km")
            print(f"  Earnings: ₹{metrics['total_earning']}")
            break
        else:
            print(f"✗ Cannot accept {order_count} orders: {metrics.get('error', 'Unknown')}")
    
    if feasible_orders:
        # Create assignment
        assignment_data = {
            'agent_id': agent_id,
            'order_ids': [str(order['_id']) for order in feasible_orders],
            'assignment_date': date.today().isoformat(),
            'total_distance': metrics['total_distance'],
            'total_time': metrics['total_time'],
            'earning_per_order': metrics['earning_per_order'],
            'total_earning': metrics['total_earning'],
            'created_at': datetime.utcnow()
        }
        
        result = Assignment.create(assignment_data)
        
        # Update orders
        for order in feasible_orders:
            Order.assign_to_agent(str(order['_id']), agent_id)
        
        assignments_created += 1
        total_orders_assigned += len(feasible_orders)
        total_distance += metrics['total_distance']
        total_cost += metrics['total_earning']
        
        print(f"✓ Created assignment with {len(feasible_orders)} orders")
    else:
        print(f"✗ No feasible assignment found for {agent['name']}")

print(f"\n=== SUMMARY ===")
print(f"Assignments created: {assignments_created}")
print(f"Total orders assigned: {total_orders_assigned}")
print(f"Total distance: {total_distance:.1f} km")
print(f"Total cost: ₹{total_cost}")

# Verify the results
print(f"\n=== VERIFICATION ===")
all_assignments = list(db.assignments.find({'assignment_date': date.today().isoformat()}))
print(f"Total assignments in database: {len(all_assignments)}")

if all_assignments:
    print("\nAssignment details:")
    for assignment in all_assignments:
        agent = db.agents.find_one({'_id': ObjectId(assignment['agent_id'])})
        agent_name = agent['name'] if agent else 'Unknown'
        print(f"  {agent_name}: {len(assignment['order_ids'])} orders, "
              f"{assignment['total_distance']:.1f} km, ₹{assignment['total_earning']}")

print(f"\n✅ Dashboard populated successfully!")
print(f"Visit http://localhost:5000 to see the updated dashboard")
