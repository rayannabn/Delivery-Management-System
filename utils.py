from datetime import date, datetime
from typing import Tuple, List
from geopy.distance import geodesic
from config import Config
from bson import ObjectId

class LocationUtils:
    @staticmethod
    def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate distance between two coordinates in kilometers"""
        return geodesic((lat1, lon1), (lat2, lon2)).kilometers
    
    @staticmethod
    def calculate_travel_time(distance_km: float) -> float:
        """Calculate travel time in hours based on distance"""
        travel_minutes = distance_km * Config.MINUTES_PER_KM
        return travel_minutes / 60  # convert to hours
    
    @staticmethod
    def calculate_route_distance(waypoints: List[Tuple[float, float]]) -> float:
        """Calculate total distance for a route with multiple waypoints"""
        if len(waypoints) < 2:
            return 0
        
        total_distance = 0
        for i in range(len(waypoints) - 1):
            total_distance += LocationUtils.calculate_distance(
                waypoints[i][0], waypoints[i][1],
                waypoints[i+1][0], waypoints[i+1][1]
            )
        return total_distance
    
    @staticmethod
    def optimize_route(warehouse_coords: Tuple[float, float], 
                      delivery_coords: List[Tuple[float, float]]) -> List[Tuple[float, float]]:
        """Simple nearest neighbor route optimization"""
        if not delivery_coords:
            return [warehouse_coords]
        
        route = [warehouse_coords]
        remaining_deliveries = delivery_coords.copy()
        current_location = warehouse_coords
        
        while remaining_deliveries:
            nearest_point = min(remaining_deliveries, 
                              key=lambda point: LocationUtils.calculate_distance(
                                  current_location[0], current_location[1],
                                  point[0], point[1]
                              ))
            route.append(nearest_point)
            remaining_deliveries.remove(nearest_point)
            current_location = nearest_point
        
        return route

class AssignmentUtils:
    @staticmethod
    def can_agent_accept_orders(agent_id: str, new_orders: List[dict], 
                               current_assignment: dict = None) -> Tuple[bool, dict]:
        """Check if agent can accept new orders based on constraints"""
        from models import Assignment
        from database import db
        
        # Get agent details
        agent = db.agents.find_one({'_id': ObjectId(agent_id)})
        if not agent:
            return False, {'error': 'Agent not found'}
        
        # Get warehouse details
        warehouse = db.warehouses.find_one({'_id': ObjectId(agent['warehouse_id'])})
        if not warehouse:
            return False, {'error': 'Warehouse not found'}
        
        # Prepare route waypoints
        warehouse_coords = (warehouse['latitude'], warehouse['longitude'])
        delivery_coords = [(order['latitude'], order['longitude']) for order in new_orders]
        
        # Optimize route
        route = LocationUtils.optimize_route(warehouse_coords, delivery_coords)
        
        # Calculate distance and time
        total_distance = LocationUtils.calculate_route_distance(route)
        total_time = LocationUtils.calculate_travel_time(total_distance)
        
        # Check constraints
        if total_distance > Config.MAX_TRAVEL_DISTANCE_PER_DAY:
            return False, {'error': f'Distance {total_distance:.2f}km exceeds limit {Config.MAX_TRAVEL_DISTANCE_PER_DAY}km'}
        
        if total_time > Config.MAX_WORKING_HOURS_PER_DAY:
            return False, {'error': f'Time {total_time:.2f}h exceeds limit {Config.MAX_WORKING_HOURS_PER_DAY}h'}
        
        # Calculate earnings
        total_orders = len(new_orders)
        if total_orders >= Config.TIER_2_ORDERS:
            earning_per_order = Config.TIER_2_PAYMENT
        elif total_orders >= Config.TIER_1_ORDERS:
            earning_per_order = Config.TIER_1_PAYMENT
        else:
            earning_per_order = Config.DEFAULT_PAYMENT
        
        total_earning = total_orders * earning_per_order
        
        if total_earning < Config.MIN_DAILY_EARNING:
            return False, {'error': f'Earning ₹{total_earning} below minimum ₹{Config.MIN_DAILY_EARNING}'}
        
        return True, {
            'total_distance': total_distance,
            'total_time': total_time,
            'total_orders': total_orders,
            'earning_per_order': earning_per_order,
            'total_earning': total_earning,
            'route': route
        }
    
    @staticmethod
    def generate_daily_summary(assignment_date: str) -> dict:
        """Generate summary metrics for a given date"""
        from database import db
        
        assignments = list(db.assignments.find({'assignment_date': assignment_date}))
        
        if not assignments:
            return {
                'date': assignment_date,
                'total_agents': 0,
                'total_orders': 0,
                'total_distance': 0,
                'total_cost': 0,
                'avg_orders_per_agent': 0,
                'deferred_orders': 0
            }
        
        total_orders = sum(len(a['order_ids']) for a in assignments)
        total_distance = sum(a['total_distance'] for a in assignments)
        total_cost = sum(a['total_earning'] for a in assignments)
        
        # Count deferred orders
        deferred_count = db.orders.count_documents({'status': 'deferred'})
        
        return {
            'date': assignment_date,
            'total_agents': len(assignments),
            'total_orders': total_orders,
            'total_distance': round(total_distance, 2),
            'total_cost': total_cost,
            'avg_orders_per_agent': round(total_orders / len(assignments), 2),
            'deferred_orders': deferred_count
        }
