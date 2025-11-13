from dash import html, dcc
import dash_bootstrap_components as dbc


def create_forgot_password_page():
    """
    Crea la página de recuperación de contraseña
    """
    return html.Div([
        dbc.Container([
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader([
                            html.H3("UNED Trivial - Dashboard", className="text-center mb-0"),
                            html.P("Recuperación de Contraseña", className="text-center text-muted mb-0")
                        ]),
                        dbc.CardBody([
                            html.H4("¿Olvidaste tu contraseña?", className="text-center mb-3"),
                            html.P(
                                "Ingresa tu correo electrónico y te enviaremos un enlace para restablecer tu contraseña.",
                                className="text-center text-muted mb-4"
                            ),
                            
                            # Alerta para mensajes
                            html.Div(id="forgot-password-alert", className="mb-3"),
                            
                            # Formulario
                            dbc.Form([
                                dbc.Row([
                                    dbc.Col([
                                        dbc.Label("Correo Electrónico", html_for="forgot-email"),
                                        dbc.Input(
                                            type="email",
                                            id="forgot-email",
                                            placeholder="correo@ejemplo.com",
                                            className="mb-3",
                                            autoFocus=True
                                        ),
                                    ])
                                ]),
                                dbc.Row([
                                    dbc.Col([
                                        dbc.Button(
                                            "Enviar Enlace de Recuperación",
                                            id="forgot-submit-button",
                                            color="primary",
                                            className="w-100",
                                            size="lg",
                                            n_clicks=0
                                        ),
                                    ])
                                ], className="mb-3"),
                                
                                # Enlaces adicionales
                                dbc.Row([
                                    dbc.Col([
                                        html.Hr(),
                                        html.Div([
                                            html.A(
                                                "Volver al inicio de sesión",
                                                href="/dashboard/login",
                                                className="text-decoration-none"
                                            )
                                        ], className="text-center"),
                                    ])
                                ])
                            ]),
                            
                            # Div oculto para mostrar cuando se envía el email
                            html.Div(
                                id="forgot-success-message",
                                style={"display": "none"},
                                children=[
                                    html.Hr(className="my-4"),
                                    dbc.Alert([
                                        html.H5("¡Email Enviado!", className="alert-heading"),
                                        html.P([
                                            "Si el correo electrónico está registrado en nuestro sistema, ",
                                            "recibirás un enlace para restablecer tu contraseña."
                                        ]),
                                        html.Hr(),
                                        html.P([
                                            "Por favor, revisa tu bandeja de entrada y la carpeta de spam. ",
                                            "El enlace expirará en 1 hora."
                                        ], className="mb-0")
                                    ], color="success"),
                                    dbc.Button(
                                        "Volver al Login",
                                        href="/dashboard/login",
                                        color="primary",
                                        className="w-100"
                                    )
                                ]
                            )
                        ])
                    ], className="shadow"),
                ], md=6, lg=5, className="mx-auto")
            ], className="align-items-center", style={"minHeight": "80vh"})
        ], fluid=True),
        
        # Store para manejar el estado
        dcc.Store(id='forgot-password-store')
    ], style={"backgroundColor": "#f8f9fa", "minHeight": "100vh", "paddingTop": "5rem"})


def create_forgot_error_alert(message):
    """
    Crea una alerta de error
    """
    return dbc.Alert(
        [
            html.I(className="fas fa-exclamation-triangle me-2"),
            message
        ],
        color="danger",
        dismissable=True
    )


def create_forgot_warning_alert(message):
    """
    Crea una alerta de advertencia
    """
    return dbc.Alert(
        [
            html.I(className="fas fa-exclamation-circle me-2"),
            message
        ],
        color="warning",
        dismissable=True
    )