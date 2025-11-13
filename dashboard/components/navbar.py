import dash_bootstrap_components as dbc
from dash import html


def create_navbar():
    """Crea la barra de navegación superior con menú desplegable para Analíticas"""
    
    # Submenú desplegable para Analíticas
    analytics_dropdown = dbc.DropdownMenu(
        children=[
            dbc.DropdownMenuItem("General", href="/dashboard/analytics/general"),
            dbc.DropdownMenuItem("Nivel de Actividad", href="/dashboard/analytics/actividad"),
            dbc.DropdownMenuItem("Participantes", href="/dashboard/analytics/participantes"),
            dbc.DropdownMenuItem("Preguntas", href="/dashboard/analytics/preguntas"),
        ],
        nav=True,
        in_navbar=True,
        label="Analíticas",
    )
    
    navbar = dbc.NavbarSimple(
        brand="Mi Dashboard",
        color="primary",
        dark=True,
        children=[
            dbc.NavItem(dbc.NavLink("Inicio", href="/dashboard/")),
            dbc.NavItem(analytics_dropdown),
            dbc.NavItem(dbc.NavLink("Configuración", href="/dashboard/settings")),
        ],
    )
    
    return navbar


def create_navbar_with_auth(username=None):
    """Crea la barra de navegación con información del usuario y botón de logout"""
    
    # Submenú desplegable para Analíticas
    analytics_dropdown = dbc.DropdownMenu(
        children=[
            dbc.DropdownMenuItem("General", href="/dashboard/analytics/general"),
            dbc.DropdownMenuItem("Nivel de Actividad", href="/dashboard/analytics/actividad"),
            dbc.DropdownMenuItem("Participantes", href="/dashboard/analytics/participantes"),
            dbc.DropdownMenuItem("Preguntas", href="/dashboard/analytics/preguntas"),
        ],
        nav=True,
        in_navbar=True,
        label="Analíticas",
    )
    
    navbar = dbc.Navbar(
        dbc.Container([
            # Logo/Brand
            dbc.NavbarBrand("Mi Dashboard", href="/dashboard/"),
            
            # Toggler para móviles
            dbc.NavbarToggler(id="navbar-toggler"),
            
            # Contenido colapsable
            dbc.Collapse(
                dbc.Row([
                    # Navegación principal
                    dbc.Col(
                        dbc.Nav([
                            dbc.NavItem(dbc.NavLink("Inicio", href="/dashboard/")),
                            dbc.NavItem(analytics_dropdown),
                            dbc.NavItem(dbc.NavLink("Configuración", href="/dashboard/settings")),
                        ], navbar=True),
                        width="auto"
                    ),
                    
                    # Información del usuario y logout
                    dbc.Col(
                        dbc.Nav([
                            dbc.NavItem(
                                html.Span([
                                    html.I(className="fas fa-user me-2"),
                                    username or "Usuario"
                                ], className="navbar-text text-light me-3")
                            ),
                            dbc.NavItem(
                                dbc.Button(
                                    [
                                        html.I(className="fas fa-sign-out-alt me-2"),
                                        "Cerrar Sesión"
                                    ],
                                    id="logout-button",
                                    color="danger",
                                    size="sm",
                                    className="ms-2",
                                    n_clicks=0
                                )
                            ),
                        ], navbar=True, className="ms-auto"),
                        width="auto"
                    ),
                ], className="flex-grow-1 justify-content-between"),
                id="navbar-collapse",
                navbar=True,
            ),
        ], fluid=True),
        color="primary",
        dark=True,
        className="mb-0"
    )
    
    return navbar


def create_sidebar():
    """Crea el menú lateral con el desplegable de Analíticas"""
    
    sidebar = html.Div(
        [
            html.H2("Menú", className="bg-secondary text-white p-2 mb-4"),
            html.Hr(),
            dbc.Nav(
                [
                    dbc.NavLink("Inicio", href="/dashboard/", active="exact"),
                    # Grupo de Analíticas con submenús
                    html.Div(
                        [
                            html.P("Analíticas", className="text-muted mb-2 mt-3"),
                            dbc.Nav(
                                [
                                    dbc.NavLink("General", href="/dashboard/analytics/general", 
                                              active="exact", className="ms-3"),
                                    dbc.NavLink("Nivel de Actividad", href="/dashboard/analytics/actividad", 
                                              active="exact", className="ms-3"),
                                    dbc.NavLink("Participantes", href="/dashboard/analytics/participantes", 
                                              active="exact", className="ms-3"),
                                    dbc.NavLink("Preguntas", href="/dashboard/analytics/preguntas", 
                                              active="exact", className="ms-3"),
                                ],
                                vertical=True,
                                pills=True,
                            ),
                        ]
                    ),
                    dbc.NavLink("Configuración", href="/dashboard/settings", active="exact", className="mt-3"),
                    html.Hr(),
                    dbc.NavLink("C.R.U.D. Preguntas", href="/dashboard/settings/preguntas", active="exact"),
                    dbc.NavLink("C.R.U.D Estudiantes", href="/dashboard/settings/estudiantes", active="exact"),
                ],
                vertical=True,
                pills=True,
            ),
        ],
        style={
            "position": "fixed", 
            "top": 56, 
            "left": 0, 
            "bottom": 0, 
            "width": "16rem", 
            "padding": "2rem 1rem", 
            "background-color": "#f8f9fa"
        },
    )
    
    return sidebar