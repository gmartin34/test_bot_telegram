from dash import html, dcc


# Layout principal de la aplicación
layout = html.Div([
    # URL para el routing
    dcc.Location(id="url", refresh=False),


    # Contenedor para el navbar (se llena dinámicamente)
    html.Div(id="navbar-container"),
    
    # Contenedor para el sidebar (se llena dinámicamente)
    html.Div(id="sidebar-container"),
    
    # Contenedor principal donde se renderiza el contenido dinámicamente
    html.Div(
        id="page-content",
        style={
            "margin-left": "18rem",
            "margin-right": "2rem",
            "padding": "2rem 1rem",
            "min-height": "100vh"
        }
    )
])