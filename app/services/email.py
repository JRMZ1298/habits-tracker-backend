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

def send_weekly_summary(
    to_email: str,
    user_name: str,
    stats: dict
):
    """
    stats debe contener:
    - total_week:     int   (hábitos completados esta semana)
    - best_streak:    int   (mejor racha activa)
    - level:          int
    - total_all_time: int
    - top_habit:      str   (hábito más completado)
    - days_data:      list  (completados por día)
    """
    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"📊 Tu resumen semanal — {user_name}"
    msg["From"]    = SMTP_USER
    msg["To"]      = to_email

    # Barras de texto para la gráfica semanal en el email
    days_html = ""
    max_val   = max((d["completed"] for d in stats["days_data"]), default=1)
    for d in stats["days_data"]:
        pct   = int((d["completed"] / max(max_val, 1)) * 100)
        days_html += f"""
            <div style="display:flex;align-items:center;gap:8px;margin-bottom:6px;">
              <span style="width:32px;font-size:11px;color:#666;">{d['day']}</span>
              <div style="flex:1;background:#f0f0f0;border-radius:4px;height:8px;">
                <div style="width:{pct}%;background:#534AB7;border-radius:4px;height:8px;"></div>
              </div>
              <span style="font-size:11px;color:#666;">{d['completed']}</span>
            </div>"""

    html = f"""
    <div style="font-family:sans-serif;max-width:520px;margin:auto;padding:32px;">
      <h1 style="color:#534AB7;font-size:28px;margin-bottom:4px;">
        Hola, {user_name} 👋
      </h1>
      <p style="color:#666;margin-bottom:32px;">
        Aquí está tu resumen de la semana.
      </p>

      <!-- Stats principales -->
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-bottom:32px;">
        <div style="background:#EEEDFE;border-radius:12px;padding:20px;">
          <p style="font-size:11px;color:#534AB7;font-weight:700;
                    text-transform:uppercase;letter-spacing:1px;margin:0 0 4px;">
            Esta semana
          </p>
          <p style="font-size:40px;font-weight:900;color:#2C2C2A;margin:0;">
            {stats['total_week']}
          </p>
          <p style="font-size:13px;color:#666;margin:0;">hábitos completados</p>
        </div>
        <div style="background:#E1F5EE;border-radius:12px;padding:20px;">
          <p style="font-size:11px;color:#1D9E75;font-weight:700;
                    text-transform:uppercase;letter-spacing:1px;margin:0 0 4px;">
            Mejor racha
          </p>
          <p style="font-size:40px;font-weight:900;color:#2C2C2A;margin:0;">
            {stats['best_streak']}
          </p>
          <p style="font-size:13px;color:#666;margin:0;">días consecutivos</p>
        </div>
      </div>

      <!-- Gráfica semanal -->
      <div style="background:#f9f9f9;border-radius:12px;padding:20px;margin-bottom:32px;">
        <p style="font-size:11px;font-weight:700;text-transform:uppercase;
                  letter-spacing:1px;color:#666;margin:0 0 16px;">
          Actividad por día
        </p>
        {days_html}
      </div>

      <!-- Stats adicionales -->
      <div style="border-top:1px solid #eee;padding-top:24px;
                  display:flex;justify-content:space-between;">
        <div>
          <p style="font-size:11px;color:#999;margin:0;">Nivel actual</p>
          <p style="font-size:20px;font-weight:700;color:#2C2C2A;margin:0;">
            {stats['level']}
          </p>
        </div>
        <div>
          <p style="font-size:11px;color:#999;margin:0;">Total histórico</p>
          <p style="font-size:20px;font-weight:700;color:#2C2C2A;margin:0;">
            {stats['total_all_time']:,}
          </p>
        </div>
        <div>
          <p style="font-size:11px;color:#999;margin:0;">Hábito estrella</p>
          <p style="font-size:14px;font-weight:700;color:#2C2C2A;margin:0;">
            {stats.get('top_habit', '—')}
          </p>
        </div>
      </div>

      <p style="margin-top:32px;font-size:12px;color:#999;text-align:center;">
        Puedes desactivar estos correos desde tu perfil.
      </p>
    </div>
    """

    msg.attach(MIMEText(html, "html"))
    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
        server.starttls()
        server.login(SMTP_USER, SMTP_PASS)
        server.sendmail(SMTP_USER, to_email, msg.as_string())