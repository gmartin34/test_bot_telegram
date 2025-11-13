from dash import html, dcc
import dash_bootstrap_components as dbc


def create_reset_password_page(token=None):
    """
    Crea la página para restablecer la contraseña
    """
    return html.Div([
        dbc.Container([
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader([
                            html.H3("UNED Trivial - Dashboard", className="text-center mb-0"),
                            html.P("Restablecer Contraseña", className="text-center text-muted mb-0")
                        ]),
                        dbc.CardBody([
                            html.H4("Nueva Contraseña", className="text-center mb-3"),
                            html.P(
                                "Ingresa tu nueva contraseña. Asegúrate de usar una contraseña segura.",
                                className="text-center text-muted mb-4"
                            ),
                            
                            # Alerta para mensajes
                            html.Div(id="reset-password-alert", className="mb-3"),
                            
                            # Formulario principal
                            html.Div(
                                id="reset-password-form-container",
                                children=[
                                    dbc.Form([
                                        # Token oculto
                                        dcc.Store(id='reset-token-store', data=token),
                                        
                                        dbc.Row([
                                            dbc.Col([
                                                dbc.Label("Nueva Contraseña", html_for="reset-new-password"),
                                                dbc.Input(
                                                    type="password",
                                                    id="reset-new-password",
                                                    placeholder="Mínimo 6 caracteres",
                                                    className="mb-3",
                                                    autoFocus=True
                                                ),
                                                dbc.FormText(
                                                    "La contraseña debe tener al menos 6 caracteres",
                                                    color="secondary"
                                                ),
                                            ])
                                        ]),
                                        
                                        dbc.Row([
                                            dbc.Col([
                                                dbc.Label("Confirmar Contraseña", html_for="reset-confirm-password"),
                                                dbc.Input(
                                                    type="password",
                                                    id="reset-confirm-password",
                                                    placeholder="Repite la contraseña",
                                                    className="mb-3"
                                                ),
                                            ])
                                        ], className="mt-3"),
                                        
                                        # Indicador de fortaleza de contraseña
                                        dbc.Row([
                                            dbc.Col([
                                                html.Div(id="password-strength-indicator", className="mb-3")
                                            ])
                                        ]),
                                        
                                        dbc.Row([
                                            dbc.Col([
                                                dbc.Button(
                                                    "Restablecer Contraseña",
                                                    id="reset-submit-button",
                                                    color="primary",
                                                    className="w-100",
                                                    size="lg",
                                                    n_clicks=0
                                                ),
                                            ])
                                        ], className="mb-3"),
                                    ]),
                                ]
                            ),
                            
                            # Mensaje de éxito (oculto inicialmente)
                            html.Div(
                                id="reset-success-container",
                                style={"display": "none"},
                                children=[
                                    dbc.Alert([
                                        html.H5("¡Contraseña Actualizada!", className="alert-heading"),
                                        html.P("Tu contraseña ha sido actualizada exitosamente."),
                                        html.Hr(),
                                        html.P(
                                            "Ya puedes iniciar sesión con tu nueva contraseña.",
                                            className="mb-0"
                                        )
                                    ], color="success"),
                                    dbc.Button(
                                        "Ir al Login",
                                        href="/dashboard/login",
                                        color="primary",
                                        className="w-100",
                                        size="lg"
                                    )
                                ]
                            ),
                            
                            # Enlaces adicionales
                            html.Div([
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
                    ], className="shadow"),
                ], md=6, lg=5, className="mx-auto")
            ], className="align-items-center", style={"minHeight": "80vh"})
        ], fluid=True)
    ], style={"backgroundColor": "#f8f9fa", "minHeight": "100vh", "paddingTop": "5rem"})


def create_password_strength_indicator(password):
    """
    Crea un indicador visual de la fortaleza de la contraseña
    """
    if not password:
        return html.Div()
    
    strength = 0
    feedback = []
    
    # Evaluar fortaleza
    if len(password) >= 6:
        strength += 25
    else:
        feedback.append("Mínimo 6 caracteres")
    
    if len(password) >= 8:
        strength += 25
    
    if any(c.isupper() for c in password) and any(c.islower() for c in password):
        strength += 25
    else:
        feedback.append("Usa mayúsculas y minúsculas")
    
    if any(c.isdigit() for c in password) or any(c in "!@#$%^&*()_+-=" for c in password):
        strength += 25
    else:
        feedback.append("Agrega números o símbolos")
    
    # Determinar color y mensaje
    if strength <= 25:
        color = "danger"
        message = "Débil"
    elif strength <= 50:
        color = "warning"
        message = "Regular"
    elif strength <= 75:
        color = "info"
        message = "Buena"
    else:
        color = "success"
        message = "Fuerte"
    
    return html.Div([
        dbc.Progress(
            value=strength,
            color=color,
            style={"height": "10px"},
            className="mb-2"
        ),
        html.Small(f"Fortaleza: {message}", className=f"text-{color}"),
        html.Div([
            html.Small(f"• {f}", className="text-muted d-block")
            for f in feedback
        ]) if feedback else None
    ])


def create_reset_error_page():
    """
    Crea una página de error para tokens inválidos
    """
    return html.Div([
        dbc.Container([
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader([
                            html.H3("UNED Trivial - Dashboard", className="text-center mb-0")
                        ]),
                        dbc.CardBody([
                            dbc.Alert([
                                html.H4("Enlace Inválido o Expirado", className="alert-heading"),
                                html.P(
                                    "El enlace de recuperación de contraseña no es válido o ha expirado."
                                ),
                                html.Hr(),
                                html.P([
                                    "Los enlaces de recuperación expiran después de 1 hora. ",
                                    "Si necesitas restablecer tu contraseña, solicita un nuevo enlace."
                                ], className="mb-0")
                            ], color="danger"),
                            
                            dbc.Button(
                                "Solicitar Nuevo Enlace",
                                href="/dashboard/forgot-password",
                                color="primary",
                                className="w-100 mb-3"
                            ),
                            dbc.Button(
                                "Volver al Login",
                                href="/dashboard/login",
                                color="secondary",
                                outline=True,
                                className="w-100"
                            )
                        ])
                    ], className="shadow")
                ], md=6, lg=5, className="mx-auto")
            ], className="align-items-center", style={"minHeight": "80vh"})
        ], fluid=True)
    ], style={"backgroundColor": "#f8f9fa", "minHeight": "100vh", "paddingTop": "5rem"})