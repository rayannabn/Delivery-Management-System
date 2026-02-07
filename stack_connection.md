# Delivery Management System - How It Works

## 🎯 Overview

The Delivery Management System is designed to automatically allocate delivery orders to agents while respecting time, distance, and profitability constraints. It simulates a real-world logistics operation similar to Amazon, Bluedart, or Delhivery.

## 🏗 System Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Web UI        │    │  Flask API       │    │   MongoDB       │
│   (Browser)     │◄──►│   (Backend)      │◄──►│   Database      │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       │
         │              ┌──────────────────┐            │
         └──────────────►│  Allocation      │◄───────────┘
                        │  Engine          │
                        └──────────────────┘
                                 │
                        ┌──────────────────┐
                        │  Background      │
                        │  Scheduler       │
                        └──────────────────┘
```

## 📊 Core Components

### 1. **Database Models** (`models.py`)

#### **Warehouse**
- **Purpose**: Represents distribution hubs across the city
- **Fields**: Name, coordinates (lat/lng), city
- **Role**: Starting point for all delivery routes

#### **Agent**
- **Purpose**: Delivery partners who work each day
- **Fields**: Name, warehouse assignment, phone, check-in status
- **Role**: Executes deliveries within constraints

#### **Order**
- **Purpose**: Customer delivery requests
- **Fields**: Order ID, customer details, delivery address, coordinates, warehouse
- **Role**: Units that need to be allocated to agents

#### **Assignment**
- **Purpose**: Daily allocation records
- **Fields**: Agent ID, order IDs, distance, time, earnings
- **Role**: Tracks what each agent delivers each day

### 2. **Allocation Engine** (`allocation_engine.py`)

This is the **brain** of the system. Here's how it works:

#### **Step 1: Data Collection**
```python
# Get all checked-in agents
checked_in_agents = Agent.get_checked_in_agents()

# Group agents by warehouse
warehouse_agents = {}
for agent in checked_in_agents:
    warehouse_id = agent['warehouse_id']
    warehouse_agents[warehouse_id].append(agent)
```

#### **Step 2: Order Processing**
```python
# Get pending orders for each warehouse
pending_orders = Order.get_by_warehouse(warehouse_id)
```

#### **Step 3: Intelligent Allocation**
For each agent, the system:

1. **Finds Optimal Order Set**: Uses distance-based heuristics to select orders
2. **Checks Constraints**: Validates against time, distance, and earning limits
3. **Calculates Route**: Optimizes delivery sequence using nearest-neighbor algorithm
4. **Assigns Orders**: Creates assignment record and updates order status

#### **Allocation Algorithm Logic**

```python
def _find_optimal_order_set(self, agent, available_orders, warehouse_id):
    # 1. Sort orders by distance from warehouse (closest first)
    orders_with_distance = []
    for order in available_orders:
        distance = calculate_distance(warehouse, order_location)
        orders_with_distance.append((order, distance))
    orders_with_distance.sort(key=lambda x: x[1])
    
    # 2. Try different order counts (50, 45, 40, etc.)
    for target_orders in range(50, 0, -5):
        candidate_orders = orders_with_distance[:target_orders]
        
        # 3. Check if agent can handle these orders
        can_accept, metrics = check_constraints(agent, candidate_orders)
        
        if can_accept:
            # 4. Calculate score (prioritize higher earnings)
            score = calculate_allocation_score(metrics)
            if score > best_score:
                best_orders = candidate_orders
    
    return best_orders
```

### 3. **Constraint Checking** (`utils.py`)

The system enforces these business rules:

#### **Time Constraint**
```python
# 1 km = 5 minutes travel time
travel_time = distance_km * 5 minutes
total_time = travel_time / 60  # convert to hours

if total_time > MAX_WORKING_HOURS_PER_DAY:  # 10 hours
    return False, "Time limit exceeded"
```

#### **Distance Constraint**
```python
if total_distance > MAX_TRAVEL_DISTANCE_PER_DAY:  # 100 km
    return False, "Distance limit exceeded"
```

#### **Earning Constraint**
```python
# Calculate payment based on order volume
if total_orders >= 50:
    earning_per_order = 42  # ₹42 per order
elif total_orders >= 25:
    earning_per_order = 35  # ₹35 per order
else:
    earning_per_order = 30  # ₹30 per order

total_earning = total_orders * earning_per_order

if total_earning < MIN_DAILY_EARNING:  # ₹500
    return False, "Earning below minimum"
```

### 4. **Route Optimization** (`utils.py`)

```python
def optimize_route(warehouse_coords, delivery_coords):
    """Simple nearest neighbor algorithm"""
    route = [warehouse_coords]
    remaining_deliveries = delivery_coords.copy()
    current_location = warehouse_coords
    
    while remaining_deliveries:
        # Find closest unvisited location
        nearest_point = min(remaining_deliveries, 
                          key=lambda point: calculate_distance(current_location, point))
        route.append(nearest_point)
        remaining_deliveries.remove(nearest_point)
        current_location = nearest_point
    
    return route
```

### 5. **Background Scheduler** (`scheduler.py`)

```python
# Runs automatically every day at 7:00 AM
scheduler.add_job(
    func=run_daily_allocation,
    trigger=CronTrigger(hour=7, minute=0),
    id='daily_allocation'
)

