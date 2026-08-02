import asyncio
import structlog
import json
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
import httpx
from ..config.settings import settings
from ..core.logging import get_logger

logger = get_logger(__name__)


class NotificationChannel:
    async def send(self, alert: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError


class DesktopNotification(NotificationChannel):
    async def send(self, alert: Dict[str, Any]) -> Dict[str, Any]:
        try:
            import subprocess
            import platform

            system = platform.system()
            title = f"AI-IDS Alert: {alert['threat_type']}"
            message = alert.get("message", alert.get("explanation", ""))

            if system == "Windows":
                import ctypes
                ctypes.windll.user32.MessageBoxW(0, message, title, 1)
            elif system == "Linux":
                subprocess.run(["notify-send", title, message], capture_output=True, timeout=5)
            elif system == "Darwin":
                subprocess.run(["osascript", "-e", f'display notification "{message}" with title "{title}"'],
                               capture_output=True, timeout=5)

            return {"channel": "desktop", "status": "sent"}
        except Exception as e:
            logger.error("Desktop notification failed", error=str(e))
            return {"channel": "desktop", "status": "failed", "error": str(e)}


class DiscordNotification(NotificationChannel):
    async def send(self, alert: Dict[str, Any]) -> Dict[str, Any]:
        webhook_url = settings.DISCORD_WEBHOOK_URL
        if not webhook_url:
            return {"channel": "discord", "status": "skipped", "reason": "not configured"}

        try:
            color_map = {"critical": 0xFF0000, "high": 0xFF6600, "medium": 0xFFCC00, "low": 0x00FF00}
            embed = {
                "title": f"🚨 AI-IDS Alert: {alert['threat_type']}",
                "description": alert.get("explanation", alert.get("message", "")),
                "color": color_map.get(alert.get("severity", "high").lower(), 0xFF6600),
                "fields": [
                    {"name": "Severity", "value": alert.get("severity", "unknown"), "inline": True},
                    {"name": "Confidence", "value": f"{alert.get('confidence', 0)*100:.1f}%", "inline": True},
                    {"name": "Source IP", "value": alert.get("src_ip", "unknown"), "inline": True},
                    {"name": "Destination IP", "value": alert.get("dst_ip", "unknown"), "inline": True},
                    {"name": "Recommendation", "value": alert.get("recommendation", "N/A"), "inline": False},
                ],
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
            payload = {"embeds": [embed]}
            async with httpx.AsyncClient() as client:
                response = await client.post(webhook_url, json=payload, timeout=10)
                response.raise_for_status()
            return {"channel": "discord", "status": "sent"}
        except Exception as e:
            logger.error("Discord notification failed", error=str(e))
            return {"channel": "discord", "status": "failed", "error": str(e)}


class SlackNotification(NotificationChannel):
    async def send(self, alert: Dict[str, Any]) -> Dict[str, Any]:
        webhook_url = settings.SLACK_WEBHOOK_URL
        if not webhook_url:
            return {"channel": "slack", "status": "skipped", "reason": "not configured"}

        try:
            blocks = [
                {"type": "section", "text": {"type": "mrkdwn", "text": f"*🚨 AI-IDS Alert: {alert['threat_type']}*"}},
                {"type": "section", "text": {"type": "mrkdwn", "text": alert.get("explanation", alert.get("message", ""))}},
                {"type": "divider"},
                {"type": "section",
                 "fields": [
                     {"type": "mrkdwn", "text": f"*Severity:*\n{alert.get('severity', 'unknown')}"},
                     {"type": "mrkdwn", "text": f"*Confidence:*\n{alert.get('confidence', 0)*100:.1f}%"},
                     {"type": "mrkdwn", "text": f"*Source IP:*\n{alert.get('src_ip', 'unknown')}"},
                     {"type": "mrkdwn", "text": f"*Destination IP:*\n{alert.get('dst_ip', 'unknown')}"},
                 ]},
            ]
            payload = {"blocks": blocks}
            async with httpx.AsyncClient() as client:
                response = await client.post(webhook_url, json=payload, timeout=10)
                response.raise_for_status()
            return {"channel": "slack", "status": "sent"}
        except Exception as e:
            logger.error("Slack notification failed", error=str(e))
            return {"channel": "slack", "status": "failed", "error": str(e)}


class TelegramNotification(NotificationChannel):
    async def send(self, alert: Dict[str, Any]) -> Dict[str, Any]:
        bot_token = settings.TELEGRAM_BOT_TOKEN
        chat_id = settings.TELEGRAM_CHAT_ID
        if not bot_token or not chat_id:
            return {"channel": "telegram", "status": "skipped", "reason": "not configured"}

        try:
            message = (
                f"🚨 *AI-IDS Alert: {alert['threat_type']}*\n\n"
                f"{alert.get('explanation', alert.get('message', ''))}\n\n"
                f"*Severity:* {alert.get('severity', 'unknown')}\n"
                f"*Confidence:* {alert.get('confidence', 0)*100:.1f}%\n"
                f"*Source IP:* {alert.get('src_ip', 'unknown')}\n"
                f"*Destination IP:* {alert.get('dst_ip', 'unknown')}\n"
                f"*Recommendation:* {alert.get('recommendation', 'N/A')}"
            )
            url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
            payload = {"chat_id": chat_id, "text": message, "parse_mode": "Markdown"}
            async with httpx.AsyncClient() as client:
                response = await client.post(url, json=payload, timeout=10)
                response.raise_for_status()
            return {"channel": "telegram", "status": "sent"}
        except Exception as e:
            logger.error("Telegram notification failed", error=str(e))
            return {"channel": "telegram", "status": "failed", "error": str(e)}


class EmailNotification(NotificationChannel):
    async def send(self, alert: Dict[str, Any]) -> Dict[str, Any]:
        if not all([settings.SMTP_SERVER, settings.SMTP_USER, settings.SMTP_PASSWORD, settings.SMTP_FROM]):
            return {"channel": "email", "status": "skipped", "reason": "not configured"}

        try:
            import smtplib
            from email.mime.text import MIMEText
            from email.mime.multipart import MIMEMultipart

            msg = MIMEMultipart("alternative")
            msg["Subject"] = f"AI-IDS Alert: {alert['threat_type']} - {alert.get('severity', 'unknown').upper()}"
            msg["From"] = settings.SMTP_FROM
            msg["To"] = settings.SMTP_FROM

            html = f"""
            <html><body>
            <h2 style="color:red;">🚨 AI-IDS Security Alert</h2>
            <h3>{alert['threat_type']}</h3>
            <p><b>Severity:</b> {alert.get('severity', 'unknown')}</p>
            <p><b>Confidence:</b> {alert.get('confidence', 0)*100:.1f}%</p>
            <p><b>Source IP:</b> {alert.get('src_ip', 'unknown')}</p>
            <p><b>Destination IP:</b> {alert.get('dst_ip', 'unknown')}</p>
            <hr>
            <p>{alert.get('explanation', alert.get('message', ''))}</p>
            <hr>
            <p><b>Recommendation:</b> {alert.get('recommendation', 'N/A')}</p>
            <p><small>Generated by AI-IDS at {datetime.now(timezone.utc).isoformat()}</small></p>
            </body></html>
            """
            msg.attach(MIMEText(html, "html"))

            with smtplib.SMTP(settings.SMTP_SERVER, settings.SMTP_PORT) as server:
                server.starttls()
                server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                server.send_message(msg)

            return {"channel": "email", "status": "sent"}
        except Exception as e:
            logger.error("Email notification failed", error=str(e))
            return {"channel": "email", "status": "failed", "error": str(e)}


class WebhookNotification(NotificationChannel):
    async def send(self, alert: Dict[str, Any]) -> Dict[str, Any]:
        webhook_url = alert.get("webhook_url", "")
        if not webhook_url:
            return {"channel": "webhook", "status": "skipped", "reason": "no URL"}

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(webhook_url, json=alert, timeout=10, headers={"Content-Type": "application/json"})
                response.raise_for_status()
            return {"channel": "webhook", "status": "sent"}
        except Exception as e:
            logger.error("Webhook notification failed", error=str(e))
            return {"channel": "webhook", "status": "failed", "error": str(e)}


class FirebaseNotification(NotificationChannel):
    async def send(self, alert: Dict[str, Any]) -> Dict[str, Any]:
        if not settings.FIREBASE_CREDENTIALS_PATH:
            return {"channel": "firebase", "status": "skipped", "reason": "not configured"}

        try:
            import firebase_admin
            from firebase_admin import credentials, messaging

            if not firebase_admin._apps:
                cred = credentials.Certificate(settings.FIREBASE_CREDENTIALS_PATH)
                firebase_admin.initialize_app(cred)

            message = messaging.Message(
                notification=messaging.Notification(
                    title=f"🚨 {alert['threat_type']}",
                    body=f"{alert.get('severity', 'alert').upper()}: {alert.get('explanation', alert.get('message', ''))[:200]}",
                ),
                data={
                    "threat_type": alert["threat_type"],
                    "severity": alert.get("severity", ""),
                    "confidence": str(alert.get("confidence", 0)),
                    "src_ip": alert.get("src_ip", ""),
                    "dst_ip": alert.get("dst_ip", ""),
                    "alert_id": alert.get("id", ""),
                },
                topic="alerts",
            )
            response = messaging.send(message)
            return {"channel": "firebase", "status": "sent", "response": response}
        except Exception as e:
            logger.error("Firebase notification failed", error=str(e))
            return {"channel": "firebase", "status": "failed", "error": str(e)}


class AlertEngine:
    def __init__(self):
        self._channels: List[NotificationChannel] = []

        if settings.ENVIRONMENT == "development" and not settings.RENDER:
            self._channels.append(DesktopNotification())

        if settings.DISCORD_WEBHOOK_URL:
            self._channels.append(DiscordNotification())
        if settings.SLACK_WEBHOOK_URL:
            self._channels.append(SlackNotification())
        if settings.TELEGRAM_BOT_TOKEN and settings.TELEGRAM_CHAT_ID:
            self._channels.append(TelegramNotification())
        if settings.SMTP_SERVER:
            self._channels.append(EmailNotification())
        if settings.FIREBASE_CREDENTIALS_PATH:
            self._channels.append(FirebaseNotification())

        self._webhook_channel = WebhookNotification()
        self._alert_history: List[Dict[str, Any]] = []

    async def send_alert(self, alert: Dict[str, Any]) -> Dict[str, Any]:
        results = {}
        for channel in self._channels:
            try:
                result = await channel.send(alert)
                results[result.get("channel", "unknown")] = result
            except Exception as e:
                logger.error("Channel send failed", channel=type(channel).__name__, error=str(e))
                results[type(channel).__name__] = {"status": "failed", "error": str(e)}

        alert["delivery_status"] = results
        self._alert_history.append(alert)

        return {
            "alert": alert,
            "delivery_results": results,
        }

    async def send_webhook_alert(self, alert: Dict[str, Any], webhook_url: str) -> Dict[str, Any]:
        alert["webhook_url"] = webhook_url
        return await self._webhook_channel.send(alert)

    def get_alert_history(self) -> List[Dict[str, Any]]:
        return self._alert_history

    def get_channel_status(self) -> Dict[str, bool]:
        return {
            "desktop": any(isinstance(c, DesktopNotification) for c in self._channels),
            "discord": settings.DISCORD_WEBHOOK_URL is not None,
            "slack": settings.SLACK_WEBHOOK_URL is not None,
            "telegram": settings.TELEGRAM_BOT_TOKEN is not None,
            "email": settings.SMTP_SERVER is not None,
            "firebase": settings.FIREBASE_CREDENTIALS_PATH is not None,
        }

    async def send_alert_to_all(self, alert_data: Dict[str, Any]) -> Dict[str, Any]:
        return await self.send_alert(alert_data)


alert_engine = AlertEngine()
