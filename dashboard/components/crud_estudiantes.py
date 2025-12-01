from dash import html, dcc, dash_table, Input, Output, State, callback, no_update, ALL
import dash_bootstrap_components as dbc
from dashboard.data.estudiantes_queries import (
    get_estudiantes_pendientes,
    get_estudiantes_activos,
    aprobar_estudiante,
    cambiar_estado_estudiante
)

def create_crud_estudiantes_content():
    """Crea el contenido del CRUD de estudiantes"""
    print("Creando contenido de CRUD Estudiantes")

    content = html.Div([
        # Header
        dbc.Card([
            dbc.CardHeader([
                html.H2("C.R.U.D. Estudiantes", className="text-center mb-0"),
                html.P("Gestión de estudiantes del sistema", className="text-center text-muted mb-0")
            ]),
            dbc.CardBody([
                # Botón de actualizar
                dbc.Button(
                    [html.I(className="bi bi-arrow-clockwise me-2"), "Actualizar"],
                    id="refresh-estudiantes-btn",
                    color="primary",
                    size="sm",
                    className="mb-3"
                ),
                
                # Primera sección: Estudiantes pendientes
                dbc.Card([
                    dbc.CardHeader([
                        html.H4("Estudiantes Pendientes de Aprobación", className="mb-0"),
                        html.P("Estudiantes que han solicitado ingresar al juego", className="text-muted mb-0 small")
                    ], className="bg-warning text-dark"),
                    dbc.CardBody([
                        html.Div(id="tabla-pendientes-container")
                    ])
                ], className="mb-4"),
                
                # Segunda sección: Estudiantes activos
                dbc.Card([
                    dbc.CardHeader([
                        html.H4("Estudiantes Registrados", className="mb-0"),
                        html.P("Gestión de estudiantes activos y dados de baja", className="text-muted mb-0 small")
                    ], className="bg-info text-white"),
                    dbc.CardBody([
                        html.Div(id="tabla-activos-container")
                    ])
                ])
            ])
        ]),
        
        # Modal de confirmación
        dbc.Modal([
            dbc.ModalHeader(dbc.ModalTitle("Confirmar Acción")),
            dbc.ModalBody(id="modal-confirm-body"),
            dbc.ModalFooter([
                dbc.Button("Cancelar", id="modal-cancel", color="secondary", className="ms-auto"),
                dbc.Button("Confirmar", id="modal-confirm", color="primary")
            ])
        ], id="confirm-modal", is_open=False),
        
        # Store para datos temporales
        dcc.Store(id="temp-action-data"),
        
        # ← AÑADIR: Store para estados iniciales de los estudiantes
        dcc.Store(id="student-states-store", data={}),
        
        # Div para notificaciones
        html.Div(id="notification-estudiantes")
    ])
    
    return content


@callback(
    [Output('tabla-pendientes-container', 'children'),
     Output('tabla-activos-container', 'children'),
     Output('student-states-store', 'data')],  
    Input('refresh-estudiantes-btn', 'n_clicks'),
    Input('notification-estudiantes', 'children')
)     
def refresh_tables(n_clicks, notification):
    """Actualiza las tablas de estudiantes"""
    
    # Obtener datos
    df_pendientes = get_estudiantes_pendientes()
    print("DF Pendientes:", df_pendientes)
    df_activos = get_estudiantes_activos()
    
    # Crear diccionario con estados actuales
    states_dict = {}
    if not df_activos.empty:
        states_dict = {row['id']: row['state'] for _, row in df_activos.iterrows()}
    
    # Crear tabla de pendientes
    if df_pendientes.empty:
        tabla_pendientes = html.P("No hay estudiantes pendientes de aprobación", 
                                 className="text-muted text-center p-3")
    else:
        tabla_pendientes = create_tabla_pendientes(df_pendientes)
    
    # Crear tabla de activos
    if df_activos.empty:
        tabla_activos = html.P("No hay estudiantes registrados", 
                              className="text-muted text-center p-3")
    else:
        tabla_activos = create_tabla_activos(df_activos)
    
    return tabla_pendientes, tabla_activos, states_dict  # ← RETORNAR ESTADOS


