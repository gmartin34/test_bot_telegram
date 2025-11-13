from dash import html, dcc, dash_table
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from dashboard.data.participantes_queries import (
    get_datos_participantes,
    get_resumen_participantes,
    get_distribucion_actividad,
    get_top_participantes
)

from dashboard.components.tables import create_metric_card


def create_participantes_content():
    """Crea el contenido de la vista de Participantes"""
    
    # Obtener datos
    df_participantes = get_datos_participantes()
    resumen = get_resumen_participantes()
    df_distribucion = get_distribucion_actividad()
    top_participantes = get_top_participantes()
    
    # Preparar columnas para la tabla principal
    tabla_columns = [
        {"name": "Nombre", "id": "nombre", "type": "text"},
        {"name": "Progreso", "id": "progreso", "type": "text"},
        {"name": "Actividad", "id": "actividad", "type": "text"},
        {"name": "Preguntas Respondidas", "id": "preguntas_respondidas", "type": "numeric"},
        {"name": "% Completado", "id": "porcentaje_completado", "type": "numeric", "format": {"specifier": ".1f"}},
        {"name": "% Acierto 1er Intento", "id": "porcentaje_primer_intento", "type": "numeric", "format": {"specifier": ".1f"}},
        {"name": "% Acierto 2do Intento", "id": "porcentaje_segundo_intento", "type": "numeric", "format": {"specifier": ".1f"}},
        {"name": "Diferencia %", "id": "diferencia_porcentajes", "type": "numeric", "format": {"specifier": ".1f"}},
        {"name": "Preguntas Retiradas", "id": "preguntas_retiradas", "type": "numeric"},
        {"name": "Días Inactivo", "id": "dias_inactivo", "type": "numeric"}
    ]
    
    # Crear gráfico de distribución de progreso
    df_progreso = df_participantes['progreso'].value_counts().reset_index()
    df_progreso.columns = ['progreso', 'cantidad']
    
    fig_progreso = px.pie(
        df_progreso,
        values='cantidad',
        names='progreso',
        color='progreso',
        color_discrete_map={
            'Completado': '#28a745',
            'Progresando': '#17a2b8',
            'Riesgo de abandono': '#ffc107',
            'No ha comenzado': '#dc3545'
        },
        title="Distribución por Estado de Progreso"
    )
    
    # Crear gráfico de barras para distribución de actividad
    fig_actividad = go.Figure()
    
    # Ordenar los niveles de actividad
    orden_actividad = ['Muy activo', 'Activo', 'Poco activo', 'Inactivo']
    df_distribucion['actividad'] = pd.Categorical(
        df_distribucion['actividad'], 
        categories=orden_actividad, 
        ordered=True
    )
    df_distribucion = df_distribucion.sort_values('actividad')
    
    fig_actividad.add_trace(go.Bar(
        x=df_distribucion['actividad'],
        y=df_distribucion['cantidad'],
        text=df_distribucion['porcentaje'].apply(lambda x: f'{x:.1f}%'),
        textposition='auto',
        marker_color=['#28a745', '#17a2b8', '#ffc107', '#dc3545']
    ))
    
    fig_actividad.update_layout(
        title="Distribución por Nivel de Actividad",
        xaxis_title="Nivel de Actividad",
        yaxis_title="Número de Participantes",
        showlegend=False
    )
    
    # Crear desempeño como texto formateado
    def crear_desempeno(row):
        return html.Div([
            html.Small([
                html.Span(f"1er: {row['porcentaje_primer_intento']:.1f}%", className="text-primary me-2"),
                html.Span(f"2do: {row['porcentaje_segundo_intento']:.1f}%", className="text-info me-2"),
                html.Span(f"Δ: {row['diferencia_porcentajes']:+.1f}%", 
                         className="text-success" if row['diferencia_porcentajes'] > 0 else "text-danger"),
                html.Br(),
                html.Span(f"Respondidas: {row['preguntas_respondidas']}/{row['total_preguntas']}", 
                         className="text-muted me-2"),
                html.Span(f"Retiradas: {row['preguntas_retiradas']}", className="text-muted")
            ])
        ])
    
    # Contenido principal
    content = html.Div([
        # Header
        dbc.Card([
            dbc.CardHeader([
                html.H2("Análisis de Participantes", className="text-center mb-0"),
                html.P("Información detallada de cada participante", className="text-center text-muted mb-0")
            ]),
            dbc.CardBody([
                # Primera fila - Métricas principales
                dbc.Row([
                    dbc.Col([
                        create_metric_card(
                            resumen['total_participantes'],
                            "Total Participantes",
                            color="primary",
                            footer=f"Activos: {resumen['participantes_activos']}"
                        )
                    ], md=2),
                    dbc.Col([
                        create_metric_card(
                            resumen['completado'],
                            "Completado",
                            color="success",
                            footer=f"{(resumen['completado']/resumen['total_participantes']*100):.1f}%"
                                  if resumen['total_participantes'] > 0 else "0%"
                        )
                    ], md=2),
                    dbc.Col([
                        create_metric_card(
                            resumen['total_participantes'] - resumen['completado'] - 
                            resumen['sin_comenzar'] - resumen['riesgo_abandono'],
                            "Progresando",
                            color="info",
                            footer="Activos últimos 7 días"
                        )
                    ], md=2),
                    dbc.Col([
                        create_metric_card(
                            resumen['riesgo_abandono'],
                            "Riesgo Abandono",
                            color="warning",
                            footer=">7 días inactivos"
                        )
                    ], md=2),
                    dbc.Col([
                        create_metric_card(
                            resumen['sin_comenzar'],
                            "Sin Comenzar",
                            color="danger",
                            footer="Registrados pero inactivos"
                        )
                    ], md=2),
                    dbc.Col([
                        create_metric_card(
                            f"{resumen['promedio_acierto']:.1f}%",
                            "Promedio Acierto",
                            color="secondary",
                            footer="Primer intento"
                        )
                    ], md=2),
                ], className="mb-4"),
                
                # Segunda fila - Gráficos
                dbc.Row([
                    dbc.Col([
                        dbc.Card([
                            dbc.CardHeader("Estado de Progreso"),
                            dbc.CardBody([
                                dcc.Graph(
                                    figure=fig_progreso,
                                    config={'displayModeBar': False}
                                )
                            ])
                        ])
                    ], md=6),
                    dbc.Col([
                        dbc.Card([
                            dbc.CardHeader("Nivel de Actividad"),
                            dbc.CardBody([
                                dcc.Graph(
                                    figure=fig_actividad,
                                    config={'displayModeBar': False}
                                )
                            ])
                        ])
                    ], md=6)
                ], className="mb-4"),
                
                # Tercera fila - Rankings
                dbc.Row([
                    dbc.Col([
                        dbc.Card([
                            dbc.CardHeader("Top 10 - Mayor Progreso", className="bg-info text-white"),
                            dbc.CardBody([
                                crear_tabla_ranking(top_participantes['por_completadas'], 'completadas')
                            ])
                        ])
                    ], md=6),
                    dbc.Col([
                        dbc.Card([
                            dbc.CardHeader("Top 10 - Mejor Desempeño", className="bg-success text-white"),
                            dbc.CardBody([
                                crear_tabla_ranking(top_participantes['por_acierto'], 'acierto')
                            ])
                        ])
                    ], md=6)
                ], className="mb-4")
            ])
        ], className="mb-4"),
        
        # Tabla principal
        dbc.Card([
            dbc.CardHeader([
                html.H4("Detalle de Todos los Participantes", className="mb-0"),
                html.P("Tabla interactiva con información completa", className="text-muted mb-0 small")
            ]),
            dbc.CardBody([
                dash_table.DataTable(
                    id='tabla-participantes',
                    columns=tabla_columns,
                    data=df_participantes.to_dict('records'),
                    sort_action="native",
                    filter_action="native",
                    page_action="native",
                    page_size=15,
                    style_table={'overflowX': 'auto'},
                    style_cell={
                        'textAlign': 'left',
                        'padding': '10px',
                        'fontSize': '14px'
                    },
                    style_header={
                        'backgroundColor': 'rgb(230, 230, 230)',
                        'fontWeight': 'bold'
                    },
                    style_data_conditional=[
                        # Colores para progreso
                        {
                            'if': {'filter_query': '{progreso} = "Completado"'},
                            'backgroundColor': '#d4edda',
                            'color': 'black',
                        },
                        {
                            'if': {'filter_query': '{progreso} = "Progresando"'},
                            'backgroundColor': '#d1ecf1',
                            'color': 'black',
                        },
                        {
                            'if': {'filter_query': '{progreso} = "Riesgo de abandono"'},
                            'backgroundColor': '#fff3cd',
                            'color': 'black',
                        },
                        {
                            'if': {'filter_query': '{progreso} = "No ha comenzado"'},
                            'backgroundColor': '#f8d7da',
                            'color': 'black',
                        },
                        # Colores para actividad
                        {
                            'if': {'column_id': 'actividad', 'filter_query': '{actividad} = "Muy activo"'},
                            'color': '#28a745',
                            'fontWeight': 'bold'
                        },
                        {
                            'if': {'column_id': 'actividad', 'filter_query': '{actividad} = "Inactivo"'},
                            'color': '#dc3545',
                            'fontWeight': 'bold'
                        },
                        # Resaltar buenos resultados
                        {
                            'if': {
                                'filter_query': '{porcentaje_primer_intento} > 70',
                                'column_id': 'porcentaje_primer_intento'
                            },
                            'color': 'green',
                            'fontWeight': 'bold'
                        },
                        {
                            'if': {
                                'filter_query': '{diferencia_porcentajes} > 10',
                                'column_id': 'diferencia_porcentajes'
                            },
                            'color': 'green',
                            'fontWeight': 'bold'
                        }
                    ],
                    export_format='csv',
                    export_headers='display'
                ),
                html.Div([
                    html.Small("Nota: Puede exportar los datos usando el botón 'Export' en la esquina superior derecha de la tabla", 
                              className="text-muted mt-2")
                ])
            ])
        ])
    ])
    
    return content


def crear_tabla_ranking(df, tipo):
    """Crea una tabla simple para mostrar rankings"""
    if df.empty:
        return html.P("No hay datos suficientes", className="text-muted")
    
    if tipo == 'completadas':
        headers = ["#", "Nombre", "Preguntas", "%"]
        rows = []
        for idx, row in df.iterrows():
            rows.append(html.Tr([
                html.Td(idx + 1),
                html.Td(row['name']),
                html.Td(row['preguntas_respondidas']),
                html.Td(f"{row['porcentaje_completado']:.1f}%")
            ]))
    else:  # acierto
        headers = ["#", "Nombre", "Respuestas", "% Acierto"]
        rows = []
        for idx, row in df.iterrows():
            rows.append(html.Tr([
                html.Td(idx + 1),
                html.Td(row['name']),
                html.Td(row['total_respuestas']),
                html.Td(f"{row['porcentaje_acierto']:.1f}%")
            ]))
    
    return dbc.Table([
        html.Thead([
            html.Tr([html.Th(h) for h in headers])
        ]),
        html.Tbody(rows)
    ], striped=True, hover=True, size="sm")