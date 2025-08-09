import schedule
import time
from datetime import datetime, timedelta
from email_service import EmailService
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

class NotificationWorkflows:
    def __init__(self):
        self.email_service = EmailService()
        self.db_url = os.getenv('DATABASE_URL')
    
    def get_db_connection(self):
        """Get database connection"""
        return psycopg2.connect(self.db_url)
    
    def send_daily_reminders(self):
        """Send daily reminder emails"""
        print(f"🔄 Running daily reminders at {datetime.now()}")
        
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()
            
            # Get staff who joined 3 days ago but haven't completed profile
            cursor.execute("""
                SELECT s.id, s.first_name, s.last_name, u.email, s.hire_date
                FROM staff s
                JOIN users u ON s.user_id = u.id
                WHERE s.hire_date >= %s
                AND s.hire_date <= %s
                AND s.status = 'active'
            """, (
                datetime.now() - timedelta(days=4),
                datetime.now() - timedelta(days=3)
            ))
            
            staff_for_reminders = cursor.fetchall()
            
            for staff in staff_for_reminders:
                staff_id, first_name, last_name, email, hire_date = staff
                
                self.email_service.send_reminder_email(
                    email,
                    'document_upload',
                    f"Please complete your profile and upload required documents. Hired on: {hire_date.strftime('%Y-%m-%d')}"
                )
                
                # Log automation activity
                cursor.execute("""
                    INSERT INTO automation_logs (workflow_type, entity_type, entity_id, status, details)
                    VALUES (%s, %s, %s, %s, %s)
                """, (
                    'daily_reminder',
                    'staff',
                    staff_id,
                    'completed',
                    f"Sent reminder email to {email}"
                ))
            
            conn.commit()
            print(f"✅ Sent {len(staff_for_reminders)} reminder emails")
            
        except Exception as e:
            print(f"❌ Error in daily reminders: {str(e)}")
        finally:
            if conn:
                conn.close()
    
    def check_compliance_renewals(self):
        """Check for upcoming compliance renewals"""
        print(f"🔍 Checking compliance renewals at {datetime.now()}")
        
        # In a real system, this would check document expiry dates
        # For demo, we'll simulate some compliance checks
        
        simulated_renewals = [
            {'staff_id': 1, 'email': 'admin@ndis.com', 'document': 'WWCC', 'expires': '2024-12-01'},
            {'staff_id': 2, 'email': 'coordinator@ndis.com', 'document': 'First Aid', 'expires': '2024-11-15'},
        ]
        
        for renewal in simulated_renewals:
            self.email_service.send_reminder_email(
                renewal['email'],
                'compliance',
                f"{renewal['document']} expires on {renewal['expires']}. Please renew immediately."
            )
            
            print(f"📋 Compliance reminder sent for {renewal['document']} to {renewal['email']}")
    
    def start_scheduler(self):
        """Start the automation scheduler"""
        print("🚀 Starting NDIS Automation Workflows")
        
        # Schedule daily reminders at 9 AM
        schedule.every().day.at("09:00").do(self.send_daily_reminders)
        
        # Schedule compliance checks every Monday at 10 AM
        schedule.every().monday.at("10:00").do(self.check_compliance_renewals)
        
        # For demo purposes, run every minute
        schedule.every(1).minutes.do(self.send_daily_reminders)
        schedule.every(2).minutes.do(self.check_compliance_renewals)
        
        print("⏰ Scheduler configured:")
        print("  - Daily reminders: Every day at 9:00 AM")
        print("  - Compliance checks: Every Monday at 10:00 AM")
        print("  - Demo mode: Running every 1-2 minutes")
        
        while True:
            schedule.run_pending()
            time.sleep(30)  # Check every 30 seconds

if __name__ == "__main__":
    workflows = NotificationWorkflows()
    workflows.start_scheduler()