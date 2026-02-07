import random
from datetime import date, datetime
from models import Warehouse, Agent, Order
from database import db
import logging

logger = logging.getLogger(__name__)

class SeedDataGenerator:
    def __init__(self):
        # Bangalore coordinates for realistic data
        self.bangalore_center = (12.9716, 77.5946)
        self.city_name = "Bangalore"
        
        # Sample data
        self.first_names = ["Rahul", "Priya", "Amit", "Sneha", "Vikram", "Anjali", 
                           "Rohit", "Kavita", "Arjun", "Meera", "Karan", "Neha",
                           "Raj", "Pooja", "Vijay", "Swati", "Manoj", "Divya"]
        
        self.last_names = ["Kumar", "Sharma", "Verma", "Gupta", "Agarwal", "Singh",
                          "Jain", "Patel", "Reddy", "Nair", "Mishra", "Chopra"]
        
        self.area_names = ["Whitefield", "Electronic City", "Indiranagar", "Koramangala",
                          "HSR Layout", "BTM Layout", "Jayanagar", "Basavanagudi",
                          "Malleshwaram", "Rajajinagar", "Yelahanka", "Marathahalli",
                          "Bellandur", "Sarjapur", "Hoskote", "Devanahalli"]
    
    def generate_warehouses(self, count: int = 10):
        """Generate warehouses across the city"""
        logger.info(f"Generating {count} warehouses")
        
        warehouses = []
        for i in range(count):
            # Generate coordinates within Bangalore area
            lat_offset = random.uniform(-0.3, 0.3)  # ~33km radius
            lon_offset = random.uniform(-0.3, 0.3)
            
            warehouse = {
                'name': f"Warehouse {i+1} - {random.choice(self.area_names)}",
                'latitude': self.bangalore_center[0] + lat_offset,
                'longitude': self.bangalore_center[1] + lon_offset,
                'city': self.city_name,
                'created_at': datetime.utcnow()
            }
            
            Warehouse.create(warehouse)
            warehouses.append(warehouse)
        
        logger.info(f"Created {len(warehouses)} warehouses")
        return warehouses
    
    def generate_agents(self, warehouses: list, agents_per_warehouse: int = 20):
        """Generate agents for each warehouse"""
        logger.info(f"Generating agents: {agents_per_warehouse} per warehouse")
        
        all_agents = []
        for warehouse in warehouses:
            for i in range(agents_per_warehouse):
                agent = {
                    'name': f"{random.choice(self.first_names)} {random.choice(self.last_names)}",
                    'warehouse_id': str(warehouse['_id']),
                    'phone': f"+91-{random.randint(9000000000, 9999999999)}",
                    'is_checked_in': False,
                    'checked_in_at': None,
                    'created_at': datetime.utcnow()
                }
                
                Agent.create(agent)
                all_agents.append(agent)
        
        logger.info(f"Created {len(all_agents)} agents")
        return all_agents
    
    def generate_orders(self, warehouses: list, max_orders_per_agent: int = 60):
        """Generate orders for each warehouse"""
        logger.info(f"Generating orders for warehouses")
        
        all_orders = []
        order_counter = 1
        
        for warehouse in warehouses:
            # Calculate number of orders for this warehouse
            agents_count = len(list(db.agents.find({'warehouse_id': str(warehouse['_id'])})))
            orders_count = min(agents_count * max_orders_per_agent, 
                             random.randint(800, 1200))  # Realistic variation
            
            logger.info(f"Generating {orders_count} orders for {warehouse['name']}")
            
            for i in range(orders_count):
                # Generate delivery coordinates within reasonable distance from warehouse
                lat_offset = random.uniform(-0.15, 0.15)  # ~16km radius
                lon_offset = random.uniform(-0.15, 0.15)
                
                order = {
                    'order_id': f"ORD{order_counter:06d}",
                    'customer_name': f"{random.choice(self.first_names)} {random.choice(self.last_names)}",
                    'customer_phone': f"+91-{random.randint(9000000000, 9999999999)}",
                    'delivery_address': f"{random.randint(1, 999)}, {random.choice(self.area_names)}, {self.city_name}",
                    'latitude': warehouse['latitude'] + lat_offset,
                    'longitude': warehouse['longitude'] + lon_offset,
                    'warehouse_id': str(warehouse['_id']),
                    'order_date': date.today().isoformat(),
                    'status': 'pending',
                    'assigned_agent_id': None,
                    'assigned_at': None,
                    'created_at': datetime.utcnow()
                }
                
                Order.create(order)
                all_orders.append(order)
                order_counter += 1
        
        logger.info(f"Created {len(all_orders)} total orders")
        return all_orders
    
    def check_in_random_agents(self, check_in_percentage: float = 0.8):
        """Check in random percentage of agents"""
        all_agents = list(Agent.get_all())
        check_in_count = int(len(all_agents) * check_in_percentage)
        
        # Randomly select agents to check in
        agents_to_check_in = random.sample(all_agents, check_in_count)
        
        for agent in agents_to_check_in:
            Agent.check_in(str(agent['_id']))
        
        logger.info(f"Checked in {len(agents_to_check_in)} out of {len(all_agents)} agents")
        return len(agents_to_check_in)
    
    def clear_all_data(self):
        """Clear all existing data"""
        logger.warning("Clearing all existing data")
        
        db.warehouses.delete_many({})
        db.agents.delete_many({})
        db.orders.delete_many({})
        db.assignments.delete_many({})
        
        logger.info("All data cleared")
    
    def generate_complete_dataset(self):
        """Generate complete dataset for testing"""
        logger.info("Starting complete dataset generation")
        
        # Clear existing data
        self.clear_all_data()
        
        # Generate warehouses
        warehouses = self.generate_warehouses(10)
        
        # Generate agents
        agents = self.generate_agents(warehouses, 20)
        
        # Generate orders
        orders = self.generate_orders(warehouses, 60)
        
        # Check in some agents
        checked_in_count = self.check_in_random_agents(0.8)
        
        summary = {
            'warehouses': len(warehouses),
            'agents': len(agents),
            'orders': len(orders),
            'checked_in_agents': checked_in_count,
            'estimated_total_cost': len(orders) * 35  # Rough estimate
        }
        
        logger.info(f"Dataset generation completed: {summary}")
        return summary

def main():
    """Main function to run seed data generation"""
    generator = SeedDataGenerator()
    summary = generator.generate_complete_dataset()
    
    print("\n" + "="*50)
    print("SEED DATA GENERATION COMPLETED")
    print("="*50)
    print(f"Warehouses created: {summary['warehouses']}")
    print(f"Agents created: {summary['agents']}")
    print(f"Orders created: {summary['orders']}")
    print(f"Agents checked in: {summary['checked_in_agents']}")
    print(f"Estimated daily cost: ₹{summary['estimated_total_cost']:,}")
    print("="*50)
    print("\nYou can now run the allocation engine to assign orders!")

if __name__ == "__main__":
    main()
