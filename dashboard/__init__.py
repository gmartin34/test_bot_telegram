import dash
import dash_bootstrap_components as dbc
from flask import redirect, request
from dashboard.components.layout import layout
from dashboard.callbacks import register_callbacks
from dashboard.auth.auth_callbacks import register_auth_callbacks
from dashboard.auth.auth_utils import is_authenticated


def create_dash_app(flask_app):
    """
    Crea y configura la aplicación Dash con autenticación
    
    Args:
        flask_app: Instancia de la aplicación Flask
    
    Returns:
        dash.Dash: Aplicación Dash configurada
    """
    
    # Configurar clave secreta para sesiones (cambiar en producción)
    flask_app.secret_key = 'uned-trivial-secret-key-change-in-production'
    
    dash_app = dash.Dash(
        server=flask_app,
        routes_pathname_prefix="/dashboard/",
        external_stylesheets=[
            dbc.themes.BOOTSTRAP,
            "https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.5/font/bootstrap-icons.css"
        ],
        suppress_callback_exceptions=True
    )
    
    # Agregar rutas de Flask para autenticación
    @flask_app.before_request
    def check_auth():
        """Verifica autenticación antes de cada request"""
        # Rutas que no requieren autenticación
        public_routes = [
            '/dashboard/login',
            '/dashboard/forgot-password',
            '/dashboard/reset-password',
            '/dashboard/_dash-component-suites/',
            '/dashboard/_dash-layout',
            '/dashboard/_dash-dependencies',
            '/dashboard/_favicon.ico',
            '/dashboard/assets/',
            '/dashboard/_dash-update-component',
            '/assets/',
        ]
        
        # Verificar si es una ruta pública
        is_public = any(request.path.startswith(route) for route in public_routes)
        
        # Si es una ruta del dashboard y no es pública, verificar autenticación
        if request.path.startswith('/dashboard/') and not is_public:
            print("Verificando autenticación para ruta:", request.path)
            if not is_authenticated():
                print("Usuario no autenticado, redirigiendo a login")
                return redirect('/dashboard/login')
    
    try:
        # Configurar el layout de Dash
        dash_app.layout = layout
        
        # Registrar todos los callbacks
        register_callbacks(dash_app)
        
        # Registrar callbacks de autenticación
        register_auth_callbacks(dash_app)

        # Registrar callbacks específicos de componentes
        from dashboard.components import crud_preguntas

        # Registrar callbacks específicos de componentes
        from dashboard.components import crud_estudiantes

        # Importar callbacks específicos de componentes
        from dashboard.components import nivel_actividad
        
        print("Dashboard configurado correctamente con autenticación")
        
    except Exception as e:
        print(f"Error al configurar el dashboard: {e}")
        raise

    return dash_app