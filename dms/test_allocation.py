#!/usr/bin/env python3
"""
Test script to verify the allocation engine functionality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from seed_data import SeedDataGenerator
from allocation_engine import allocation_engine
from scheduler import scheduler
from utils import AssignmentUtils
from database import db
from datetime import date, datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_allocation_system():
    """Test the complete allocation system"""
    print("="*60)
    print("DELIVERY MANAGEMENT SYSTEM - ALLOCATION TEST")
    print("="*60)
    
    try:
        # Step 1: Generate seed data
        print("\n1. Generating seed data...")
        generator = SeedDataGenerator()
        summary = generator.generate_complete_dataset()
        print(f"   ✓ Generated {summary['warehouses']} warehouses")
        print(f"   ✓ Generated {summary['agents']} agents")
        print(f"   ✓ Generated {summary['orders']} orders")
        print(f"   ✓ Checked in {summary['checked_in_agents']} agents")
        
        # Step 2: Run allocation
        print("\n2. Running order allocation...")
        result = allocation_engine.run_allocation()
        
        if result['status'] == 'success':
            print(f"   ✓ Allocation completed successfully")
            print(f"   ✓ Total orders assigned: {result['total_assigned']}")
            print(f"   ✓ Total orders deferred: {result['total_deferred']}")
        else:
            print(f"   ✗ Allocation failed: {result.get('message', 'Unknown error')}")
            return False
        
        # Step 3: Generate summary
        print("\n3. Generating daily summary...")
        today = date.today().isoformat()
        summary = AssignmentUtils.generate_daily_summary(today)
        
        print(f"   Date: {summary['date']}")
        print(f"   Total agents working: {summary['total_agents']}")
        print(f"   Total orders assigned: {summary['total_orders']}")
        print(f"   Total distance traveled: {summary['total_distance']} km")
        print(f"   Total cost: ₹{summary['total_cost']:,}")
        print(f"   Average orders per agent: {summary['avg_orders_per_agent']}")
        print(f"   Deferred orders: {summary['deferred_orders']}")
        
        # Step 4: Show sample assignments
        print("\n4. Sample assignments:")
        from models import Assignment
        assignments = Assignment.get_by_date(date.today())
        
        if assignments:
            print(f"   Showing first 3 assignments:")
            for i, assignment in enumerate(assignments[:3]):
                print(f"   Assignment {i+1}:")
                print(f"     Agent ID: {assignment['agent_id']}")
                print(f"     Orders: {len(assignment['order_ids'])}")
                print(f"     Distance: {assignment['total_distance']:.2f} km")
                print(f"     Earning: ₹{assignment['total_earning']}")
                print(f"     Rate: ₹{assignment['earning_per_order']}/order")
        
        print("\n" + "="*60)
        print("TEST COMPLETED SUCCESSFULLY!")
        print("="*60)
        return True
        
    except Exception as e:
        print(f"\n✗ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_scheduler():
    """Test the scheduler functionality"""
    print("\n" + "="*60)
    print("SCHEDULER TEST")
    print("="*60)
    
    try:
        print("Starting scheduler...")
        scheduler.start()
        print("✓ Scheduler started successfully")
        
        # Test manual allocation trigger
        print("Testing manual allocation trigger...")
        result = scheduler.run_allocation_now()
        print(f"✓ Manual allocation completed: {result['status']}")
        
        print("Stopping scheduler...")
        scheduler.stop()
        print("✓ Scheduler stopped successfully")
        
        return True
        
    except Exception as e:
        print(f"✗ Scheduler test failed: {str(e)}")
        return False

def cleanup_database():
    """Clean up the database after testing"""
    print("\nCleaning up database...")
    try:
        db.warehouses.delete_many({})
        db.agents.delete_many({})
        db.orders.delete_many({})
        db.assignments.delete_many({})
        print("✓ Database cleaned up")
    except Exception as e:
        print(f"✗ Cleanup failed: {str(e)}")

if __name__ == "__main__":
    # Ask user if they want to run tests
    print("This test will:")
    print("1. Generate sample data (10 warehouses, 200 agents, ~10,000 orders)")
    print("2. Run the allocation algorithm")
    print("3. Display results and metrics")
    print("4. Clean up the database")
    
    response = input("\nDo you want to proceed? (y/n): ").lower().strip()
    
    if response == 'y':
        success = test_allocation_system()
        
        if success:
            response2 = input("\nDo you want to test the scheduler as well? (y/n): ").lower().strip()
            if response2 == 'y':
                test_scheduler()
        
        response3 = input("\nDo you want to clean up the database? (y/n): ").lower().strip()
        if response3 == 'y':
            cleanup_database()
        
        print("\nTest completed!")
    else:
        print("Test cancelled.")
