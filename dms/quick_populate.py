#!/usr/bin/env python3

import sys
sys.path.append('/home/rayan/Desktop/projects/assignment')

from models import Agent, Order, Assignment
from utils import AssignmentUtils
from database import db
from datetime import date, datetime
from bson import ObjectId

print("=== QUICK DASHBOARD POPULATION ===")

# Get checked-in agents
agents = list(db.agents.find({'is_checked_in': True}).limit(8))
print(f"Found {len(agents)} agents")

assignments_created = 0

for i, agent in enumerate(agents):
    agent_id = str(agent['_id'])
    warehouse_id = str(agent['warehouse_id'])
    
    # Get pending orders for this warehouse
    orders = list(db.orders.find({'warehouse_id': warehouse_id, 'status': 'pending'}).limit(12))
    
    if len(orders) < 8:
        print(f"Agent {i+1}: {agent['name']} - Only {len(orders)} orders available")
        continue
    
    # Try to assign 8-12 orders
    test_orders = orders[:8] if i % 2 == 0 else orders[:10]
    
    can_accept, metrics = AssignmentUtils.can_agent_accept_orders(agent_id, test_orders)
    
    if can_accept:
        # Create assignment
        assignment_data = {
            'agent_id': agent_id,
            'order_ids': [str(order['_id']) for order in test_orders],
            'assignment_date': date.today().isoformat(),
            'total_distance': metrics['total_distance'],
            'total_time': metrics['total_time'],
            'earning_per_order': metrics['earning_per_order'],
            'total_earning': metrics['total_earning'],
            'created_at': datetime.utcnow()
        }
        
        result = Assignment.create(assignment_data)
        
        # Update orders
        for order in test_orders:
            Order.assign_to_agent(str(order['_id']), agent_id)
        
        assignments_created += 1
        print(f"✓ Agent {i+1}: {agent['name']} - {len(test_orders)} orders, ₹{metrics['total_earning']}")
    else:
        print(f"✗ Agent {i+1}: {agent['name']} - Cannot assign orders")

print(f"\nCreated {assignments_created} assignments")

# Check final results
assignments = list(db.assignments.find({'assignment_date': date.today().isoformat()}))
print(f"Total assignments in database: {len(assignments)}")

if assignments:
    total_orders = sum(len(a['order_ids']) for a in assignments)
    total_cost = sum(a['total_earning'] for a in assignments)
    total_distance = sum(a['total_distance'] for a in assignments)
    
    print(f"Total orders assigned: {total_orders}")
    print(f"Total cost: ₹{total_cost}")
    print(f"Total distance: {total_distance:.1f} km")
    print(f"Average orders per agent: {total_orders/len(assignments):.1f}")

print(f"\n🎉 Dashboard is ready! Visit http://localhost:5000")
