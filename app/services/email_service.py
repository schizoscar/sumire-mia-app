import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from flask import current_app

def send_email(to_email, subject, html_content):
    """Send email using SendGrid."""
    sendgrid_api_key = os.environ.get('SENDGRID_API_KEY')
    
    if not sendgrid_api_key:
        print("Warning: SENDGRID_API_KEY not set. Email not sent.")
        return False
    
    message = Mail(
        from_email=os.environ.get('SENDGRID_FROM_EMAIL', 'noreply@example.com'),
        to_emails=to_email,
        subject=subject,
        html_content=html_content
    )
    
    try:
        sg = SendGridAPIClient(sendgrid_api_key)
        response = sg.send(message)
        return response.status_code == 202
    except Exception as e:
        print(f"Error sending email: {e}")
        return False

def send_invitation_email(email, username, temporary_password):
    """Send invitation email to new user."""
    app_name = os.environ.get('APP_NAME', 'すみれ＆みあ')
    app_url = os.environ.get('APP_URL', 'http://localhost:5000')
    
    subject = f"Welcome to {app_name}!"
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: linear-gradient(135deg, #9b59b6, #ff69b4); color: white; padding: 20px; text-align: center; border-radius: 10px 10px 0 0; }}
            .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
            .button {{ display: inline-block; padding: 12px 24px; background: #9b59b6; color: white; text-decoration: none; border-radius: 25px; margin: 20px 0; }}
            .footer {{ text-align: center; margin-top: 20px; color: #666; font-size: 0.9em; }}
            .credentials {{ background: #fff; padding: 15px; border-left: 4px solid #9b59b6; margin: 20px 0; font-family: monospace; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>✨ {app_name} ✨</h1>
                <p>Your personal calendar & task manager</p>
            </div>
            <div class="content">
                <h2>Welcome, {username}!</h2>
                <p>You've been invited to join {app_name} – your cute and modern calendar, to-do list, and reminder app!</p>
                
                <h3>Your Login Credentials:</h3>
                <div class="credentials">
                    <p><strong>Username:</strong> {username}</p>
                    <p><strong>Temporary Password:</strong> {temporary_password}</p>
                </div>
                
                <p style="text-align: center;">
                    <a href="{app_url}/auth/login" class="button">Login to Your Account</a>
                </p>
                
                <p><strong>Important:</strong> For security reasons, please change your password after logging in.</p>
                
                <p>With {app_name}, you can:</p>
                <ul>
                    <li>📅 Manage your calendar with color-coded events</li>
                    <li>✅ Keep track of your to-do lists</li>
                    <li>⏰ Set reminders that will be sent to your email</li>
                    <li>🎨 Choose between purple and pink themes</li>
                </ul>
                
                <p>We're excited to have you on board!</p>
                
                <p>Best regards,<br>The {app_name} Team</p>
            </div>
            <div class="footer">
                <p>© 2024 {app_name}. All rights reserved.</p>
                <p style="font-size: 0.8em;">This is an automated message, please do not reply.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return send_email(email, subject, html_content)

def send_reminder_email(email, username, reminder_title, reminder_message, reminder_time):
    """Send reminder notification email."""
    app_name = os.environ.get('APP_NAME', 'すみれ＆みあ')
    
    subject = f"🔔 Reminder: {reminder_title}"
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: linear-gradient(135deg, #9b59b6, #ff69b4); color: white; padding: 20px; text-align: center; border-radius: 10px 10px 0 0; }}
            .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
            .reminder-box {{ background: #fff; padding: 20px; border-radius: 10px; margin: 20px 0; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
            .footer {{ text-align: center; margin-top: 20px; color: #666; font-size: 0.9em; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🔔 Time's Up!</h1>
            </div>
            <div class="content">
                <h2>Hello {username}!</h2>
                <p>This is your reminder for:</p>
                
                <div class="reminder-box">
                    <h3 style="color: #9b59b6;">{reminder_title}</h3>
                    <p><strong>Time:</strong> {reminder_time}</p>
                    <p><strong>Message:</strong> {reminder_message}</p>
                </div>
                
                <p style="text-align: center;">
                    <a href="{os.environ.get('APP_URL', 'http://localhost:5000')}/reminders" style="display: inline-block; padding: 10px 20px; background: #9b59b6; color: white; text-decoration: none; border-radius: 25px;">
                        View All Reminders
                    </a>
                </p>
            </div>
            <div class="footer">
                <p>© 2024 {app_name}. All rights reserved.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return send_email(email, subject, html_content)