import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv

load_dotenv()

# Email configuration
sender_email = os.getenv("GMAIL_ADDRESS")

password = os.getenv("GMAIL_PASSWORD")  # Use an app-specific password for Gmail

webclient_base_url = os.getenv("WEBCLIENT_BASE_URL") or "http://localhost:5173"

def send_email(receiver_email, subject, body):
    # Construct the message
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = subject
    message.attach(MIMEText(body, "plain"))

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()  # Upgrade connection to secure
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, message.as_string())
            print("Email sent successfully!")
    except Exception as e:
        print(f"Error: {e}")

def send_verification_email(receiver_email, verification_code):
    subject = "Verification Code"
    body = f"Your verification code is: {webclient_base_url}/verify/{verification_code}"
    send_email(receiver_email, subject, body)