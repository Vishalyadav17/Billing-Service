from src.logger import logger


def send_invoice_email(bill_data: dict) -> None:
    # runs in background via BackgroundTasks, failures won't affect the response
    # TODO: plug in SMTP here when ready (Gmail: smtp.gmail.com:587 with app password)
    logger.info("invoice for bill #%s queued to send to %s", bill_data.get("bill_id"), bill_data.get("customer_email"))
