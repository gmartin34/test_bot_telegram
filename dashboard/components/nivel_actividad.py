from dash import html, dcc, dash_table, Input, Output, callback
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import pandas as pd

from dashboard.data.actividad_queries import (
    get_actividad_por_periodo,
    get_distribucion_actividad_periodo,
    get_evolucion_diaria_mes,
    get_comparacion_meses,
    get_estadisticas_detalladas_periodo
)
from dashboard.utils.date_utils import get_last_n_months, get_month_names


def create_nivel_actividad_content():
    """Crea el contenido de la vista de Nivel de Actividad"""
    
    # Obtener lista de meses para el selector
    meses_disponibles = get_last_n_months(12)
    mes_actual = datetime.now()
    valor_inicial = f"{mes_actual.year}-{mes_actual.month:02d}"
    
    # Contenido principal
    content = html.Div([
        # Header con selector de mes
        dbc.Card([
            dbc.CardHeader([
                dbc.Row([
                    dbc.Col([
                        html.H2("Nivel de Actividad", className="mb-0"),
                        html.P("Análisis temporal de la participación", className="text-muted mb-0")
                    ], md=8),
                    dbc.Col([
                        html.Label("Seleccionar período:", className="me-2"),
                        dcc.Dropdown(
                            id='selector-mes',
                            options=[{'label': m['name'], 'value': m['value']} for m in meses_disponibles],
                            value=valor_inicial,
                            clearable=False,
                            style={'width': '200px'}
                        )
                    ], md=4, className="text-end")
                ], align="center")
            ]),
            dbc.CardBody([
                # Contenedor para las métricas principales
                html.Div(id='metricas-periodo'),
                
                # Gráficos principales
                dbc.Row([
                    dbc.Col([
                        dbc.Card([
                            dbc.CardHeader("Distribución por Nivel de Actividad"),
                            dbc.CardBody([
                                dcc.Graph(id='grafico-distribucion-actividad')
                            ])
                        ])
                    ], md=6),
                    dbc.Col([
                        dbc.Card([
                            dbc.CardHeader("Tabla de Niveles de Actividad"),
                            dbc.CardBody([
                                html.Div(id='tabla-distribucion-actividad')
                            ])
                        ])
                    ], md=6)
                ], className="mb-4"),
                
                # Evolución diaria
                dbc.Row([
                    dbc.Col([
                        dbc.Card([
                            dbc.CardHeader("Evolución Diaria del Mes"),
                            dbc.CardBody([
                                dcc.Graph(id='grafico-evolucion-diaria')
                            ])
                        ])
                    ], md=12)
                ], className="mb-4"),
                
                # Comparación histórica
                dbc.Row([
                    dbc.Col([
                        dbc.Card([
                            dbc.CardHeader("Comparación Últimos 6 Meses"),
                            dbc.CardBody([
                                dcc.Graph(id='grafico-comparacion-meses')
                            ])
                        ])
                    ], md=12)
                ], className="mb-4"),
                
                # Estadísticas adicionales
                html.Div(id='estadisticas-adicionales')
            ])
        ])
    ])
    
    return content


