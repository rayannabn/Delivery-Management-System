#!/usr/bin/env python3

import sys
sys.path.append('/home/rayan/Desktop/projects/assignment')

from models import Agent, Order, Assignment
from utils import AssignmentUtils
from database import db
from datetime import date
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def debug_allocation():
    print("=== DEBUGGING ALLOCATION ===")
    
    # Check checked-in agents
    checked_in_agents = Agent.get_checked_in_agents()
    print(f"Checked-in agents: {len(checked_in_agents)}")
    
    if checked_in_agents:
        print(f"First agent: {checked_in_agents[0]['name']}, Warehouse: {checked_in_agents[0]['warehouse_id']}")
    
    # Check pending orders
    pending_orders = Order.get_pending_orders()
    print(f"Pending orders: {len(pending_orders)}")
    
    if pending_orders:
        print(f"First order: {pending_orders[0]['order_id']}, Warehouse: {pending_orders[0]['warehouse_id']}")
    
    # Check orders by warehouse for first agent's warehouse
    if checked_in_agents:
        warehouse_id = checked_in_agents[0]['warehouse_id']
        warehouse_orders = Order.get_by_warehouse(warehouse_id)
        print(f"Orders for warehouse {warehouse_id}: {len(warehouse_orders)}")
        
        if warehouse_orders:
            # Test constraint checking with different order counts
            agent_id = str(checked_in_agents[0]['_id'])
            
            for order_count in [5, 10, 15, 20]:
                test_orders = warehouse_orders[:order_count]
                
                print(f"\nTesting {order_count} orders:")
                can_accept, metrics = AssignmentUtils.can_agent_accept_orders(agent_id, test_orders)
                
                print(f"Can accept: {can_accept}")
                if can_accept:
                    print(f"Metrics: {metrics}")
                    break
                else:
                    print(f"Error: {metrics.get('error', 'Unknown error')}")
    
    # Check existing assignments
    today = date.today()
    assignments = Assignment.get_by_date(today)
    print(f"Existing assignments for {today}: {len(assignments)}")

if __name__ == "__main__":
    debug_allocation()
