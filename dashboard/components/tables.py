from dash import dash_table
import dash_bootstrap_components as dbc
from dash import html


def create_styled_datatable(df, columns, table_id, page_size=20, row_selectable=False):
    """
    Crea una DataTable estilizada y consistente
    
    Args:
        df: DataFrame con los datos
        columns: Lista de diccionarios con la configuración de columnas
        table_id: ID único para la tabla
        page_size: Número de filas por página
        row_selectable: Si las filas son seleccionables ('single', 'multi', False)
    
    Returns:
        dash_table.DataTable configurada
    """
    
    return dash_table.DataTable(
        id=table_id,
        columns=columns,
        data=df.to_dict('records'),
        sort_action="native",
        filter_action="native",
        page_action="native",
        page_size=page_size,
        row_selectable=row_selectable,
        style_table={
            'overflowX': 'auto',
            'minWidth': '100%'
        },
        style_cell={
            'textAlign': 'left',
            'padding': '12px',
            'fontSize': '14px',
            'fontFamily': 'Arial, sans-serif'
        },
        style_header={
            'backgroundColor': 'rgb(248, 249, 250)',
            'fontWeight': 'bold',
            'textAlign': 'center',
            'border': '1px solid #dee2e6'
        },
        style_data={
            'border': '1px solid #dee2e6',
            'backgroundColor': 'white'
        },
        style_data_conditional=[
            {
                'if': {'row_index': 'odd'},
                'backgroundColor': 'rgb(248, 249, 250)'
            }
        ],
        style_filter={
            'backgroundColor': 'white',
            'border': '1px solid #dee2e6'
        }
    )


def create_summary_table(data_dict, title="Resumen"):
    """
    Crea una tabla de resumen con pares clave-valor
    
    Args:
        data_dict: Diccionario con los datos a mostrar
        title: Título de la tabla
    
    Returns:
        dbc.Card con la tabla de resumen
    """
    
    rows = []
    for key, value in data_dict.items():
        rows.append(
            html.Tr([
                html.Td(key, className="fw-bold"),
                html.Td(value, className="text-end")
            ])
        )
    
    return dbc.Card([
        dbc.CardHeader(title),
        dbc.CardBody([
            dbc.Table([
                html.Tbody(rows)
            ], striped=True, hover=True, responsive=True, size="sm")
        ])
    ])


def create_metric_card(value, label, color="primary", icon=None, footer=None):
    """
    Crea una tarjeta de métrica individual
    
    Args:
        value: Valor principal a mostrar
        label: Etiqueta descriptiva
        color: Color de Bootstrap (primary, success, warning, etc.)
        icon: Icono opcional (como clase CSS)
        footer: Texto opcional para el pie de la tarjeta
    
    Returns:
        dbc.Card configurada
    """
    
    card_content = [
        html.H2(value, className="text-center mb-2"),
        html.P(label, className="text-center text-muted mb-0")
    ]
    
    if icon:
        card_content.insert(0, html.I(className=f"{icon} fa-3x mb-3", 
                                     style={"opacity": 0.3}))
    
    card = dbc.Card([
        dbc.CardBody(card_content)
    ], color=color, outline=True)
    
    if footer:
        card.children.append(
            dbc.CardFooter(footer, className="text-center small")
        )
    
    return card


def create_progress_bar(value, max_value=100, label="", color="primary", striped=True, animated=True):
    """
    Crea una barra de progreso
    
    Args:
        value: Valor actual
        max_value: Valor máximo
        label: Etiqueta a mostrar
        color: Color de Bootstrap
        striped: Si la barra debe tener rayas
        animated: Si las rayas deben estar animadas
    
    Returns:
        dbc.Progress configurado
    """
    
    return dbc.Progress(
        value=value,
        max=max_value,
        label=f"{label} ({value}/{max_value})" if label else f"{value}/{max_value}",
        color=color,
        striped=striped,
        animated=animated,
        className="mb-3"
    )


def create_comparison_table(df, metric_columns, label_column="label"):
    """
    Crea una tabla de comparación con barras de progreso
    
    Args:
        df: DataFrame con los datos
        metric_columns: Lista de columnas que contienen métricas
        label_column: Columna que contiene las etiquetas
    
    Returns:
        dbc.Table con visualización de comparación
    """
    
    rows = []
    for _, row in df.iterrows():
        cells = [html.Td(row[label_column], className="fw-bold")]
        
        for col in metric_columns:
            value = row[col]
            # Asumir que el valor es un porcentaje
            if isinstance(value, (int, float)):
                cells.append(
                    html.Td([
                        dbc.Progress(
                            value=value,
                            max=100,
                            label=f"{value:.1f}%",
                            color=get_color_by_value(value),
                            style={"height": "20px"}
                        )
                    ])
                )
            else:
                cells.append(html.Td(value))
        
        rows.append(html.Tr(cells))
    
    headers = [html.Th(label_column.replace('_', ' ').title())]
    headers.extend([html.Th(col.replace('_', ' ').title()) for col in metric_columns])
    
    return dbc.Table([
        html.Thead([html.Tr(headers)]),
        html.Tbody(rows)
    ], striped=True, hover=True, responsive=True)


def get_color_by_value(value, thresholds=None):
    """
    Determina el color basado en el valor y umbrales
    
    Args:
        value: Valor numérico
        thresholds: Dict con umbrales {danger: 30, warning: 60, success: 80}
    
    Returns:
        String con el color de Bootstrap
    """
    
    if thresholds is None:
        thresholds = {"danger": 30, "warning": 60, "success": 80}
    
    if value < thresholds["danger"]:
        return "danger"
    elif value < thresholds["warning"]:
        return "warning"
    elif value < thresholds["success"]:
        return "info"
    else:
        return "success"