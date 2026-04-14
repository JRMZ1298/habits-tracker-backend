import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

SMTP_HOST   = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT   = int(os.getenv("SMTP_PORT", 587))
SMTP_USER   = os.getenv("SMTP_USER")
SMTP_PASS   = os.getenv("SMTP_PASS")

def send_reminder(to_email: str, user_name: str, habits: list[str]):
    msg = MIMEMultipart("alternative")
    msg["Subject"] = "⏰ No olvides tus hábitos de hoy"
    msg["From"]    = SMTP_USER
    msg["To"]      = to_email

    habit_list = "".join(f"<li>{h}</li>" for h in habits)
    html = f"""
    <h2>Hola {user_name} 👋</h2>
    <p>Estos hábitos te están esperando hoy:</p>
    <ul>{habit_list}</ul>
    <p>¡No rompas tu racha!</p>
    """
    msg.attach(MIMEText(html, "html"))

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
        server.starttls()
        server.login(SMTP_USER, SMTP_PASS)
        server.sendmail(SMTP_USER, to_email, msg.as_string())


def send_streak_milestone(to_email: str, user_name: str, habit: str, streak: int):
    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"🔥 ¡{streak} días seguidos con '{habit}'!"
    msg["From"]    = SMTP_USER
    msg["To"]      = to_email

    html = f"""
    <h2>¡Felicidades {user_name}!</h2>
    <p>Llevas <strong>{streak} días consecutivos</strong> completando <em>{habit}</em>.</p>
    <p>Sigue así 💪</p>
    """
    msg.attach(MIMEText(html, "html"))

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
        server.starttls()
        server.login(SMTP_USER, SMTP_PASS)
        server.sendmail(SMTP_USER, to_email, msg.as_string())