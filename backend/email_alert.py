import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
import os

def send_security_alert_email(subject, text_message, attachment_path=None):
    """Establishes safe SMTP handshake tunnel to relay critical security alerts."""
    # ⚠️ REPLACEMENT REQUIRED: Put your Gmail address and your 16-character App Password below
    sender_email = "your_email@gmail.com"
    app_password = "your_app_password"  # Generated via Google Account > Security > App Passwords
    receiver_email = "recipient_email@gmail.com"

    # Construct clean email multipart container wrapper
    msg = MIMEMultipart()
    msg["Subject"] = f"⚠️ [RAKSHAK AI] {subject}"
    msg["From"] = sender_email
    msg["To"] = receiver_email

    # Attach the body text plain payload text
    msg.attach(MIMEText(text_message, "html"))

    # If forensic screenshot evidence exists, attach it to the email bundle inline
    if attachment_path and os.path.exists(attachment_path):
        try:
            with open(attachment_path, "rb") as f:
                img_data = f.read()
            image_attachment = MIMEImage(img_data, name=os.path.basename(attachment_path))
            msg.attach(image_attachment)
        except Exception as e:
            print(f"Error packing visual attachment: {e}")

    # Fire off SMTP delivery thread loops
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()  # Secure the connection with TLS encryption
        server.login(sender_email, app_password)
        server.sendmail(sender_email, receiver_email, msg.as_string())
        server.quit()
        print(f"📧 Security alert notification successfully broadcast to {receiver_email}")
    except Exception as e:
        print(f"SMTP Relay System Fault: {e}. (Ensure App Passwords are valid).")