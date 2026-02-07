# 🚚 Delivery Management System

An intelligent order allocation system for last-mile logistics, inspired by platforms like Amazon, Bluedart, and Delhivery.

## 🎯 Overview

This system automatically allocates delivery orders to agents while respecting time, distance, and profitability constraints. It simulates a real-world logistics operation with warehouses, delivery agents, and customer orders.

## ✨ Key Features

- **🤖 Automated Order Allocation**: Intelligent algorithm assigns orders to delivery agents
- **⏱️ Constraint Compliance**: Respects time (15 hours/day) and distance (200 km/day) limits  
- **💰 Profitability Optimization**: Maximizes earnings with tiered payment structure
- **⏰ Background Processing**: Scheduled jobs for daily allocation at 7:00 AM
- **🌐 Real-time Web Dashboard**: Modern UI for monitoring and management
- **📊 REST APIs**: Complete API endpoints for integration
- **🗄️ MongoDB Integration**: Scalable NoSQL database for data persistence

## 📋 System Architecture

### Core Models
1. **Warehouses** - Distribution hubs with location data
2. **Agents** - Delivery partners who check in daily
3. **Orders** - Delivery requests with customer and location details
4. **Assignments** - Daily order allocations to agents

### Business Rules
- **Working Hours**: Max 15 hours per day
- **Travel Distance**: Max 200 km per day
- **Travel Speed**: 1 km = 3 minutes
- **Minimum Earning**: ₹50 per day per agent
- **Payment Tiers**:
  - 15+ orders/day: ₹35 per order
  - 30+ orders/day: ₹42 per order
  - <15 orders/day: ₹30 per order

## 🏗️ Technical Stack

- **Backend**: Flask (Python 3.13)
- **Database**: MongoDB 8.0
- **Background Tasks**: APScheduler
- **Location Services**: GeoPy
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
- **API**: RESTful with JSON responses

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- MongoDB 4.4+
- pip package manager

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd delivery-management-system
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables**
   ```bash
   # Edit .env file with your MongoDB connection
   MONGODB_URI=mongodb://localhost:27017/
   DB_NAME=delivery_management
   ```

4. **Start MongoDB**
   ```bash
   # Make sure MongoDB is running
   sudo systemctl start mongod
   ```

5. **Run the application**
   ```bash
   python app.py
   ```

6. **Access the web interface**
   - Open your browser and go to `http://localhost:5000`
   - Dashboard will load with system metrics

## 🎮 Using the System

### Web Interface

- **Dashboard** (`http://localhost:5000`) - Main overview with metrics and controls
- **Agents** (`http://localhost:5000/agents`) - Manage delivery agents
- **Orders** (`http://localhost:5000/orders`) - View and manage orders
- **Warehouses** (`http://localhost:5000/warehouses`) - View distribution centers

### Key Actions

1. **Generate Test Data**
   ```bash
   curl -X POST http://localhost:5000/seed-data
   ```

2. **Check-in Agents**
   - Use the Agents page to check in agents manually
   - Or use API: `curl -X POST http://localhost:5000/check-in/<agent_id>`

3. **Run Allocation**
   ```bash
   curl -X POST http://localhost:5000/run-allocation
   ```

4. **View Results**
   - Dashboard shows real-time metrics
   - Check assignments and agent performance

## 📊 API Endpoints

### Data Management
- `GET /api/warehouses` - List all warehouses
- `GET /api/agents` - List all agents
- `GET /api/orders` - List pending orders

### Operations
- `POST /seed-data` - Generate test data
- `POST /check-in/<agent_id>` - Check in agent
- `POST /run-allocation` - Manual allocation trigger

### Reporting
- `GET /api/summary/<date>` - Daily metrics (YYYY-MM-DD format)
- `GET /api/assignments/<date>` - Assignment details
- `GET /api/health` - System health check

## 🧪 Testing

### Automated Testing
```bash
# Run complete system test
python test_allocation.py

# Generate test data and test allocation
python populate_dashboard.py
```

### Manual Testing
```bash
# Generate sample data
curl -X POST http://localhost:5000/seed-data

# Check system health
curl http://localhost:5000/api/health

# View today's summary
curl http://localhost:5000/api/summary/$(date +%Y-%m-%d)
```

## 📈 System Metrics

The dashboard tracks these key metrics:

- **Total Agents Working**: Number of checked-in agents
- **Total Orders Assigned**: Orders successfully allocated
- **Total Distance Traveled**: Combined distance of all routes (km)
- **Total Cost**: Daily operational cost (₹)
- **Average Orders per Agent**: Workload distribution
- **Deferred Orders**: Orders carried over to next day

## 🎯 Allocation Algorithm

The system uses a greedy approach with constraint satisfaction:

1. **Group agents by warehouse**
2. **For each agent**:
   - Select orders by distance from warehouse (nearest first)
   - Try different order quantities (30 down to 5)
   - Check constraints (time, distance, earnings)
   - Assign feasible order set
3. **Optimize routes** using nearest-neighbor algorithm
4. **Create assignments** and update order status

### Constraint Checking

```python
# Time constraint
travel_time = (distance_km * 3) / 60  # hours
if travel_time > 15: return False

# Distance constraint  
if distance_km > 200: return False

# Earning constraint
if total_earning < 50: return False
```

## 🗂️ Project Structure

