from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime, time
from allocation_engine import allocation_engine
from models import Agent
import logging

logger = logging.getLogger(__name__)

class DeliveryScheduler:
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.setup_jobs()
    
    def setup_jobs(self):
        """Setup scheduled jobs"""
        # Run allocation every day at 7:00 AM
        self.scheduler.add_job(
            func=self.run_daily_allocation,
            trigger=CronTrigger(hour=7, minute=0),
            id='daily_allocation',
            name='Daily Order Allocation',
            replace_existing=True
        )
        
        # Check out all agents at 8:00 PM
        self.scheduler.add_job(
            func=self.check_out_all_agents,
            trigger=CronTrigger(hour=20, minute=0),
            id='daily_checkout',
            name='Daily Agent Checkout',
            replace_existing=True
        )
    
    def run_daily_allocation(self):
        """Run the daily order allocation"""
        try:
            logger.info("Starting scheduled daily allocation")
            result = allocation_engine.run_allocation()
            
            if result['status'] == 'success':
                logger.info(f"Daily allocation completed successfully: {result}")
            else:
                logger.error(f"Daily allocation failed: {result}")
                
        except Exception as e:
            logger.error(f"Error in daily allocation: {str(e)}")
    
    def check_out_all_agents(self):
        """Check out all agents at end of day"""
        try:
            logger.info("Checking out all agents")
            Agent.check_out_all()
            logger.info("All agents checked out successfully")
        except Exception as e:
            logger.error(f"Error checking out agents: {str(e)}")
    
    def start(self):
        """Start the scheduler"""
        try:
            self.scheduler.start()
            logger.info("Delivery scheduler started successfully")
        except Exception as e:
            logger.error(f"Error starting scheduler: {str(e)}")
    
    def stop(self):
        """Stop the scheduler"""
        try:
            self.scheduler.shutdown()
            logger.info("Delivery scheduler stopped")
        except Exception as e:
            logger.error(f"Error stopping scheduler: {str(e)}")
    
    def run_allocation_now(self):
        """Manually trigger allocation for testing"""
        return self.run_daily_allocation()

# Global scheduler instance
scheduler = DeliveryScheduler()
