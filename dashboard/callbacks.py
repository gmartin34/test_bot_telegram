from dash import Input, Output, html, dcc
from dashboard.components.navbar import create_navbar_with_auth, create_sidebar
from dashboard.auth.auth_utils import is_authenticated, get_current_user


def register_callbacks(app):
    """Registra todos los callbacks de la aplicación"""
    
    @app.callback(
        [Output("page-content", "children"),
         Output("navbar-container", "children"),
         Output("sidebar-container", "children")],
        Input("url", "pathname")
    )
    def display_page(pathname):
        print(101, "Ruta solicitadaXXXXXXXXXXXXXXXXXXXXXXXXXXXX:", pathname)
        """Callback principal para manejar la navegación entre páginas"""

        # Páginas de autenticación (sin navbar ni sidebar)
        if pathname == "/dashboard/login":
            print(102, "Cargando página de loginXXXXXXXXXXXXXXXXXXXXXX")
            from dashboard.components.login import create_login_page
            return create_login_page(), html.Div(), html.Div()
        
        elif pathname == "/dashboard/forgot-password":
            from dashboard.components.forgot_password import create_forgot_password_page
            return create_forgot_password_page(), html.Div(), html.Div()
        
        elif pathname == "/dashboard/reset-password":
            from dashboard.components.reset_password import create_reset_password_page
            return create_reset_password_page(), html.Div(), html.Div()
        
        # Páginas protegidas (con navbar y sidebar)
        # Verificar autenticación
        if not is_authenticated():
            return dcc.Location(pathname="/dashboard/login", id="redirect"), html.Div(), html.Div()
        
        # Obtener usuario actual para el navbar
        current_user = get_current_user()
        navbar = create_navbar_with_auth(current_user)
        sidebar = create_sidebar()
        
        # Página de inicio
        if pathname == "/dashboard/" or pathname == "/dashboard":
            content = html.Div([
                html.Div(
                    className="card",
                    children=[
                        html.Div(
                            className="text-center card-header",
                            children=[
                                html.H2("Panel del Docente"),
                            ]
                        ),
                        html.Div(
                            className="card-body text-center",
                            children=[
                                html.H1("UNED", className="display-3 mb-4"),
                                html.P(
                                    f"Bienvenido {current_user} al panel de control del Trivial UNED",
                                    className="lead"
                                ),
                                html.Hr(),
                                html.Div(
                                    className="row mt-5",
                                    children=[
                                        html.Div(
                                            className="col-md-3",
                                            children=[
                                                html.Div(
                                                    className="card text-center mb-3",
                                                    children=[
                                                        html.Div(
                                                            className="card-body",
                                                            children=[
                                                                html.H5("Analíticas", className="card-title"),
                                                                html.P("Accede a las estadísticas detalladas", 
                                                                      className="card-text"),
                                                                html.A("Ir a General", 
                                                                      href="/dashboard/analytics/general",
                                                                      className="btn btn-primary")
                                                            ]
                                                        )
                                                    ]
                                                )
                                            ]
                                        ),
                                        html.Div(
                                            className="col-md-3",
                                            children=[
                                                html.Div(
                                                    className="card text-center mb-3",
                                                    children=[
                                                        html.Div(
                                                            className="card-body",
                                                            children=[
                                                                html.H5("Actividad", className="card-title"),
                                                                html.P("Monitorea el nivel de actividad", 
                                                                      className="card-text"),
                                                                html.A("Ver Actividad", 
                                                                      href="/dashboard/analytics/actividad",
                                                                      className="btn btn-info")
                                                            ]
                                                        )
                                                    ]
                                                )
                                            ]
                                        ),
                                        html.Div(
                                            className="col-md-3",
                                            children=[
                                                html.Div(
                                                    className="card text-center mb-3",
                                                    children=[
                                                        html.Div(
                                                            className="card-body",
                                                            children=[
                                                                html.H5("Participantes", className="card-title"),
                                                                html.P("Gestiona los participantes", 
                                                                      className="card-text"),
                                                                html.A("Ver Participantes", 
                                                                      href="/dashboard/analytics/participantes",
                                                                      className="btn btn-success")
                                                            ]
                                                        )
                                                    ]
                                                )
                                            ]
                                        ),
                                        html.Div(
                                            className="col-md-3",
                                            children=[
                                                html.Div(
                                                    className="card text-center mb-3",
                                                    children=[
                                                        html.Div(
                                                            className="card-body",
                                                            children=[
                                                                html.H5("Preguntas", className="card-title"),
                                                                html.P("Analiza las preguntas", 
                                                                      className="card-text"),
                                                                html.A("Ver Preguntas", 
                                                                      href="/dashboard/analytics/preguntas",
                                                                      className="btn btn-warning")
                                                            ]
                                                        )
                                                    ]
                                                )
                                            ]
                                        )
                                    ]
                                )
                            ]
                        )
                    ]
                )
            ])
            
            return content, navbar, sidebar
        
        # Páginas de analíticas
        elif pathname == "/dashboard/analytics/general":
            from dashboard.components.general import create_general_content
            return create_general_content(), navbar, sidebar
            
        elif pathname == "/dashboard/analytics/actividad":
            from dashboard.components.nivel_actividad import create_nivel_actividad_content
            return create_nivel_actividad_content(), navbar, sidebar
            
        elif pathname == "/dashboard/analytics/participantes":
            from dashboard.components.participantes import create_participantes_content
            return create_participantes_content(), navbar, sidebar
            
        elif pathname == "/dashboard/analytics/preguntas":
            from dashboard.components.preguntas import create_preguntas_content
            return create_preguntas_content(), navbar, sidebar
            
        elif pathname == "/dashboard/settings":
            return html.Div([
                html.H2("Configuración"),
                html.P("Opciones de configuración del dashboard...")
            ]), navbar, sidebar
            
        elif pathname == "/dashboard/settings/preguntas":
            from dashboard.components.crud_preguntas import create_crud_preguntas_content
            return create_crud_preguntas_content(), navbar, sidebar
        
        elif pathname == "/dashboard/settings/estudiantes":
            from dashboard.components.crud_estudiantes import create_crud_estudiantes_content
            return create_crud_estudiantes_content(), navbar, sidebar
        
        # Página 404
        else:
            return html.Div([
                html.H1("404: Página no encontrada", className="text-danger"),
                html.P(f"La ruta '{pathname}' no existe."),
                html.A("Volver al inicio", href="/dashboard/", className="btn btn-primary")
            ]), navbar, sidebar