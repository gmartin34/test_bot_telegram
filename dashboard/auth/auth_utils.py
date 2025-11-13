import hashlib
import secrets
import string
from datetime import datetime, timedelta
from functools import wraps
from flask import session, redirect, url_for, request
import dash
from dash import html
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


def hash_password(password):
    """
    Genera hash SHA-256 de una contraseña
    """
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(password, hashed):
    """
    Verifica si una contraseña coincide con su hash
    """
    return hash_password(password) == hashed


def generate_token(length=32):
    """
    Genera un token aleatorio seguro
    """
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))


def is_authenticated():
    """
    Verifica si el usuario está autenticado
    """
    return session.get('authenticated', False)


def get_current_user():
    """
    Obtiene el usuario actual de la sesión
    """
    return session.get('username', None)


def login_user(username):
    """
    Registra al usuario en la sesión
    """
    session['authenticated'] = True
    session['username'] = username
    session['login_time'] = datetime.now().isoformat()


def logout_user():
    """
    Cierra la sesión del usuario
    """
    session.pop('authenticated', None)
    session.pop('username', None)
    session.pop('login_time', None)


def require_auth(f):
    """
    Decorador para proteger rutas que requieren autenticación
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not is_authenticated():
            return redirect('/dashboard/login')
        return f(*args, **kwargs)
    return decorated_function


def check_session_timeout(timeout_minutes=30):
    """
    Verifica si la sesión ha expirado
    """
    if 'login_time' in session:
        login_time = datetime.fromisoformat(session['login_time'])
        if datetime.now() - login_time > timedelta(minutes=timeout_minutes):
            logout_user()
            return True
    return False


def send_reset_email(email, token, username):
    """
    Envía email de recuperación de contraseña
    NOTA: Esta es una implementación básica. En producción usar un servicio de email
    """
    # Configuración del servidor SMTP (ejemplo con Gmail)
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    sender_email = "noreply@uned-trivial.com"  # Cambiar en producción
    sender_password = "password"  # Usar variables de entorno en producción
    
    # Crear mensaje
    message = MIMEMultipart("alternative")
    message["Subject"] = "Recuperación de contraseña - UNED Trivial"
    message["From"] = sender_email
    message["To"] = email
    
    # Contenido del email
    text = f"""
    Hola {username},
    
    Has solicitado restablecer tu contraseña.
    
    Para continuar, haz clic en el siguiente enlace:
    http://localhost:5000/dashboard/reset-password?token={token}
    
    Este enlace expirará en 1 hora.
    
    Si no solicitaste este cambio, ignora este mensaje.
    
    Saludos,
    Equipo UNED Trivial
    """
    
    html_content = f"""
    <html>
      <body>
        <h2>Recuperación de contraseña</h2>
        <p>Hola <strong>{username}</strong>,</p>
        <p>Has solicitado restablecer tu contraseña.</p>
        <p>Para continuar, haz clic en el siguiente enlace:</p>
        <p><a href="http://localhost:5000/dashboard/reset-password?token={token}" 
              style="background-color: #007bff; color: white; padding: 10px 20px; 
                     text-decoration: none; border-radius: 5px;">
              Restablecer contraseña
           </a></p>
        <p>Este enlace expirará en 1 hora.</p>
        <p>Si no solicitaste este cambio, ignora este mensaje.</p>
        <hr>
        <p><small>Equipo UNED Trivial</small></p>
      </body>
    </html>
    """
    
    # Adjuntar partes del mensaje
    part1 = MIMEText(text, "plain")
    part2 = MIMEText(html_content, "html")
    message.attach(part1)
    message.attach(part2)
    
    # En desarrollo, solo imprimir el enlace
    print(f"\n=== EMAIL DE RECUPERACIÓN ===")
    print(f"Para: {email}")
    print(f"Usuario: {username}")
    print(f"Token: {token}")
    print(f"Enlace: http://localhost:5000/dashboard/reset-password?token={token}")
    print(f"============================\n")
    
    # En producción, descomentar para enviar email real:
    """
    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, email, message.as_string())
        server.quit()
        return True
    except Exception as e:
        print(f"Error enviando email: {e}")
        return False
    """
    return True


def create_protected_layout(content):
    """
    Envuelve el contenido en una verificación de autenticación
    """
    if not is_authenticated():
        return html.Div([
            html.H3("Acceso Denegado", className="text-danger"),
            html.P("Debes iniciar sesión para acceder a esta página."),
            html.A("Ir al Login", href="/dashboard/login", className="btn btn-primary")
        ])
    
    # Verificar timeout de sesión
    if check_session_timeout():
        return html.Div([
            html.H3("Sesión Expirada", className="text-warning"),
            html.P("Tu sesión ha expirado. Por favor, inicia sesión nuevamente."),
            html.A("Ir al Login", href="/dashboard/login", className="btn btn-primary")
        ])
    
    return content