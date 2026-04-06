import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Optional

from src.core.config import settings

logger = logging.getLogger(__name__)

class EmailService:
    """SMTP email service with async-compatible wrapper."""

    def _build_message(self, to: str, subject: str, html_body: str) -> MIMEMultipart:
        msg = MIMEMultipart("alternative")
        msg["From"] = settings.SMTP_FROM
        msg["To"] = to
        msg["Subject"] = subject
        msg.attach(MIMEText(html_body, "html"))
        return msg

    def _send(self, msg: MIMEMultipart) -> None:
        try:
            with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
                server.ehlo()
                if settings.SMTP_TLS:
                    server.starttls()
                if settings.SMTP_USER and settings.SMTP_PASSWORD:
                    server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                server.send_message(msg)
        except smtplib.SMTPException as exc:
            logger.error("Failed to send email to %s: %s", msg["To"], exc)
            raise

    async def send_welcome(self, to: str, username: str) -> None:
        subject = f"Welcome to {settings.PROJECT_NAME}!"
        body = f"<h1>Welcome, {username}!</h1><p>Your account has been created successfully.</p>"
        msg = self._build_message(to=to, subject=subject, html_body=body)
        self._send(msg)
        logger.info("Welcome email sent to %s", to)

    async def send_password_reset(self, to: str, reset_token: str) -> None:
        reset_url = f"{settings.FRONTEND_URL}/reset-password?token={reset_token}"
        subject = "Password reset request"
        body = f"<p>Click <a href='{reset_url}'>here</a> to reset your password. Link expires in 1 hour.</p>"
        msg = self._build_message(to=to, subject=subject, html_body=body)
        self._send(msg)
        logger.info("Password reset email sent to %s", to)

    async def send_notification(self, to: str, title: str, body_text: str) -> None:
        subject = f"[{settings.PROJECT_NAME}] {title}"
        body = f"<h2>{title}</h2><p>{body_text}</p>"
        msg = self._build_message(to=to, subject=subject, html_body=body)
        self._send(msg)
        logger.info("Notification email sent to %s: %s", to, title)