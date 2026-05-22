"""Fake enterprise tools with no built-in governance checks."""

from shared.fake_enterprise_data import CONFIDENTIAL_INTERNAL_DOC


def read_internal_docs() -> str:
    """Return simulated confidential enterprise data."""
    return CONFIDENTIAL_INTERNAL_DOC


def send_email(to: str, subject: str, body: str) -> str:
    """Pretend to send an email without touching any real system."""
    return f"EMAIL SENT to {to}: {subject}\n{body}"


def delete_records(record_id: str) -> str:
    """Pretend to delete a record."""
    return f"RECORD DELETED: {record_id}"


def export_customer_data(destination: str) -> str:
    """Pretend to export customer data."""
    return f"CUSTOMER DATA EXPORTED to {destination}"