@callback(
    [Output('metricas-periodo', 'children'),
     Output('grafico-distribucion-actividad', 'figure'),
     Output('tabla-distribucion-actividad', 'children'),
     Output('grafico-evolucion-diaria', 'figure'),
     Output('grafico-comparacion-meses', 'figure'),
     Output('estadisticas-adicionales', 'children')],
    Input('selector-mes', 'value')
)
def update_nivel_actividad(periodo_seleccionado):
    """Actualiza todos los componentes cuando se selecciona un nuevo período"""
    
    # Parsear el período seleccionado
    año, mes = map(int, periodo_seleccionado.split('-'))
    nombre_mes = get_month_names()[mes]
    
    # Obtener datos
    actividad_periodo = get_actividad_por_periodo(mes, año)
    distribucion, df_detalle = get_distribucion_actividad_periodo(mes, año)
    evolucion_diaria = get_evolucion_diaria_mes(mes, año)
    comparacion_meses = get_comparacion_meses()
    stats_detalladas = get_estadisticas_detalladas_periodo(mes, año)
    
    # 1. Crear métricas principales
    metricas = dbc.Row([
        dbc.Col([
            dbc.Alert([
                html.H4(f"{actividad_periodo['preguntas_esperadas']:,}", className="alert-heading"),
                html.P("Preguntas Esperadas", className="mb-0"),
                html.Hr(),
                html.P(f"Para {actividad_periodo['total_participantes']} participantes", 
                      className="mb-0 small")
            ], color="primary")
        ], md=3),
        dbc.Col([
            dbc.Alert([
                html.H4(f"{actividad_periodo['preguntas_respondidas']:,}", className="alert-heading"),
                html.P("Preguntas Respondidas", className="mb-0"),
                html.Hr(),
                html.P(f"En {actividad_periodo['dias_periodo']} días", 
                      className="mb-0 small")
            ], color="info")
        ], md=3),
        dbc.Col([
            dbc.Alert([
                html.H4(f"{actividad_periodo['indicador_actividad']:.1f}%", className="alert-heading"),
                html.P("Indicador Global de Actividad", className="mb-0"),
                html.Hr(),
                html.P(
                    "Excelente" if actividad_periodo['indicador_actividad'] >= 70
                    else "Bueno" if actividad_periodo['indicador_actividad'] >= 50
                    else "Regular" if actividad_periodo['indicador_actividad'] >= 30
                    else "Bajo",
                    className="mb-0 small text-center fw-bold"
                )
            ], color=get_color_by_percentage(actividad_periodo['indicador_actividad']))
        ], md=3),
        dbc.Col([
            dbc.Alert([
                html.H4(f"{stats_detalladas['nuevos_participantes']}", className="alert-heading"),
                html.P("Nuevos Participantes", className="mb-0"),
                html.Hr(),
                html.P(f"En {nombre_mes}", className="mb-0 small")
            ], color="success")
        ], md=3)
    ], className="mb-4")
    
    # 2. Gráfico de distribución (dona)
    fig_distribucion = px.pie(
        distribucion,
        values='cantidad',
        names='nivel',
        hole=0.4,
        color='nivel',
        color_discrete_map={
            'Muy activo': '#28a745',
            'Activo': '#17a2b8',
            'Poco activo': '#ffc107',
            'Inactivo': '#dc3545'
        }
    )
    fig_distribucion.update_traces(
        textposition='inside',
        textinfo='percent+label'
    )
    fig_distribucion.update_layout(
        showlegend=True,
        height=400
    )
    
    # 3. Tabla de distribución
    tabla_distribucion = dbc.Table([
        html.Thead([
            html.Tr([
                html.Th("Nivel de Actividad"),
                html.Th("Criterio", className="text-center"),
                html.Th("Participantes", className="text-center"),
                html.Th("Porcentaje", className="text-center")
            ])
        ]),
        html.Tbody([
            html.Tr([
                html.Td([
                    html.Span("● ", style={'color': get_color_nivel(row['nivel']), 'fontSize': '20px'}),
                    row['nivel']
                ]),
                html.Td(get_criterio_nivel(row['nivel']), className="text-center small"),
                html.Td(row['cantidad'], className="text-center"),
                html.Td(f"{row['porcentaje']:.1f}%", className="text-center")
            ]) for _, row in distribucion.iterrows()
        ])
    ], striped=True, hover=True)
    
    # 4. Gráfico de evolución diaria
    if not evolucion_diaria.empty:
        fig_evolucion = go.Figure()
        
        # Línea de participantes activos
        fig_evolucion.add_trace(go.Scatter(
            x=evolucion_diaria['dia'],
            y=evolucion_diaria['participantes_activos'],
            mode='lines+markers',
            name='Participantes Activos',
            line=dict(color='#007bff', width=2),
            marker=dict(size=8)
        ))
        
        # Barras de respuestas totales
        fig_evolucion.add_trace(go.Bar(
            x=evolucion_diaria['dia'],
            y=evolucion_diaria['total_respuestas'],
            name='Respuestas Totales',
            marker_color='lightblue',
            yaxis='y2',
            opacity=0.6
        ))
        
        fig_evolucion.update_layout(
            title=f"Actividad Diaria - {nombre_mes} {año}",
            xaxis_title="Día del Mes",
            yaxis_title="Participantes Activos",
            yaxis2=dict(
                title="Respuestas Totales",
                overlaying='y',
                side='right'
            ),
            hovermode='x unified',
            height=400
        )
    else:
        fig_evolucion = go.Figure()
        fig_evolucion.add_annotation(
            text="Sin datos para el período seleccionado",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False
        )
    
    # 5. Gráfico de comparación de meses
    if not comparacion_meses.empty:
        fig_comparacion = go.Figure()
        
        # Barras de participantes únicos
        fig_comparacion.add_trace(go.Bar(
            x=comparacion_meses['periodo'],
            y=comparacion_meses['participantes_unicos'],
            name='Participantes Únicos',
            marker_color='#17a2b8'
        ))
        
        # Línea de porcentaje de acierto
        fig_comparacion.add_trace(go.Scatter(
            x=comparacion_meses['periodo'],
            y=comparacion_meses['porcentaje_acierto'],
            mode='lines+markers',
            name='% Acierto',
            yaxis='y2',
            line=dict(color='#28a745', width=3),
            marker=dict(size=10)
        ))
        
        fig_comparacion.update_layout(
            title="Tendencia de Actividad - Últimos 6 Meses",
            xaxis_title="Mes",
            yaxis_title="Participantes Únicos",
            yaxis2=dict(
                title="% Acierto",
                overlaying='y',
                side='right',
                range=[0, 100]
            ),
            hovermode='x unified',
            height=400
        )
    else:
        fig_comparacion = go.Figure()
    
    # 6. Estadísticas adicionales
    estadisticas_adicionales = dbc.Card([
        dbc.CardHeader(f"Estadísticas Detalladas - {nombre_mes} {año}"),
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    html.H6("Participación", className="text-muted"),
                    html.P([
                        html.Strong(f"{stats_detalladas['participantes_activos']}"),
                        " participantes activos"
                    ]),
                    html.P([
                        html.Strong(f"{stats_detalladas['preguntas_unicas']}"),
                        " preguntas diferentes respondidas"
                    ])
                ], md=3),
                dbc.Col([
                    html.H6("Rendimiento", className="text-muted"),
                    html.P([
                        html.Strong(f"{stats_detalladas['porcentaje_acierto_primero']:.1f}%"),
                        " acierto en primer intento"
                    ]),
                    html.P([
                        html.Strong(f"{stats_detalladas['promedio_intentos']:.2f}"),
                        " intentos promedio por pregunta"
                    ])
                ], md=3),
                dbc.Col([
                    html.H6("Actividad", className="text-muted"),
                    html.P([
                        html.Strong(f"{stats_detalladas['total_respuestas']:,}"),
                        " respuestas totales"
                    ]),
                    html.P([
                        html.Strong(f"{stats_detalladas['asignaturas_activas']}"),
                        " asignaturas con actividad"
                    ])
                ], md=3),
                dbc.Col([
                    html.H6("Promedio Diario", className="text-muted"),
                    html.P([
                        html.Strong(
                            f"{stats_detalladas['total_respuestas'] / actividad_periodo['dias_periodo']:.0f}"
                        ),
                        " respuestas por día"
                    ]),
                    html.P([
                        html.Strong(
                            f"{stats_detalladas['participantes_activos'] / actividad_periodo['dias_periodo']:.1f}"
                        ),
                        " participantes activos por día"
                    ])
                ], md=3)
            ])
        ])
    ])
    
    return (metricas, fig_distribucion, tabla_distribucion, 
            fig_evolucion, fig_comparacion, estadisticas_adicionales)


def get_color_by_percentage(percentage):
    """Determina el color basado en el porcentaje"""
    if percentage >= 70:
        return "success"
    elif percentage >= 50:
        return "info"
    elif percentage >= 30:
        return "warning"
    else:
        return "danger"


def get_color_nivel(nivel):
    """Retorna el color para cada nivel de actividad"""
    colores = {
        'Muy activo': '#28a745',
        'Activo': '#17a2b8',
        'Poco activo': '#ffc107',
        'Inactivo': '#dc3545'
    }
    return colores.get(nivel, '#6c757d')


def get_criterio_nivel(nivel):
    """Retorna el criterio para cada nivel de actividad"""
    criterios = {
        'Muy activo': '≥ 70% de las preguntas',
        'Activo': '≥ 50% y < 70%',
        'Poco activo': '> 0% y < 50%',
        'Inactivo': '0% de las preguntas'
    }
    return criterios.get(nivel, '')