# Auto checkout at 8:00 PM
scheduler.add_job(
    func=check_out_all_agents,
    trigger=CronTrigger(hour=20, minute=0),
    id='daily_checkout'
)
```

## 🔄 Daily Workflow

### **Morning (7:00 AM)**
1. **Scheduler triggers allocation**
2. **System finds all checked-in agents**
3. **Groups agents by warehouse**
4. **Allocates orders using algorithm**
5. **Updates order statuses to 'assigned'**
6. **Creates assignment records**

### **During Day**
1. **Agents check in at warehouses**
2. **Receive their assigned orders**
3. **Follow optimized delivery routes**
4. **Complete deliveries within constraints**

### **Evening (8:00 PM)**
1. **Scheduler auto-checks out all agents**
2. **System prepares for next day**
3. **Deferred orders carry over**

## 🎯 Key Features

### **1. Intelligent Allocation**
- **Distance-based**: Prioritizes orders closest to warehouse
- **Constraint-aware**: Respects time, distance, earning limits
- **Profitability-focused**: Maximizes agent earnings through tiered payments

### **2. Real-time Monitoring**
- **Dashboard**: Live metrics and statistics
- **Agent Management**: Check-in/check-out functionality
- **Order Tracking**: Status updates and assignment details

### **3. Scalability**
- **Handles**: 10 warehouses, 200 agents, 12,000 orders daily
- **Performance**: Allocation completes in <30 seconds
- **Database**: MongoDB for efficient data storage

## 📱 Web Interface

### **Dashboard** (`/`)
- **Daily Summary**: Orders, agents, distance, cost
- **Recent Assignments**: Agent performance details
- **System Status**: Health and scheduler status
- **Actions**: Run allocation, generate test data

### **Agents Page** (`/agents`)
- **Agent List**: All agents with check-in status
- **Statistics**: Total, checked-in, checked-out counts
- **Actions**: Individual or bulk check-in

### **Orders Page** (`/orders`)
- **Pending Orders**: Customer delivery requests
- **Warehouse Distribution**: Orders per warehouse
- **Allocation Trigger**: Run allocation process

### **Warehouses Page** (`/warehouses`)
- **Warehouse List**: All distribution centers
- **Location Details**: Coordinates and city information
- **Coverage Map**: Visual representation

## 🧪 Testing & Data Generation

### **Seed Data** (`seed_data.py`)
```python
# Generates realistic test data:
- 10 warehouses across Bangalore
- 20 agents per warehouse (200 total)
- ~10,000 orders per day
- 80% agent check-in rate
```

### **Test Script** (`test_allocation.py`)
```python
# Complete system test:
1. Generate test data
2. Run allocation
3. Display results
4. Clean up database
```

## 🔧 API Endpoints

### **Data Management**
- `GET /warehouses` - List all warehouses
- `GET /agents` - List all agents
- `GET /orders` - List pending orders

### **Operations**
- `POST /seed-data` - Generate test data
- `POST /check-in/<agent_id>` - Check in agent
- `POST /run-allocation` - Manual allocation trigger

### **Reporting**
- `GET /summary/<date>` - Daily metrics
- `GET /assignments/<date>` - Assignment details
- `GET /health` - System status

## 📊 Business Logic Examples

### **Example 1: Agent Allocation**
```
Agent: Rahul Kumar
Warehouse: Whitefield
Available Orders: 45 nearby orders

Allocation Process:
1. System selects 45 closest orders
2. Calculates route: 85 km total distance
3. Travel time: 85 km × 5 min = 425 min = 7.1 hours
4. Earnings: 45 orders × ₹35 = ₹1,575
5. Check: Time < 10h ✓, Distance < 100km ✓, Earnings > ₹500 ✓
6. Result: Orders assigned to Rahul
```

### **Example 2: Constraint Violation**
```
Agent: Amit Sharma
Available Orders: 60 distant orders

Allocation Process:
1. System selects 60 orders
2. Calculates route: 120 km total distance
3. Check: Distance > 100km ✗
4. Result: Try smaller order set (55, 50, 45...)
5. Final: 50 orders assigned (95 km, 7.9 hours, ₹2,100)
```

## 🎯 Success Metrics

The system optimizes for:
- **High Agent Utilization**: Max orders per agent within constraints
- **Cost Efficiency**: Minimize total distance traveled
- **Profitability**: Help agents reach higher payment tiers
- **Fair Distribution**: Balance workload across agents

## 🚀 Why This Design?

1. **Simplicity**: Uses proven algorithms (nearest neighbor)
2. **Scalability**: MongoDB handles large datasets efficiently
3. **Maintainability**: Clean separation of concerns
4. **Extensibility**: Easy to add new features (real-time tracking, etc.)
5. **Reliability**: Background scheduler ensures daily operations

This system demonstrates practical application of:
- **Route Optimization Algorithms**
- **Constraint Satisfaction Problems**
- **Database Design**
- **API Development**
- **Background Processing**
- **Web UI Development**

It's a simplified but realistic simulation of actual logistics systems used by major delivery companies.
