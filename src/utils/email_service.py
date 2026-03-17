import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from src.logger import logger

# Gmail SMTP config — set these in your .env file
SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USER = os.getenv("SMTP_USER", "")   # your Gmail address e.g. yourname@gmail.com
SMTP_PASS = os.getenv("SMTP_PASS", "")   # Gmail App Password (not your account password)
                                          # Generate at: Google Account > Security > App Passwords


def build_invoice_html(bill_data: dict) -> str:
    rows = ""
    for item in bill_data["items"]:
        rows += f"""
        <tr>
            <td>{item['product_code']}</td>
            <td>{item['product_name']}</td>
            <td>{item['quantity']}</td>
            <td>{item['unit_price']:.2f}</td>
            <td>{item['purchase_price']:.2f}</td>
            <td>{item['tax_percentage']:.1f}%</td>
            <td>{item['tax_payable']:.2f}</td>
            <td>{item['total_price']:.2f}</td>
        </tr>"""

    return f"""
    <html><body style="font-family:Arial,sans-serif;font-size:14px;">
        <h2>Invoice — Bill #{bill_data['bill_id']}</h2>
        <p>Thank you for your purchase!</p>
        <table border="1" cellpadding="6" cellspacing="0" style="border-collapse:collapse;width:100%;">
            <thead style="background:#eee;">
                <tr>
                    <th>Product ID</th><th>Name</th><th>Qty</th><th>Unit Price</th>
                    <th>Purchase Price</th><th>Tax %</th><th>Tax</th><th>Total</th>
                </tr>
            </thead>
            <tbody>{rows}</tbody>
        </table>
        <br>
        <table cellpadding="4">
            <tr><td>Total (excl. tax):</td><td><b>{bill_data['total_without_tax']:.2f}</b></td></tr>
            <tr><td>Total tax:</td><td><b>{bill_data['total_tax']:.2f}</b></td></tr>
            <tr><td>Net price:</td><td><b>{bill_data['net_price']:.2f}</b></td></tr>
            <tr><td>Rounded net price:</td><td><b>{bill_data['rounded_net_price']:.2f}</b></td></tr>
            <tr><td>Cash paid:</td><td><b>{bill_data['cash_paid']:.2f}</b></td></tr>
            <tr><td>Balance returned:</td><td><b>{bill_data['balance']:.2f}</b></td></tr>
        </table>
    </body></html>
    """


def send_invoice_email(bill_data: dict) -> None:
    # runs in background via BackgroundTasks, failures won't affect the bill response
    customer_email = bill_data.get("customer_email", "")

    if not SMTP_USER or not SMTP_PASS:
        logger.info("SMTP not configured — skipping email for bill #%s", bill_data.get("bill_id"))
        return

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"Your Invoice — Bill #{bill_data['bill_id']}"
        msg["From"] = SMTP_USER
        msg["To"] = customer_email

        msg.attach(MIMEText(build_invoice_html(bill_data), "html"))

        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.ehlo()
            server.starttls()
            server.login(SMTP_USER, SMTP_PASS)
            server.sendmail(SMTP_USER, customer_email, msg.as_string())

        logger.info("invoice email sent for bill #%s to %s", bill_data.get("bill_id"), customer_email)
    except Exception as e:
        logger.error("failed to send invoice email for bill #%s: %s", bill_data.get("bill_id"), e)
