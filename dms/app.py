from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
from datetime import date, datetime
from models import Warehouse, Agent, Order, Assignment
from allocation_engine import allocation_engine
from scheduler import scheduler
from seed_data import SeedDataGenerator
from utils import AssignmentUtils
from database import db
from bson import ObjectId
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    """Home dashboard page"""
    return render_template('dashboard.html')

@app.route('/dashboard')
def dashboard():
    """Dashboard page (alternative route)"""
    return render_template('dashboard.html')

@app.route('/agents')
def agents_page():
    """Agents management page"""
    return render_template('agents.html')

@app.route('/orders')
def orders_page():
    """Orders management page"""
    return render_template('orders.html')

@app.route('/warehouses')
def warehouses_page():
    """Warehouses management page"""
    return render_template('warehouses.html')

@app.route('/api')
def api_info():
    """API information endpoint"""
    return jsonify({
        'message': 'Delivery Management System API',
        'version': '1.0.0',
        'endpoints': {
            'GET /': 'Dashboard UI',
            'GET /api': 'API information',
            'GET /warehouses': 'List all warehouses',
            'GET /agents': 'List all agents',
            'GET /orders': 'List all orders',
            'POST /seed-data': 'Generate seed data',
            'POST /check-in/<agent_id>': 'Check in agent',
            'POST /run-allocation': 'Run order allocation manually',
            'GET /assignments/<date>': 'Get assignments for date',
            'GET /summary/<date>': 'Get daily summary',
            'GET /health': 'Health check'
        }
    })

@app.route('/api/warehouses')
def get_warehouses():
    """Get all warehouses (API endpoint)"""
    try:
        warehouses = Warehouse.get_all()
        # Convert ObjectId to string
        for warehouse in warehouses:
            warehouse['_id'] = str(warehouse['_id'])
        return jsonify({'warehouses': warehouses})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/agents')
def get_agents():
    """Get all agents (API endpoint)"""
    try:
        agents = Agent.get_all()
        # Convert ObjectId to string
        for agent in agents:
            agent['_id'] = str(agent['_id'])
            agent['warehouse_id'] = str(agent['warehouse_id'])
        return jsonify({'agents': agents})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/orders')
def get_orders():
    """Get all orders (API endpoint)"""
    try:
        orders = Order.get_pending_orders()
        # Convert ObjectId to string
        for order in orders:
            order['_id'] = str(order['_id'])
            order['warehouse_id'] = str(order['warehouse_id'])
            if order.get('assigned_agent_id'):
                order['assigned_agent_id'] = str(order['assigned_agent_id'])
        return jsonify({'orders': orders})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/seed-data', methods=['POST'])
def generate_seed_data():
    """Generate seed data for testing"""
    try:
        generator = SeedDataGenerator()
        summary = generator.generate_complete_dataset()
        return jsonify({
            'message': 'Seed data generated successfully',
            'summary': summary
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/check-in/<agent_id>', methods=['POST'])
def check_in_agent(agent_id):
    """Check in an agent"""
    try:
        result = Agent.check_in(agent_id)
        if result.modified_count > 0:
            return jsonify({'message': f'Agent {agent_id} checked in successfully'})
        else:
            return jsonify({'error': 'Agent not found or already checked in'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/run-allocation', methods=['POST'])
def run_allocation():
    """Manually trigger order allocation"""
    try:
        result = allocation_engine.run_allocation()
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/assignments/<date_str>')
def get_assignments(date_str):
    """Get assignments for a specific date (API endpoint)"""
    try:
        assignment_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        assignments = Assignment.get_by_date(assignment_date)
        
        # Convert ObjectId to string and enrich data
        for assignment in assignments:
            assignment['_id'] = str(assignment['_id'])
            assignment['agent_id'] = str(assignment['agent_id'])
            
            # Get agent details
            agent = db.agents.find_one({'_id': ObjectId(assignment['agent_id'])})
            if agent:
                assignment['agent_name'] = agent['name']
            
            # Get order details
            order_details = []
            for order_id in assignment['order_ids']:
                order = db.orders.find_one({'_id': ObjectId(order_id)})
                if order:
                    order_details.append({
                        'order_id': order['order_id'],
                        'customer_name': order['customer_name'],
                        'delivery_address': order['delivery_address']
                    })
            assignment['order_details'] = order_details
        
        return jsonify({'assignments': assignments})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/summary/<date_str>')
def get_summary(date_str):
    """Get daily summary (API endpoint)"""
    try:
        summary = AssignmentUtils.generate_daily_summary(date_str)
        return jsonify(summary)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/health')
def health_check():
    """Health check endpoint (API endpoint)"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'scheduler_running': scheduler.scheduler.running
    })

if __name__ == '__main__':
    # Start the scheduler
    scheduler.start()
    
    # Run the Flask app
    app.run(debug=True, host='0.0.0.0', port=5000)
