from dash import html, dcc, dash_table
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
from dashboard.data.preguntas_queries import (
    get_estadisticas_preguntas, 
    get_resumen_preguntas,
    get_preguntas_por_asignatura,
    get_top_preguntas_faciles_dificiles
)


def create_preguntas_content():
    """Crea el contenido de la vista de Preguntas"""
    
    # Obtener datos
    df_preguntas = get_estadisticas_preguntas()
    resumen = get_resumen_preguntas()
    df_asignaturas = get_preguntas_por_asignatura()
    top_preguntas = get_top_preguntas_faciles_dificiles()
    
    # Preparar datos para la tabla principal
    tabla_columns = [
        {"name": "ID", "id": "id_pregunta", "type": "numeric"},
        {"name": "Pregunta", "id": "pregunta", "type": "text"},
        {"name": "Asignatura", "id": "asignatura", "type": "text"},
        {"name": "Nivel", "id": "nivel", "type": "numeric"},
        {"name": "Participantes", "id": "participantes_respondieron", "type": "numeric"},
        {"name": "Total Intentos", "id": "total_intentos", "type": "numeric"},
        {"name": "Media Intentos", "id": "media_intentos", "type": "numeric", "format": {"specifier": ".2f"}},
        {"name": "Veces Retirada", "id": "veces_retirada", "type": "numeric"},
        {"name": "% Acierto 1er", "id": "porcentaje_acierto_primero", "type": "numeric", "format": {"specifier": ".1f"}},
        {"name": "% Acierto 2do", "id": "porcentaje_acierto_segundo", "type": "numeric", "format": {"specifier": ".1f"}},
        {"name": "Diferencia %", "id": "diferencia_porcentajes", "type": "numeric", "format": {"specifier": ".1f"}},
        {"name": "Dificultad", "id": "dificultad", "type": "text"}
    ]
    
    # Crear gráfico de distribución de dificultad
    if not df_preguntas.empty:
        df_dificultad = df_preguntas['dificultad'].value_counts().reset_index()
        df_dificultad.columns = ['dificultad', 'cantidad']
        
        fig_dificultad = px.pie(
            df_dificultad, 
            values='cantidad', 
            names='dificultad',
            color='dificultad',
            color_discrete_map={
                'Fácil': '#28a745',
                'Media': '#ffc107',
                'Difícil': '#dc3545'
            },
            title="Distribución por Dificultad"
        )
    else:
        fig_dificultad = go.Figure()
        fig_dificultad.add_annotation(
            text="Sin datos disponibles",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False
        )
    
    # Crear gráfico de preguntas por asignatura
    if not df_asignaturas.empty:
        fig_asignaturas = go.Figure()
        fig_asignaturas.add_trace(go.Bar(
            x=df_asignaturas['asignatura'],
            y=df_asignaturas['total_preguntas'],
            name='Total Preguntas',
            marker_color='lightblue'
        ))
        fig_asignaturas.add_trace(go.Bar(
            x=df_asignaturas['asignatura'],
            y=df_asignaturas['preguntas_respondidas'],
            name='Respondidas',
            marker_color='darkblue'
        ))
        fig_asignaturas.update_layout(
            title="Preguntas por Asignatura",
            xaxis_title="Asignatura",
            yaxis_title="Número de Preguntas",
            barmode='group',
            height=400
        )
    else:
        fig_asignaturas = go.Figure()
        fig_asignaturas.add_annotation(
            text="Sin datos disponibles",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False
        )
    
    # Contenido principal
    content = html.Div([
        # Header
        dbc.Card([
            dbc.CardHeader([
                html.H2("Análisis de Preguntas", className="text-center mb-0"),
                html.P("Estadísticas detalladas preguntas", className="text-center text-muted mb-0")
            ]),
            dbc.CardBody([
                # Primera fila - Resumen
                dbc.Row([
                    dbc.Col([
                        dbc.Alert([
                            html.H4(resumen['total_preguntas'], className="alert-heading"),
                            html.P("Total Preguntas", className="mb-0"),
                            html.Hr(),
                            html.P(f"Activas: {resumen['preguntas_respondidas']}", className="mb-0 small")
                        ], color="primary")
                    ], md=3),
                    dbc.Col([
                        dbc.Alert([
                            html.H4(resumen['preguntas_sin_responder'], className="alert-heading"),
                            html.P("Sin Responder", className="mb-0"),
                            html.Hr(),
                            html.P(f"{(resumen['preguntas_sin_responder']/resumen['total_preguntas']*100):.1f}% del total" 
                                  if resumen['total_preguntas'] > 0 else "0% del total", 
                                  className="mb-0 small")
                        ], color="warning")
                    ], md=3),
                    dbc.Col([
                        dbc.Alert([
                            html.H4(f"{resumen['promedio_acierto_primero']:.1f}%", className="alert-heading"),
                            html.P("Promedio Acierto 1er Intento", className="mb-0"),
                            html.Hr(),
                            html.P("Global del sistema", className="mb-0 small")
                        ], color="success")
                    ], md=3),
                    dbc.Col([
                        dbc.Alert([
                            html.H4(f"{resumen['promedio_intentos']:.2f}", className="alert-heading"),
                            html.P("Media de Intentos", className="mb-0"),
                            html.Hr(),
                            html.P("Por pregunta", className="mb-0 small")
                        ], color="info")
                    ], md=3),
                ], className="mb-4"),
                
                # Segunda fila - Gráficos
                dbc.Row([
                    dbc.Col([
                        dbc.Card([
                            dbc.CardHeader("Distribución por Dificultad"),
                            dbc.CardBody([
                                dcc.Graph(
                                    figure=fig_dificultad,
                                    config={'displayModeBar': False}
                                )
                            ])
                        ])
                    ], md=6),
                    dbc.Col([
                        dbc.Card([
                            dbc.CardHeader("Preguntas por Asignatura"),
                            dbc.CardBody([
                                dcc.Graph(
                                    figure=fig_asignaturas,
                                    config={'displayModeBar': False}
                                )
                            ])
                        ])
                    ], md=6)
                ], className="mb-4"),
                
                # Tercera fila - Top preguntas
                dbc.Row([
                    dbc.Col([
                        dbc.Card([
                            dbc.CardHeader("Top 5 Preguntas Más Fáciles", className="bg-success text-white"),
                            dbc.CardBody([
                                crear_tabla_top_preguntas(top_preguntas['faciles'], 'faciles')
                            ])
                        ])
                    ], md=6),
                    dbc.Col([
                        dbc.Card([
                            dbc.CardHeader("Top 5 Preguntas Más Difíciles", className="bg-danger text-white"),
                            dbc.CardBody([
                                crear_tabla_top_preguntas(top_preguntas['dificiles'], 'dificiles')
                            ])
                        ])
                    ], md=6)
                ], className="mb-4")
            ])
        ], className="mb-4"),
        
        # Tabla principal
        dbc.Card([
            dbc.CardHeader([
                html.H4("Detalle de Todas las Preguntas", className="mb-0"),
                html.P("Haga clic en los encabezados para ordenar", className="text-muted mb-0 small")
            ]),
            dbc.CardBody([
                dash_table.DataTable(
                    id='tabla-preguntas',
                    columns=tabla_columns,
                    data=df_preguntas.to_dict('records'),
                    sort_action="native",
                    filter_action="native",
                    page_action="native",
                    page_size=20,
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
                        {
                            'if': {'filter_query': '{dificultad} = "Fácil"'},
                            'backgroundColor': '#d4edda',
                            'color': 'black',
                        },
                        {
                            'if': {'filter_query': '{dificultad} = "Media"'},
                            'backgroundColor': '#fff3cd',
                            'color': 'black',
                        },
                        {
                            'if': {'filter_query': '{dificultad} = "Difícil"'},
                            'backgroundColor': '#f8d7da',
                            'color': 'black',
                        },
                        {
                            'if': {'filter_query': '{diferencia_porcentajes} > 10'},
                            'color': 'green',
                            'fontWeight': 'bold'
                        }
                    ],
                    style_cell_conditional=[
                        {
                            'if': {'column_id': 'pregunta'},
                            'textAlign': 'left',
                            'maxWidth': '300px',
                            'overflow': 'hidden',
                            'textOverflow': 'ellipsis'
                        }
                    ]
                )
            ])
        ])
    ])
    
    return content


def crear_tabla_top_preguntas(df, tipo):
    """Crea una tabla simple para mostrar top preguntas"""
    if df.empty:
        return html.P("No hay datos suficientes", className="text-muted")
    
    color_class = "table-success" if tipo == 'faciles' else "table-danger"
    
    return dbc.Table([
        html.Thead([
            html.Tr([
                html.Th("#", style={"width": "10%"}),
                html.Th("Pregunta", style={"width": "50%"}),
                html.Th("Asignatura", style={"width": "25%"}),
                html.Th("% Acierto", style={"width": "15%"})
            ])
        ]),
        html.Tbody([
            html.Tr([
                html.Td(idx + 1),
                html.Td(row['pregunta'][:50] + "..." if len(row['pregunta']) > 50 else row['pregunta']),
                html.Td(row['asignatura']),
                html.Td(f"{row['porcentaje_acierto']:.1f}%")
            ]) for idx, row in df.iterrows()
        ])
    ], striped=True, hover=True, size="sm", className=color_class)