def create_tabla_pendientes(df):
    """Crea la tabla de estudiantes pendientes"""
    rows = []
    for idx, row in df.iterrows():
        rows.append(
            html.Tr([
                html.Td(row['id']),
                html.Td(row['name']),
                html.Td(row['email']),
                html.Td(row['fecha_registro'].strftime('%d/%m/%Y %H:%M') if row['fecha_registro'] else 'N/A'),
                html.Td([
                    dbc.Button(
                        "Aceptar",
                        id={"type": "aprobar-btn", "index": row['id']},
                        color="success",
                        size="sm"
                    )
                ])
            ])
        )
    
    return dbc.Table([
        html.Thead([
            html.Tr([
                html.Th("ID"),
                html.Th("Nombre"),
                html.Th("Email"),
                html.Th("Fecha Registro"),
                html.Th("Acción")
            ])
        ]),
        html.Tbody(rows)
    ], striped=True, hover=True, responsive=True)


def create_tabla_activos(df):
    """Crea la tabla de estudiantes activos"""
    rows = []
    for idx, row in df.iterrows():
        # Determinar el color del badge según el estado
        if row['state'] == 'A':
            badge_color = "success"
            badge_text = "Activo"
        elif row['state'] == 'B':
            badge_color = "danger"
            badge_text = "Baja"
        else:
            badge_color = "warning"
            badge_text = "Pendiente"
        
        rows.append(
            html.Tr([
                html.Td(row['id']),
                html.Td(row['name']),
                html.Td(row['email']),
                html.Td([
                    dbc.Badge(badge_text, color=badge_color)
                ]),
                html.Td(row['preguntas_respondidas'] or 0),
                html.Td(f"{row['porcentaje_acierto']:.1f}%" if row['porcentaje_acierto'] else "0%"),
                html.Td(row['ultima_actividad'].strftime('%d/%m/%Y') if row['ultima_actividad'] else 'Sin actividad'),
                html.Td([
                    dbc.Select(
                        id={"type": "cambiar-estado", "index": row['id']},
                        options=[
                            {"label": "Activo", "value": "A"},
                            {"label": "Baja", "value": "B"}
                        ],
                        value=row['state'],
                        size="sm"
                    )
                ])
            ])
        )
    
    return dbc.Table([
        html.Thead([
            html.Tr([
                html.Th("ID"),
                html.Th("Nombre"),
                html.Th("Email"),
                html.Th("Estado"),
                html.Th("Preguntas"),
                html.Th("% Acierto"),
                html.Th("Última Actividad"),
                html.Th("Cambiar Estado")
            ])
        ]),
        html.Tbody(rows)
    ], striped=True, hover=True, responsive=True, size="sm")

