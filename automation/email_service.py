import smtplib
import os
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart
from datetime import datetime

class EmailService:
    def __init__(self):
        # In production, use environment variables
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        self.email = os.getenv('EMAIL_ADDRESS', 'noreply@ndis.com')
        self.password = os.getenv('EMAIL_PASSWORD', 'your-app-password')
    
    def send_welcome_email(self, to_email, staff_name, staff_id):
        """Send welcome email to new staff"""
        subject = "Welcome to NDIS Platform!"
        
        body = f"""
        Dear {staff_name},
        
        Welcome to our NDIS platform! We're excited to have you join our team.
        
        Your account details:
        - Staff ID: {staff_id}
        - Login Email: {to_email}
        
        Next steps:
        1. Complete your profile information
        2. Upload required documents (ID, qualifications, WWCC)
        3. Complete NDIS worker screening
        4. Attend orientation session
        
        If you have any questions, please contact your supervisor.
        
        Best regards,
        NDIS Platform Team
        
        ---
        This is an automated message. Please do not reply.
        """
        
        return self._send_email(to_email, subject, body)
    
    def send_reminder_email(self, to_email, reminder_type, details):
        """Send reminder emails"""
        subjects = {
            'document_upload': 'Document Upload Reminder',
            'orientation': 'Orientation Session Reminder',
            'compliance': 'Compliance Renewal Reminder'
        }
        
        subject = subjects.get(reminder_type, 'NDIS Platform Reminder')
        
        body = f"""
        Hello,
        
        This is a friendly reminder regarding: {reminder_type.replace('_', ' ').title()}
        
        Details: {details}
        
        Please take action as soon as possible to ensure compliance.
        
        Best regards,
        NDIS Platform Team
        """
        
        return self._send_email(to_email, subject, body)
    
    def _send_email(self, to_email, subject, body):
        """Internal method to send email"""
        try:
            # For demo purposes, just print the email
            print(f"\n📧 EMAIL SENT")
            print(f"To: {to_email}")
            print(f"Subject: {subject}")
            print(f"Body: {body}")
            print(f"Sent at: {datetime.now()}")
            print("=" * 50)
            
            # In production, uncomment this:
            # msg = MimeMultipart()
            # msg['From'] = self.email
            # msg['To'] = to_email
            # msg['Subject'] = subject
            # msg.attach(MimeText(body, 'plain'))
            # 
            # server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            # server.starttls()
            # server.login(self.email, self.password)
            # server.send_message(msg)
            # server.quit()
            
            return True
        except Exception as e:
            print(f"❌ Email sending failed: {str(e)}")
            return False