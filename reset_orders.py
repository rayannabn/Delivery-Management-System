#!/usr/bin/env python3

import sys
sys.path.append('/home/rayan/Desktop/projects/assignment')

from database import db

print("=== RESETTING DEFERRED ORDERS TO PENDING ===")

# Reset all deferred orders to pending
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

print(f"Reset {result.modified_count} orders from deferred to pending")

# Clear existing assignments
db.assignments.delete_many({})
print("Cleared all assignments")

print("Ready for new allocation run!")
