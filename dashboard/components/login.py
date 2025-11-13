from dash import html, dcc
import dash_bootstrap_components as dbc


def create_login_page():
    """
    Crea la página de login
    """
    return html.Div([
        dbc.Container([
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader([
                            html.H3("UNED Trivial - Dashboard", className="text-center mb-0"),
                            html.P("Panel de Control", className="text-center text-muted mb-0")
                        ]),
                        dbc.CardBody([
                            html.H4("Iniciar Sesión", className="text-center mb-4"),
                            
                            # Alerta para mensajes de error
                            html.Div(id="login-alert", className="mb-3"),
                            
                            # Formulario de login
                            dbc.Form([
                                dbc.Row([
                                    dbc.Col([
                                        dbc.Label("Usuario", html_for="login-username"),
                                        dbc.Input(
                                            type="text",
                                            id="login-username",
                                            placeholder="Ingrese su usuario",
                                            className="mb-3",
                                            autoFocus=True
                                        ),
                                    ])
                                ]),
                                dbc.Row([
                                    dbc.Col([
                                        dbc.Label("Contraseña", html_for="login-password"),
                                        dbc.Input(
                                            type="password",
                                            id="login-password",
                                            placeholder="Ingrese su contraseña",
                                            className="mb-3"
                                        ),
                                    ])
                                ]),
                                dbc.Row([
                                    dbc.Col([
                                        dbc.Button(
                                            "Iniciar Sesión",
                                            id="login-button",
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
                                                "¿Olvidaste tu contraseña?",
                                                href="/dashboard/forgot-password",
                                                className="text-decoration-none"
                                            )
                                        ], className="text-center"),
                                    ])
                                ])
                            ])
                        ])
                    ], className="shadow"),
                ], md=6, lg=4, className="mx-auto")
            ], className="align-items-center", style={"minHeight": "80vh"})
        ], fluid=True),
        
        # Store para manejar redirecciones
        dcc.Store(id='login-redirect-store'),
        
        # Location para detectar cuando llegamos de una redirección
        dcc.Location(id='login-url', refresh=False)
    ], style={"backgroundColor": "#f8f9fa", "minHeight": "100vh", "paddingTop": "5rem"})


def create_login_error_alert(message):
    """
    Crea una alerta de error para el login
    """
    return dbc.Alert(
        [
            html.I(className="fas fa-exclamation-triangle me-2"),
            message
        ],
        color="danger",
        dismissable=True
    )


def create_login_success_alert(message):
    """
    Crea una alerta de éxito para el login
    """
    return dbc.Alert(
        [
            html.I(className="fas fa-check-circle me-2"),
            message
        ],
        color="success",
        dismissable=True
    )


def create_login_info_alert(message):
    """
    Crea una alerta informativa para el login
    """
    return dbc.Alert(
        [
            html.I(className="fas fa-info-circle me-2"),
            message
        ],
        color="info",
        dismissable=True
    )