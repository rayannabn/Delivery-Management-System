#!/usr/bin/env python3

import sys
sys.path.append('/home/rayan/Desktop/projects/assignment')

from database import db
from datetime import date

print("=== CHECKING ASSIGNMENTS ===")

# Check all assignments
all_assignments = list(db.assignments.find({}))
print(f"Total assignments in database: {len(all_assignments)}")

# Check today's assignments
today = date.today()
today_str = today.isoformat()
print(f"Today's date: {today_str}")

today_assignments = list(db.assignments.find({'assignment_date': today_str}))
print(f"Assignments for today ({today_str}): {len(today_assignments)}")

# Show assignment details
if today_assignments:
    print("\nToday's assignments:")
    for i, assignment in enumerate(today_assignments[:3]):
        print(f"  Assignment {i+1}:")
        print(f"    ID: {assignment['_id']}")
        print(f"    Agent: {assignment['agent_id']}")
        print(f"    Date: {assignment['assignment_date']}")
        print(f"    Orders: {len(assignment['order_ids'])}")
        print(f"    Distance: {assignment['total_distance']}")
        print(f"    Earnings: {assignment['total_earning']}")
else:
    print("No assignments found for today")
    
    # Show all assignment dates
    all_dates = db.assignments.distinct('assignment_date')
    print(f"All assignment dates in database: {all_dates}")

# Check if there are any assignments with different date format
print(f"\nChecking for date format issues...")
for assignment in all_assignments[:5]:
    print(f"  Date: '{assignment['assignment_date']}' (type: {type(assignment['assignment_date'])})")
