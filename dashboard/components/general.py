from dash import html, dcc
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
from dashboard.data.data_query import progreso_estudiantes
from dashboard.data.general_queries import get_actividad_mensual_anual, get_resumen_general


def create_general_content():
    """Crea el contenido de la vista General"""
    
    # Obtener datos
    data = progreso_estudiantes()
    df_mensual = get_actividad_mensual_anual()
    resumen = get_resumen_general()
    
    # Crear gráfico de pie para progreso
    fig_progreso = px.pie(
        data["dataframe"], 
        values='total_progreso', 
        names='progreso', 
        color='progreso',
        color_discrete_map={
            'Completado': '#28a745',
            'Sin empezar': '#dc3545',
            'En progreso': '#ffc107'
        },
        title="Estado de Progreso de Estudiantes"
    )
    fig_progreso.update_traces(textposition='inside', textinfo='percent+label')
    
    # Crear gráfico de barras para actividad mensual
    fig_mensual = go.Figure()
    fig_mensual.add_trace(go.Bar(
        x=df_mensual['mes_nombre'],
        y=df_mensual['preguntas_respondidas'],
        name='Preguntas Respondidas',
        marker_color='#007bff'
    ))
    
    fig_mensual.update_layout(
        title="Actividad Mensual - Año Actual",
        xaxis_title="Mes",
        yaxis_title="Número de Preguntas",
        showlegend=False,
        height=400
    )
    
    # Contenido principal
    content = html.Div([
        # Header
        dbc.Card([
            dbc.CardHeader([
                html.H2("UNED - Trivial", className="text-center mb-0"),
                html.P("Vista General del Sistema", className="text-center text-muted mb-0")
            ]),
            dbc.CardBody([
                # Primera fila - Estadísticas principales
                dbc.Row([
                    dbc.Col([
                        dbc.Alert([
                            html.H4(data["num_tot_est"], className="alert-heading"),
                            html.P("Participantes Totales", className="mb-0"),
                            html.Hr(),
                            html.P(f"Activos: {resumen['estudiantes_activos']}", className="mb-0 small")
                        ], color="primary")
                    ], md=3),
                    dbc.Col([
                        dbc.Alert([
                            html.H4(data["num_tot_pre"], className="alert-heading"),
                            html.P("Preguntas Disponibles", className="mb-0"),
                            html.Hr(),
                            html.P(f"Asignaturas: {resumen['asignaturas_activas']}", className="mb-0 small")
                        ], color="info")
                    ], md=3),
                    dbc.Col([
                        dbc.Alert([
                            html.H4(f"{data['por_acierto']:.1f}%", className="alert-heading"),
                            html.P("Tasa de Acierto Global", className="mb-0"),
                            html.Hr(),
                            html.P(f"Total intentos: {data['num_tot_attempts']:,}", className="mb-0 small")
                        ], color="success")
                    ], md=3),
                    dbc.Col([
                        dbc.Alert([
                            html.H4(f"{data['num_pri_bien_por']:.1f}%", className="alert-heading"),
                            html.P("Acierto Primer Intento", className="mb-0"),
                            html.Hr(),
                            html.P(f"Activos hoy: {resumen['activos_ultima_semana']}", className="mb-0 small")
                        ], color="warning")
                    ], md=3),
                ], className="mb-4"),
                
                # Segunda fila - Tabla de actividad detallada
                dbc.Row([
                    dbc.Col([
                        dbc.Card([
                            dbc.CardHeader("Resumen de Actividad"),
                            dbc.CardBody([
                                dbc.Table([
                                    html.Thead([
                                        html.Tr([
                                            html.Th("Métrica", style={"width": "50%"}),
                                            html.Th("Intentos", className="text-center"),
                                            html.Th("Aciertos", className="text-center")
                                        ])
                                    ]),
                                    html.Tbody([
                                        html.Tr([
                                            html.Td("Total Respuestas"),
                                            html.Td(f"{data['num_tot_attempts']:,}", className="text-center"),
                                            html.Td(f"{data['por_acierto']:.1f}%", className="text-center text-success")
                                        ]),
                                        html.Tr([
                                            html.Td("Primer Intento"),
                                            html.Td(f"{data['num_first_attempt']:,}", className="text-center"),
                                            html.Td(f"{data['num_pri_bien_por']:.1f}%", className="text-center text-info")
                                        ]),
                                        html.Tr([
                                            html.Td("Mejora en Segundo Intento"),
                                            html.Td("-", className="text-center"),
                                            html.Td(
                                                f"+{abs(data['por_acierto'] - data['num_pri_bien_por']):.1f}%", 
                                                className="text-center text-warning"
                                            )
                                        ])
                                    ])
                                ], striped=True, hover=True, size="sm")
                            ])
                        ])
                    ], md=12)
                ], className="mb-4")
            ])
        ], className="mb-4"),
        
        # Gráficos
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Distribución de Progreso"),
                    dbc.CardBody([
                        dcc.Graph(
                            id="progreso-pie-chart",
                            figure=fig_progreso,
                            config={'displayModeBar': False}
                        )
                    ])
                ])
            ], md=6),
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Actividad Mensual"),
                    dbc.CardBody([
                        dcc.Graph(
                            id="actividad-mensual-chart",
                            figure=fig_mensual,
                            config={'displayModeBar': False}
                        )
                    ])
                ])
            ], md=6)
        ])
    ])
    
    return content