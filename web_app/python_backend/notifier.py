import aiosmtplib
from email.message import EmailMessage
import os

SMTP_HOSTNAME = ""
SMTP_PORT =
SMTP_USERNAME = ""
SMTP_PASSWORD = ""

async def send_result_email(user_email: str, job_id: str, file_path: str):
    msg = EmailMessage()
    msg["From"] = SMTP_USERNAME
    msg["To"] = user_email
    msg["Subject"] = f"scAdapter Job Completed [{job_id}]"
    
    body = (
        "Hello,\n\n"
        "Your automated cell type annotation job is complete. "
        "Please find your annotated csv attached.\n\n"
        "Best regards,\nThe scAdapter Team"
    )
    msg.set_content(body)

    try:
        with open(file_path, "rb") as f:
            csv_data = f.read()
            
        filename = os.path.basename(file_path)
        msg.add_attachment(csv_data, maintype="text", subtype="csv", filename=filename)
        
        await aiosmtplib.send(
            msg,
            hostname=SMTP_HOSTNAME,
            port=SMTP_PORT,
            start_tls=True,
            username=SMTP_USERNAME,
            password=SMTP_PASSWORD
        )
        print(f"[EMAIL] Sent results to {user_email}")
        
    except Exception as e:
        print(f"[EMAIL ERROR] Failed to send to {user_email}: {e}")
