import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from flask import current_app
import sys

def send_email(to_email, subject, html_content):
    """Send email using SendGrid with detailed logging."""
    sendgrid_api_key = os.environ.get('SENDGRID_API_KEY')
    
    print("\n" + "="*60)
    print(f"📧 EMAIL DEBUG INFO")
    print("="*60)
    print(f"To: {to_email}")
    print(f"Subject: {subject}")
    print(f"From: {os.environ.get('SENDGRID_FROM_EMAIL', 'Not set')}")
    print(f"API Key present: {'✅ Yes' if sendgrid_api_key else '❌ No'}")
    
    if not sendgrid_api_key:
        print("❌ ERROR: SENDGRID_API_KEY environment variable is not set!")
        print("   To fix: Add your SendGrid API key to .env file or Render environment variables")
        print("   Get your key from: https://app.sendgrid.com/settings/api_keys")
        print("="*60 + "\n")
        return False
    
    # Check if API key format is valid (should start with SG.)
    if not sendgrid_api_key.startswith('SG.'):
        print("⚠️ WARNING: SendGrid API key format looks incorrect")
        print(f"   Key starts with: {sendgrid_api_key[:10]}...")
        print("   It should start with 'SG.'")
    
    # Verify sender email is verified in SendGrid
    from_email = os.environ.get('SENDGRID_FROM_EMAIL', 'noreply@example.com')
    print(f"From email: {from_email}")
    print("\n📋 IMPORTANT: This email MUST be verified in SendGrid")
    print("   Verify at: https://app.sendgrid.com/settings/sender_auth")
    
    message = Mail(
        from_email=from_email,
        to_emails=to_email,
        subject=subject,
        html_content=html_content
    )
    
    try:
        print("\n📤 Attempting to send email via SendGrid...")
        sg = SendGridAPIClient(sendgrid_api_key)
        response = sg.send(message)
        
        print(f"✅ SendGrid Response Status: {response.status_code}")
        print(f"📋 Response Headers: {dict(response.headers)}")
        
        if response.status_code == 202:
            print("✅ Email accepted by SendGrid (status 202)")
            print("⚠️ Note: Status 202 means 'accepted', not 'delivered'")
            print("   The email may be delayed or deferred")
            print("   Check SendGrid dashboard for delivery status")
            print("="*60 + "\n")
            return True
        else:
            print(f"❌ Unexpected status code: {response.status_code}")
            print("="*60 + "\n")
            return False
            
    except Exception as e:
        print(f"\n❌ ERROR sending email: {str(e)}")
        print("\n🔍 Common causes:")
        print("   1. Unverified sender email - Verify at SendGrid")
        print("   2. Invalid API key - Regenerate a new one")
        print("   3. SendGrid account issues - Check dashboard")
        print("   4. Network connectivity problems")
        print("\n📊 Check SendGrid dashboard for details:")
        print("   https://app.sendgrid.com/email_activity")
        print("="*60 + "\n")
        return False

def send_invitation_email(email, username, temporary_password):
    """Send invitation email to new user."""
    app_name = os.environ.get('APP_NAME', 'すみれ＆みあ')
    app_url = os.environ.get('APP_URL', 'https://sumire-mia-app.vercel.app/')
    login_url = f"{app_url}/auth/login"
    
    print(f"\n📨 Preparing invitation email for {username} ({email})")
    
    subject = f"Welcome to {app_name}!"
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{ font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif; line-height: 1.6; color: #4a4a4a; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: linear-gradient(135deg, #e6e6fa, #ffdab9); padding: 30px; text-align: center; border-radius: 24px 24px 0 0; }}
            .content {{ background: #faf7f2; padding: 30px; border-radius: 0 0 24px 24px; }}
            .button {{ display: inline-block; padding: 12px 30px; background: #e6e6fa; color: #4a4a4a; text-decoration: none; border-radius: 30px; margin: 20px 0; font-weight: 500; }}
            .credentials {{ background: white; padding: 20px; border-radius: 16px; margin: 20px 0; border-left: 4px solid #e6e6fa; }}
            .footer {{ text-align: center; margin-top: 30px; color: #8b8b8b; font-size: 0.9em; }}
            code {{ background: #e6e6fa; padding: 4px 8px; border-radius: 8px; font-family: monospace; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1 style="color: #4a4a4a; margin:0;">✨ {app_name} ✨</h1>
            </div>
            <div class="content">
                <h2 style="margin-top:0;">welcome, {username}!</h2>
                <p>you've been invited to join {app_name} – your personal calendar and task manager.</p>
                
                <div class="credentials">
                    <h3 style="margin-top: 0; color: #4a4a4a;">your login credentials:</h3>
                    <p><strong>username:</strong> {username}</p>
                    <p><strong>temporary password:</strong> <code>{temporary_password}</code></p>
                </div>
                
                <div style="text-align: center;">
                    <a href="{login_url}" class="button">login to your account</a>
                </div>
                
                <p style="margin-top: 20px;"><strong>important:</strong> please change your password after logging in for security.</p>
            </div>
            <div class="footer">
                <p>© 2024 {app_name}. all rights reserved.</p>
                <p style="font-size: 0.8em;">this is an automated message, please do not reply.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return send_email(email, subject, html_content)

def send_password_reset_email(email, username, temporary_password):
    """Send password reset email."""
    app_name = os.environ.get('APP_NAME', 'すみれ＆みあ')
    app_url = os.environ.get('APP_URL', 'https://sumire-mia-app.vercel.app/')
    login_url = f"{app_url}/auth/login"
    
    print(f"\n🔐 Preparing password reset email for {username} ({email})")
    
    subject = f"🔐 Password Reset - {app_name}"
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{ font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif; line-height: 1.6; color: #4a4a4a; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: linear-gradient(135deg, #e6e6fa, #ffdab9); padding: 30px; text-align: center; border-radius: 24px 24px 0 0; }}
            .content {{ background: #faf7f2; padding: 30px; border-radius: 0 0 24px 24px; }}
            .button {{ display: inline-block; padding: 12px 30px; background: #e6e6fa; color: #4a4a4a; text-decoration: none; border-radius: 30px; margin: 20px 0; font-weight: 500; }}
            .credentials {{ background: white; padding: 20px; border-radius: 16px; margin: 20px 0; border-left: 4px solid #e6e6fa; }}
            .footer {{ text-align: center; margin-top: 30px; color: #8b8b8b; font-size: 0.9em; }}
            code {{ background: #e6e6fa; padding: 8px 16px; border-radius: 8px; font-family: monospace; font-size: 1.2em; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1 style="color: #4a4a4a; margin:0;">🔐 password reset</h1>
            </div>
            <div class="content">
                <h2 style="margin-top:0;">hello {username},</h2>
                <p>your password has been reset by an administrator.</p>
                
                <div class="credentials">
                    <h3 style="margin-top: 0; color: #4a4a4a;">your new temporary password:</h3>
                    <p style="text-align: center;"><code>{temporary_password}</code></p>
                </div>
                
                <div style="text-align: center;">
                    <a href="{login_url}" class="button">login with new password</a>
                </div>
                
                <p style="margin-top: 20px;"><strong>important:</strong> please change your password after logging in for security.</p>
                
                <p>if you didn't request this change, please contact your administrator immediately.</p>
            </div>
            <div class="footer">
                <p>© 2024 {app_name}. all rights reserved.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return send_email(email, subject, html_content)