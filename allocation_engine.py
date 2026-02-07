from datetime import date, datetime
from typing import List, Dict, Tuple
from database import db
from models import Agent, Order, Assignment
from utils import LocationUtils, AssignmentUtils
from config import Config
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OrderAllocationEngine:
    def __init__(self):
        self.today = date.today()
    
    def run_allocation(self) -> Dict:
        """Main allocation method that runs the complete allocation process"""
        logger.info(f"Starting order allocation for {self.today}")
        
        # Get all checked-in agents
        checked_in_agents = Agent.get_checked_in_agents()
        logger.info(f"Found {len(checked_in_agents)} checked-in agents")
        
        if not checked_in_agents:
            logger.warning("No agents checked in today")
            return {'status': 'failed', 'message': 'No agents checked in'}
        
        # Group agents by warehouse
        warehouse_agents = {}
        for agent in checked_in_agents:
            warehouse_id = agent['warehouse_id']
            if warehouse_id not in warehouse_agents:
                warehouse_agents[warehouse_id] = []
            warehouse_agents[warehouse_id].append(agent)
        
        # Process each warehouse
        total_assigned = 0
        total_deferred = 0
        
        for warehouse_id, agents in warehouse_agents.items():
            logger.info(f"Processing warehouse {warehouse_id} with {len(agents)} agents")
            
            # Get pending orders for this warehouse
            pending_orders = Order.get_by_warehouse(warehouse_id)
            logger.info(f"Found {len(pending_orders)} pending orders for warehouse {warehouse_id}")
            
            if not pending_orders:
                continue
            
            # Allocate orders to agents
            assigned_count, deferred_orders = self._allocate_orders_for_warehouse(
                agents, pending_orders, warehouse_id
            )
            
            total_assigned += assigned_count
            total_deferred += len(deferred_orders)
            
            # Mark deferred orders
            if deferred_orders:
                deferred_ids = [str(order['_id']) for order in deferred_orders]
                Order.defer_orders(deferred_ids)
                logger.info(f"Deferred {len(deferred_orders)} orders for warehouse {warehouse_id}")
        
        # Generate summary
        summary = AssignmentUtils.generate_daily_summary(self.today.isoformat())
        
        logger.info(f"Allocation completed. Assigned: {total_assigned}, Deferred: {total_deferred}")
        
        return {
            'status': 'success',
            'date': self.today.isoformat(),
            'total_assigned': total_assigned,
            'total_deferred': total_deferred,
            'summary': summary
        }
    
    def _allocate_orders_for_warehouse(self, agents: List[Dict], 
                                      orders: List[Dict], 
                                      warehouse_id: str) -> Tuple[int, List[Dict]]:
        """Allocate orders for a specific warehouse"""
        unassigned_orders = orders.copy()
        assigned_count = 0
        
        # Sort agents by name for fair distribution
        agents.sort(key=lambda x: x['name'])
        
        for agent in agents:
            if not unassigned_orders:
                break
            
            # Find optimal order set for this agent
            optimal_orders = self._find_optimal_order_set(
                agent, unassigned_orders, warehouse_id
            )
            
            if optimal_orders:
                # Create assignment
                assignment_data = {
                    'agent_id': str(agent['_id']),
                    'order_ids': [str(order['_id']) for order in optimal_orders],
                    'assignment_date': self.today.isoformat(),
                    'total_distance': 0,  # Will be calculated below
                    'total_time': 0,
                    'earning_per_order': 0,
                    'total_earning': 0,
                    'created_at': datetime.utcnow()
                }
                
                # Calculate actual route and metrics
                can_accept, metrics = AssignmentUtils.can_agent_accept_orders(
                    str(agent['_id']), optimal_orders
                )
                
                if can_accept:
                    assignment_data.update({
                        'total_distance': metrics['total_distance'],
                        'total_time': metrics['total_time'],
                        'earning_per_order': metrics['earning_per_order'],
                        'total_earning': metrics['total_earning']
                    })
                    
                    # Save assignment
                    Assignment.create(assignment_data)
                    
                    # Mark orders as assigned
                    for order in optimal_orders:
                        Order.assign_to_agent(str(order['_id']), str(agent['_id']))
                        unassigned_orders.remove(order)
                        assigned_count += 1
                    
                    logger.info(f"Assigned {len(optimal_orders)} orders to agent {agent['name']}")
        
        return assigned_count, unassigned_orders
    
    def _find_optimal_order_set(self, agent: Dict, 
                               available_orders: List[Dict], 
                               warehouse_id: str) -> List[Dict]:
        """Find the optimal set of orders for an agent using greedy approach"""
        best_orders = []
        best_score = -1
        
        # Try different order counts to find optimal allocation
        max_orders_to_try = min(len(available_orders), 60)  # Max 60 orders per agent
        
        for target_orders in range(30, 4, -1):  # Try 30, 29, 28, ..., 5 orders
            if target_orders > len(available_orders):
                continue
            
            # Select closest orders to warehouse (simple heuristic)
            warehouse = db.warehouses.find_one({'_id': warehouse_id})
            if not warehouse:
                continue
            
            warehouse_coords = (warehouse['latitude'], warehouse['longitude'])
            
            # Sort orders by distance from warehouse
            orders_with_distance = []
            for order in available_orders:
                order_coords = (order['latitude'], order['longitude'])
                distance = LocationUtils.calculate_distance(
                    warehouse_coords[0], warehouse_coords[1],
                    order_coords[0], order_coords[1]
                )
                orders_with_distance.append((order, distance))
            
            orders_with_distance.sort(key=lambda x: x[1])
            
            # Take the closest target_orders
            candidate_orders = [item[0] for item in orders_with_distance[:target_orders]]
            
            # Check if agent can handle these orders
            can_accept, metrics = AssignmentUtils.can_agent_accept_orders(
                str(agent['_id']), candidate_orders
            )
            
            if can_accept:
                # Calculate score (prioritize higher earnings and better utilization)
                score = self._calculate_allocation_score(metrics)
                
                if score > best_score:
                    best_score = score
                    best_orders = candidate_orders
        
        return best_orders
    
    def _calculate_allocation_score(self, metrics: Dict) -> float:
        """Calculate score for an allocation based on multiple factors"""
        # Prioritize higher earnings
        earning_score = metrics['total_earning'] / 100  # Normalize
        
        # Prioritize higher order count (better utilization)
        order_score = metrics['total_orders'] / 50  # Normalize to max 50 orders
        
        # Prioritize agents hitting payment tiers
        tier_bonus = 0
        if metrics['total_orders'] >= Config.TIER_2_ORDERS:
            tier_bonus = 10
        elif metrics['total_orders'] >= Config.TIER_1_ORDERS:
            tier_bonus = 5
        
        # Penalize excessive distance (efficiency)
        distance_penalty = metrics['total_distance'] / Config.MAX_TRAVEL_DISTANCE_PER_DAY
        
        total_score = earning_score + order_score + tier_bonus - distance_penalty
        return total_score

# Global instance
allocation_engine = OrderAllocationEngine()