@callback(
    [Output('confirm-modal', 'is_open'),
     Output('modal-confirm-body', 'children'),
     Output('temp-action-data', 'data')],
    [Input({"type": "aprobar-btn", "index": ALL}, 'n_clicks'),
     Input({"type": "cambiar-estado", "index": ALL}, 'value')],
    [State({"type": "aprobar-btn", "index": ALL}, 'id'),
     State({"type": "cambiar-estado", "index": ALL}, 'id'),
     State('student-states-store', 'data')],  # ← USAR STORE EN LUGAR DE cambiar_states
    prevent_initial_call=True
)
def show_confirmation(aprobar_clicks, cambiar_values, aprobar_ids, cambiar_ids, stored_states):
    import json
    from dash import callback_context

    ctx = callback_context
    print("DEBUG show_confirmation ctx.triggered:", ctx.triggered)

    if not ctx.triggered:
        return False, "", None

    # Tomar solo el trigger real
    triggered = ctx.triggered[0]
    prop_id = triggered.get('prop_id')
    if not prop_id:
        return False, "", None

    trigger_part = prop_id.split('.')[0]
    try:
        trigger_id = json.loads(trigger_part)
    except Exception:
        trigger_id = None

    # Botón aprobar
    if trigger_id and trigger_id.get("type") == "aprobar-btn":
        student_id = trigger_id.get("index")
        # Verificar que el click no sea None
        idx = next((i for i, id_dict in enumerate(aprobar_ids) if id_dict.get("index") == student_id), None)
        if idx is not None and aprobar_clicks[idx] is None:
            return False, "", None
        
        return True, f"¿Está seguro de aprobar al estudiante ID {student_id}?", {
            "action": "aprobar",
            "student_id": student_id
        }

    # Select cambiar-estado
    if trigger_id and trigger_id.get("type") == "cambiar-estado":
        student_id = trigger_id.get("index")
        
        # Obtener el índice del estudiante
        idx = next((i for i, id_dict in enumerate(cambiar_ids) if id_dict.get("index") == student_id), None)
        if idx is None:
            return False, "", None
        
        # Obtener nuevo valor del select
        nuevo_valor = cambiar_values[idx] if idx < len(cambiar_values) else None
        
        # ← OBTENER VALOR ORIGINAL DEL STORE
        valor_original = stored_states.get(str(student_id))  # Convertir a string por si acaso
        
        print(f"DEBUG student_id: {student_id}")
        print(f"DEBUG valor_original (store): {valor_original}")
        print(f"DEBUG nuevo_valor: {nuevo_valor}")
        
        # Verificar que realmente haya cambiado
        if nuevo_valor == valor_original or nuevo_valor is None:
            print(f"DEBUG: No hay cambio real")
            return False, "", None
        
        estado_texto = "Activo" if nuevo_valor == "A" else "Baja"
        return True, f"¿Está seguro de cambiar el estado del estudiante ID {student_id} a {estado_texto}?", {
            "action": "cambiar_estado",
            "student_id": student_id,
            "nuevo_estado": nuevo_valor
        }

    return False, "", None
@callback(
    [Output('notification-estudiantes', 'children', allow_duplicate=True),
     Output('confirm-modal', 'is_open', allow_duplicate=True)],
    [Input('modal-confirm', 'n_clicks'),
     Input('modal-cancel', 'n_clicks')],
    State('temp-action-data', 'data'),
    prevent_initial_call=True
)
def handle_confirmation(confirm_clicks, cancel_clicks, action_data):
    """Maneja la confirmación de acciones"""
    from dash import callback_context
    ctx = callback_context
    
    if not ctx.triggered:
        return no_update, False
    
    trigger_id = ctx.triggered[0]['prop_id']
    
    if 'modal-cancel' in trigger_id:
        return no_update, False
    
    if 'modal-confirm' in trigger_id and action_data:
        if action_data['action'] == 'aprobar':
            if aprobar_estudiante(action_data['student_id']):
                notification = dbc.Alert(
                    f"Estudiante ID {action_data['student_id']} aprobado exitosamente",
                    color="success",
                    dismissable=True,
                    duration=3000
                )
            else:
                notification = dbc.Alert(
                    "Error al aprobar estudiante",
                    color="danger",
                    dismissable=True,
                    duration=3000
                )
        
        elif action_data['action'] == 'cambiar_estado':
            if cambiar_estado_estudiante(action_data['student_id'], action_data['nuevo_estado']):
                estado_texto = "Activo" if action_data['nuevo_estado'] == "A" else "Baja"
                notification = dbc.Alert(
                    f"Estado del estudiante ID {action_data['student_id']} cambiado a {estado_texto}",
                    color="success",
                    dismissable=True,
                    duration=3000
                )
            else:
                notification = dbc.Alert(
                    "Error al cambiar estado del estudiante",
                    color="danger",
                    dismissable=True,
                    duration=3000
                )
        
        return notification, False
    
    return no_update, False