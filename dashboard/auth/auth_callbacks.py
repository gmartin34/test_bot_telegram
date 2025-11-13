from dash import Input, Output, State, html, dcc, callback, no_update
from dash.exceptions import PreventUpdate
import dash
from flask import session
from dashboard.auth.auth_queries import (
    verify_user_credentials,
    get_user_by_email,
    create_password_reset_token,
    verify_reset_token,
    update_user_password,
    mark_token_as_used
)
from dashboard.auth.auth_utils import (
    login_user,
    logout_user,
    send_reset_email,
    is_authenticated
)
from dashboard.components.login import (
    create_login_error_alert,
    create_login_success_alert,
    create_login_info_alert
)
from dashboard.components.forgot_password import (
    create_forgot_error_alert,
    create_forgot_warning_alert
)
from dashboard.components.reset_password import create_password_strength_indicator
import re


def register_auth_callbacks(app):
    """
    Registra todos los callbacks relacionados con autenticación
    """
    
    # Callback para el login
    @app.callback(
        [Output('login-alert', 'children'),
         Output('login-redirect-store', 'data')],
        [Input('login-button', 'n_clicks')],
        [State('login-username', 'value'),
         State('login-password', 'value')],
        prevent_initial_call=True
    )
    def handle_login(n_clicks, username, password):
        if n_clicks == 0:
            raise PreventUpdate
        
        # Validar campos vacíos
        if not username or not password:
            return create_login_error_alert("Por favor, completa todos los campos"), no_update
        
        # Verificar credenciales
        user = verify_user_credentials(username, password)
        
        if user:
            # Login exitoso
            login_user(username)
            return create_login_success_alert("¡Inicio de sesión exitoso! Redirigiendo..."), {'redirect': True}
        else:
            # Login fallido
            return create_login_error_alert("Usuario o contraseña incorrectos"), no_update
    
    
    # Callback para redirección después del login
    @app.callback(
        Output('url', 'pathname'),
        Input('login-redirect-store', 'data'),
        prevent_initial_call=True
    )
    def redirect_after_login(data):
        if data and data.get('redirect'):
            return '/dashboard/'
        raise PreventUpdate
    
    
    # Callback para mostrar mensaje cuando se llega desde logout
    @app.callback(
        Output('login-alert', 'children', allow_duplicate=True),
        Input('login-url', 'search'),
        prevent_initial_call=True
    )
    def show_logout_message(search):
        if search and 'logout=true' in search:
            return create_login_info_alert("Has cerrado sesión exitosamente")
        raise PreventUpdate
    
    
    # Callback para manejar recuperación de contraseña
    @app.callback(
        [Output('forgot-password-alert', 'children'),
         Output('forgot-success-message', 'style'),
         Output('forgot-email', 'disabled'),
         Output('forgot-submit-button', 'disabled')],
        Input('forgot-submit-button', 'n_clicks'),
        State('forgot-email', 'value'),
        prevent_initial_call=True
    )
    def handle_forgot_password(n_clicks, email):
        if n_clicks == 0:
            raise PreventUpdate
        
        # Validar email
        if not email:
            return (
                create_forgot_error_alert("Por favor, ingresa tu correo electrónico"),
                {"display": "none"},
                False,
                False
            )
        
        # Validar formato de email
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            return (
                create_forgot_error_alert("Por favor, ingresa un correo electrónico válido"),
                {"display": "none"},
                False,
                False
            )
        
        # Buscar usuario por email
        user = get_user_by_email(email)
        
        if user and user['is_active']:
            # Crear token y enviar email
            token = create_password_reset_token(user['id'])
            if token:
                send_reset_email(email, token, user['username'])
        
        # Siempre mostrar mensaje de éxito (por seguridad)
        return (
            no_update,
            {"display": "block"},
            True,
            True
        )
    
    
    # Callback para verificar token al cargar página de reset
    @app.callback(
        [Output('reset-password-alert', 'children'),
         Output('reset-password-form-container', 'style'),
         Output('reset-token-store', 'data', allow_duplicate=True)],
        Input('url', 'search'),
        prevent_initial_call=True
    )
    def verify_token_on_load(search):
        if '/reset-password' not in dash.callback_context.triggered[0]['prop_id']:
            raise PreventUpdate
        
        # Extraer token de la URL
        token = None
        if search:
            params = search.replace('?', '').split('&')
            for param in params:
                if param.startswith('token='):
                    token = param.replace('token=', '')
                    break
        
        if not token:
            return (
                html.Div([
                    html.H5("Enlace Inválido", className="text-danger"),
                    html.P("No se encontró un token válido en el enlace."),
                    html.A("Solicitar nuevo enlace", href="/dashboard/forgot-password", 
                          className="btn btn-primary")
                ]),
                {"display": "none"},
                None
            )
        
        # Verificar token
        token_data = verify_reset_token(token)
        
        if not token_data:
            return (
                html.Div([
                    html.H5("Enlace Expirado o Inválido", className="text-danger"),
                    html.P("Este enlace ha expirado o ya fue utilizado."),
                    html.A("Solicitar nuevo enlace", href="/dashboard/forgot-password", 
                          className="btn btn-primary")
                ]),
                {"display": "none"},
                None
            )
        
        # Token válido
        return (
            html.Div([
                html.P(f"Usuario: {token_data['username']}", className="text-info")
            ]),
            {"display": "block"},
            token
        )
    
    
    # Callback para mostrar indicador de fortaleza de contraseña
    @app.callback(
        Output('password-strength-indicator', 'children'),
        Input('reset-new-password', 'value')
    )
    def update_password_strength(password):
        if not password:
            return html.Div()
        return create_password_strength_indicator(password)
    
    
    # Callback para manejar el reset de contraseña
    @app.callback(
        [Output('reset-password-alert', 'children', allow_duplicate=True),
         Output('reset-success-container', 'style'),
         Output('reset-password-form-container', 'style', allow_duplicate=True)],
        Input('reset-submit-button', 'n_clicks'),
        [State('reset-new-password', 'value'),
         State('reset-confirm-password', 'value'),
         State('reset-token-store', 'data')],
        prevent_initial_call=True
    )
    def handle_reset_password(n_clicks, new_password, confirm_password, token):
        if n_clicks == 0:
            raise PreventUpdate
        
        # Validar token
        if not token:
            return (
                html.Div([
                    html.H5("Error", className="text-danger"),
                    html.P("Token inválido. Por favor, solicita un nuevo enlace.")
                ]),
                {"display": "none"},
                {"display": "none"}
            )
        
        # Validar campos
        if not new_password or not confirm_password:
            return (
                create_forgot_error_alert("Por favor, completa todos los campos"),
                {"display": "none"},
                {"display": "block"}
            )
        
        # Validar longitud de contraseña
        if len(new_password) < 6:
            return (
                create_forgot_error_alert("La contraseña debe tener al menos 6 caracteres"),
                {"display": "none"},
                {"display": "block"}
            )
        
        # Validar que las contraseñas coincidan
        if new_password != confirm_password:
            return (
                create_forgot_error_alert("Las contraseñas no coinciden"),
                {"display": "none"},
                {"display": "block"}
            )
        
        # Verificar token nuevamente
        token_data = verify_reset_token(token)
        if not token_data:
            return (
                html.Div([
                    html.H5("Token Expirado", className="text-danger"),
                    html.P("Este enlace ha expirado. Por favor, solicita uno nuevo.")
                ]),
                {"display": "none"},
                {"display": "none"}
            )
        
        # Actualizar contraseña
        if update_user_password(token_data['user_id'], new_password):
            # Marcar token como usado
            mark_token_as_used(token_data['token_id'])
            
            return (
                no_update,
                {"display": "block"},
                {"display": "none"}
            )
        else:
            return (
                create_forgot_error_alert("Error al actualizar la contraseña. Por favor, intenta nuevamente."),
                {"display": "none"},
                {"display": "block"}
            )
    
    
    # Callback para logout
    @app.callback(
        Output('url', 'pathname', allow_duplicate=True),
        Input('logout-button', 'n_clicks'),
        prevent_initial_call=True
    )
    def handle_logout(n_clicks):
        if n_clicks:
            logout_user()
            return '/dashboard/login'
        raise PreventUpdate