```
delivery-management-system/
├── app.py                 # Flask application and API routes
├── config.py              # Configuration settings
├── database.py            # MongoDB connection and collections
├── models.py              # Data models (Warehouse, Agent, Order, Assignment)
├── allocation_engine.py   # Core allocation algorithm
├── scheduler.py           # Background job scheduler
├── utils.py               # Utility functions (distance, constraints)
├── seed_data.py           # Test data generation
├── templates/             # HTML templates
│   ├── base.html          # Base template with styling
│   ├── dashboard.html     # Main dashboard
│   ├── agents.html        # Agent management
│   ├── orders.html        # Order management
│   └── warehouses.html    # Warehouse view
├── requirements.txt       # Python dependencies
├── .env                   # Environment variables
└── README.md             # This file
```

## 🔧 Configuration

Key settings in `config.py`:

```python
# Business constraints
MAX_WORKING_HOURS_PER_DAY = 15    # hours
MAX_TRAVEL_DISTANCE_PER_DAY = 200 # km  
MINUTES_PER_KM = 3                # travel time per km

# Payment tiers
MIN_DAILY_EARNING = 50            # rupees
TIER_1_ORDERS = 15                # orders per day
TIER_1_PAYMENT = 35               # rupees per order
TIER_2_ORDERS = 30                # orders per day
TIER_2_PAYMENT = 42               # rupees per order
DEFAULT_PAYMENT = 30              # rupees per order
```

## 📅 Daily Workflow

### Morning (7:00 AM)
1. **Scheduler triggers allocation automatically**
2. **System finds all checked-in agents**
3. **Groups agents by warehouse**
4. **Allocates orders using intelligent algorithm**
5. **Updates order statuses to 'assigned'**
6. **Creates assignment records**

### During Day
1. **Agents check in at warehouses**
2. **Receive assigned orders via dashboard**
3. **Follow optimized delivery routes**
4. **Complete deliveries within constraints**

### Evening (8:00 PM)
1. **Scheduler auto-checks out all agents**
2. **System prepares for next day's operations**
3. **Deferred orders carry over automatically**

## 🎨 Web Interface Features

### Dashboard
- **Real-time metrics** with auto-refresh every 30 seconds
- **System health monitoring**
- **Quick actions** (run allocation, generate data)
- **Recent assignments** with performance details

### Agent Management
- **Agent list** with check-in status
- **Bulk check-in** functionality
- **Performance statistics**
- **Warehouse assignment tracking**

### Order Tracking
- **Pending orders** with customer details
- **Warehouse distribution** analytics
- **Real-time status updates**
- **Allocation triggering**

### Warehouse Overview
- **Location details** with coordinates
- **Coverage visualization**
- **Order distribution** by warehouse
- **Geographic clustering** information

## 🚨 Troubleshooting

### Common Issues

1. **"Unexpected token '<', "<!DOCTYPE "... is not valid JSON"**
   - **Cause**: API endpoints returning HTML instead of JSON
   - **Fix**: Ensure all API calls use `/api/` prefix

2. **"No agents checked in"**
   - **Cause**: Agents need to be manually checked in before allocation
   - **Fix**: Use Agents page or API to check in agents

3. **"All orders deferred"**
   - **Cause**: Constraints too strict for order distribution
   - **Fix**: Adjust constraints in `config.py` or generate clustered data

4. **MongoDB connection errors**
   - **Cause**: MongoDB not running or wrong connection string
   - **Fix**: Start MongoDB and check `.env` configuration

### Debug Commands

```bash
# Check MongoDB connection
python -c "from database import db; print('Connected:', db.db.name)"

# Verify data generation
python seed_data.py

# Test allocation manually
python test_allocation.py

# Check system health
curl http://localhost:5000/api/health
```

## 📊 Performance Characteristics

- **Scalability**: Handles 10 warehouses, 200 agents, 12,000 orders daily
- **Allocation Time**: Completes daily allocation in <30 seconds
- **Memory Usage**: Efficient MongoDB queries with proper indexing
- **Concurrent Users**: Supports multiple dashboard users simultaneously
- **Auto-refresh**: Dashboard updates every 30 seconds

## 🎯 Business Logic Examples

### Example 1: Successful Assignment
```
Agent: Rahul Kumar
Warehouse: Whitefield
Orders: 15 nearby deliveries
Route: 116.1 km total distance
Time: 5.8 hours (116.1 km × 3 min/km)
Earnings: ₹525 (15 × ₹35)
Status: ✅ All constraints satisfied
```

### Example 2: Constraint Violation
```
Agent: Amit Sharma  
Orders: 25 distant deliveries
Route: 220 km total distance
Check: Distance > 200km ✗
Result: Orders deferred, try smaller set
```

## 🔮 Future Enhancements

- **Real-time GPS tracking** integration
- **Mobile app** for delivery agents
- **Advanced route optimization** (Google Maps API)
- **Machine learning** for demand prediction
- **Multi-city support** with geographic clustering
- **Payment integration** with digital wallets
- **Customer notifications** via SMS/Email
- **Performance analytics** and reporting dashboard

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is for evaluation purposes only.

## 📞 Support

For technical questions or issues:
- Check the troubleshooting section above
- Review the API documentation
- Examine the logs in the terminal output

---

## 🎉 Quick Demo

Ready to see it in action?

```bash
# 1. Start the system
python app.py

# 2. Generate test data
curl -X POST http://localhost:5000/seed-data

# 3. Check in some agents
# (Use the web interface at http://localhost:5000/agents)

# 4. Run allocation
curl -X POST http://localhost:5000/run-allocation

# 5. View results
# Open http://localhost:5000 in your browser
```

**Experience the complete delivery management system with intelligent allocation, real-time monitoring, and comprehensive analytics!** 🚚✨
