# ============================================================
# alert_system.py - Automated Contamination Alert System
# Project: AI-Driven Assessment of Heavy Metal Pollution Indices
# ============================================================
#
# WHAT THIS MODULE DOES:
# When the anomaly detector flags a sudden contamination spike,
# this module composes and "sends" an alert to district health
# authorities / Jal Shakti officers.
#
# IMPORTANT DESIGN DECISION (read before using in a live demo):
# This ships in SIMULATION MODE by default. It builds the exact
# real message that would be sent, and shows it in the dashboard,
# WITHOUT requiring live Twilio/SMTP credentials. This is
# deliberate: a hackathon/viva demo that depends on a real SMS
# API key or a real email account login is a live-failure risk
# (expired trial credits, blocked ports, wrong credentials, etc).
#
# The actual sending logic (real Twilio SMS, real SMTP email) is
# fully implemented below and works correctly if you provide real
# credentials via environment variables - switch SIMULATION_MODE
# to False and set the credentials to go live. Until then, every
# call safely returns the composed message without any network
# calls, so the dashboard demo never depends on external services.
# ============================================================

import os
from datetime import datetime

SIMULATION_MODE = True  # set False + provide credentials below to send real alerts

# Real credentials (only used if SIMULATION_MODE = False)
TWILIO_ACCOUNT_SID = os.environ.get("TWILIO_ACCOUNT_SID", "")
TWILIO_AUTH_TOKEN = os.environ.get("TWILIO_AUTH_TOKEN", "")
TWILIO_FROM_NUMBER = os.environ.get("TWILIO_FROM_NUMBER", "")
ALERT_SMTP_HOST = os.environ.get("ALERT_SMTP_HOST", "smtp.gmail.com")
ALERT_SMTP_PORT = int(os.environ.get("ALERT_SMTP_PORT", "587"))
ALERT_SMTP_USER = os.environ.get("ALERT_SMTP_USER", "")
ALERT_SMTP_PASSWORD = os.environ.get("ALERT_SMTP_PASSWORD", "")


def compose_alert_message(location_name, hpi_value, safety_category, anomaly_score, season):
    timestamp = datetime.now().strftime("%d-%m-%Y %H:%M IST")
    return (
        f"[GROUNDWATER ALERT - SIH25067]\n"
        f"Time: {timestamp}\n"
        f"Location: {location_name or 'Unspecified'}\n"
        f"Season: {season}\n"
        f"Predicted HPI: {hpi_value:.1f} ({safety_category})\n"
        f"Anomaly Score: {anomaly_score:.3f} (below normal-range threshold)\n"
        f"Action: Sudden contamination pattern detected. Immediate field "
        f"verification recommended. Notify district health officer.\n"
        f"Source: AI-Driven Heavy Metal Pollution Assessment System, "
        f"Chennai Institute of Technology (ECE Dept.)"
    )


def send_sms_alert(to_number, message):
    """
    Sends a real SMS via Twilio if SIMULATION_MODE is False and
    credentials are set. Returns a result dict either way.
    """
    if SIMULATION_MODE or not (TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN and TWILIO_FROM_NUMBER):
        return {"sent": False, "simulated": True, "channel": "SMS",
                "detail": "Simulation mode - no real SMS sent. Message composed successfully."}
    try:
        from twilio.rest import Client
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        msg = client.messages.create(body=message, from_=TWILIO_FROM_NUMBER, to=to_number)
        return {"sent": True, "simulated": False, "channel": "SMS", "sid": msg.sid}
    except Exception as e:
        return {"sent": False, "simulated": False, "channel": "SMS", "error": str(e)}


def send_email_alert(to_email, subject, message):
    """
    Sends a real email via SMTP if SIMULATION_MODE is False and
    credentials are set. Returns a result dict either way.
    """
    if SIMULATION_MODE or not (ALERT_SMTP_USER and ALERT_SMTP_PASSWORD):
        return {"sent": False, "simulated": True, "channel": "Email",
                "detail": "Simulation mode - no real email sent. Message composed successfully."}
    try:
        import smtplib
        from email.mime.text import MIMEText
        msg = MIMEText(message)
        msg["Subject"] = subject
        msg["From"] = ALERT_SMTP_USER
        msg["To"] = to_email
        with smtplib.SMTP(ALERT_SMTP_HOST, ALERT_SMTP_PORT) as server:
            server.starttls()
            server.login(ALERT_SMTP_USER, ALERT_SMTP_PASSWORD)
            server.sendmail(ALERT_SMTP_USER, [to_email], msg.as_string())
        return {"sent": True, "simulated": False, "channel": "Email"}
    except Exception as e:
        return {"sent": False, "simulated": False, "channel": "Email", "error": str(e)}


def trigger_alert(location_name, hpi_value, safety_category, anomaly_score, season,
                    phone_number=None, email_address=None):
    """
    Main entry point: composes the alert and dispatches it (or
    simulates dispatch) via both SMS and Email channels.
    Returns the composed message plus both channel results.
    """
    message = compose_alert_message(location_name, hpi_value, safety_category, anomaly_score, season)
    results = []
    if phone_number:
        results.append(send_sms_alert(phone_number, message))
    if email_address:
        results.append(send_email_alert(email_address, "Groundwater Contamination Alert", message))
    return {"message": message, "results": results}
