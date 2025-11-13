from dash import html, dcc, dash_table, Output, Input, State, ALL, callback, no_update
import dash_bootstrap_components as dbc
from dashboard.data.crud_queries import (
    create_question,
    delete_question,
    get_all_subjects,
    get_questions_by_subject
)


def create_crud_preguntas_content():
    """Crea el contenido principal del CRUD de preguntas"""
    
    # Obtener todas las asignaturas
    df_subjects = get_all_subjects()
    
    # Crear acordeón con las asignaturas
    accordion_items = []
    for idx, subject in df_subjects.iterrows():
        accordion_items.append(
            dbc.AccordionItem(
                create_subject_content(subject),
                title=f"{subject['faculty']} - {subject['name']}",
                item_id=f"subject-{subject['id']}"
            )
        )
    
    content = html.Div([
        # Header
        dbc.Card([
            dbc.CardHeader([
                html.H2("C.R.U.D. Preguntas", className="text-center mb-0"),
                html.P("Gestión de preguntas por asignatura", className="text-center text-muted mb-0")
            ])
        ], className="mb-4"),
        
        # Acordeón con asignaturas
        dbc.Accordion(
            accordion_items,
            id="subjects-accordion",
            start_collapsed=True
        ),
        
        # Modal para crear/editar preguntas
        dbc.Modal([
            dbc.ModalHeader(dbc.ModalTitle("", id="modal-title")),
            dbc.ModalBody([
                dbc.Form([
                    dbc.Row([
                        dbc.Col([
                            dbc.Label("Pregunta *"),
                            dbc.Input(id="input-question", type="text", required=True)
                        ], md=12)
                    ], className="mb-3"),
                    dbc.Row([
                        dbc.Col([
                            dbc.Label("Estado"),
                            dbc.Select(
                                id="input-state",
                                options=[
                                    {"label": "Activo", "value": "A"},
                                    {"label": "Inactivo", "value": "I"}
                                ],
                                value="A"
                            )
                        ], md=4),
                        dbc.Col([
                            dbc.Label("Nivel"),
                            dbc.Input(id="input-level", type="number", min=1, value=1)
                        ], md=4),
                        dbc.Col([
                            dbc.Label("Respuesta Correcta *"),
                            dbc.Select(
                                id="input-solution",
                                options=[
                                    {"label": "1", "value": "1"},
                                    {"label": "2", "value": "2"},
                                    {"label": "3", "value": "3"},
                                    {"label": "4", "value": "4"}
                                ],
                                required=True
                            )
                        ], md=4)
                    ], className="mb-3"),
                    dbc.Row([
                        dbc.Col([
                            dbc.Label("Respuesta 1 *"),
                            dbc.Input(id="input-answer1", type="text", required=True)
                        ], md=6),
                        dbc.Col([
                            dbc.Label("Respuesta 2 *"),
                            dbc.Input(id="input-answer2", type="text", required=True)
                        ], md=6)
                    ], className="mb-3"),
                    dbc.Row([
                        dbc.Col([
                            dbc.Label("Respuesta 3 *"),
                            dbc.Input(id="input-answer3", type="text", required=True)
                        ], md=6),
                        dbc.Col([
                            dbc.Label("Respuesta 4 *"),
                            dbc.Input(id="input-answer4", type="text", required=True)
                        ], md=6)
                    ], className="mb-3"),
                    dbc.Row([
                        dbc.Col([
                            dbc.Label("Explicación"),
                            dbc.Textarea(id="input-why", rows=3)
                        ], md=12)
                    ])
                ])
            ]),
            dbc.ModalFooter([
                dbc.Button("Cancelar", id="modal-cancel", className="ms-auto", color="secondary"),
                dbc.Button("Guardar", id="modal-save", color="primary")
            ])
        ], id="question-modal", size="lg", is_open=False),
        
        # Modal de confirmación para eliminar
        dbc.Modal([
            dbc.ModalHeader(dbc.ModalTitle("Confirmar Eliminación")),
            dbc.ModalBody("¿Está seguro de que desea eliminar esta pregunta?", id="delete-confirm-body"),
            dbc.ModalFooter([
                dbc.Button("Cancelar", id="delete-cancel", className="ms-auto", color="secondary"),
                dbc.Button("Eliminar", id="delete-confirm", color="danger")
            ])
        ], id="delete-modal", is_open=False),
        
        # Store para datos temporales
        dcc.Store(id="temp-question-data"),
        dcc.Store(id="temp-delete-data"),
        
        # Div para notificaciones
        html.Div(id="notification-container")
    ])
    
    return content

@callback(
    Output("question-modal", "is_open", allow_duplicate=True),
    Output("modal-title", "children", allow_duplicate=True),
    Output("temp-question-data", "data", allow_duplicate=True),
    Output("delete-modal", "is_open", allow_duplicate=True),
    Output("temp-delete-data", "data", allow_duplicate=True),
    Input({"type": "add-question-btn", "index": ALL}, "n_clicks"),
    Input({"type": "edit-btn", "index": ALL}, "n_clicks"),
    Input({"type": "delete-btn", "index": ALL}, "n_clicks"),
    Input("delete-cancel", "n_clicks"),
    State({"type": "add-question-btn", "index": ALL}, "id"),
    State({"type": "edit-btn", "index": ALL}, "id"),
    State({"type": "delete-btn", "index": ALL}, "id"),
    prevent_initial_call=True
)
def toggle_modal(add_clicks, edit_clicks, delete_clicks, cancel_click, add_ids, edit_ids, delete_ids):
    from dash import callback_context
    ctx = callback_context

    if not ctx.triggered:
        return False, "", None, False, None

    trigger_id = ctx.triggered[0]["prop_id"]

    import json

    if "modal-cancel" in trigger_id:
        return False, "", None, False, None

    if "add-question-btn" in trigger_id:
        button_id = json.loads(trigger_id.split(".")[0])
        subject_id = button_id["index"]
        return True, "Nueva Pregunta", {"subject_id": subject_id, "mode": "create"}, False, None

    if "edit-btn" in trigger_id:
        button_id = json.loads(trigger_id.split(".")[0])
        subject_id, question_id = button_id["index"].split("-")
        # Aquí puedes cargar los datos de la pregunta si lo necesitas
        return True, f"Editar Pregunta #{question_id}", {
            "subject_id": int(subject_id),
            "question_id": int(question_id),
            "mode": "edit"
        }, False, None

    if "delete-btn" in trigger_id:
        button_id = json.loads(trigger_id.split(".")[0])
        subject_id, question_id = button_id["index"].split("-")
        return False, "", None, True, {
            "subject_id": int(subject_id),
            "question_id": int(question_id)
        }

    return False, "", None, False, None


def create_subject_content(subject):
    """Crea el contenido para cada asignatura"""
    
    # Obtener preguntas de la asignatura con estadísticas
    df_questions = get_questions_by_subject(subject['id'])
    
    content = html.Div([
        # Header con toggle de estado
        dbc.Row([
            dbc.Col([
                html.P([
                    html.Strong("Total de preguntas: "),
                    f"{subject['total_questions']}"
                ], className="mb-0")
            ], md=8),
            dbc.Col([
                dbc.Label("Estado de la asignatura:", className="me-2"),
                dbc.Switch(
                    id={"type": "subject-toggle", "index": subject['id']},
                    value=subject['status'] == 'A',
                    label="Activa" if subject['status'] == 'A' else "Inactiva",
                    className="d-inline-block"
                )
            ], md=4, className="text-end")
        ], className="mb-3"),
        
        html.Hr(),
        
        # Botón para añadir nueva pregunta
        dbc.Button(
            [html.I(className="bi bi-plus-circle me-2"), "Nueva Pregunta"],
            id={"type": "add-question-btn", "index": subject['id']},
            color="success",
            size="sm",
            className="mb-3"
        ),
        
        # Contenedor de preguntas con scroll
        html.Div(
            id={"type": "questions-container", "index": subject['id']},
            children=create_questions_table(df_questions, subject['id']),
            style={
                "maxHeight": "400px",
                "overflowY": "auto",
                "border": "1px solid #dee2e6",
                "borderRadius": "0.25rem",
                "padding": "10px"
            }
        )
    ])
    
    return content

def create_questions_table(df_questions, subject_id):
    """Crea la tabla de preguntas mostrando todos los campos de la tabla questions"""
    if df_questions.empty:
        return html.P("No hay preguntas registradas para esta asignatura.", 
                     className="text-muted text-center p-3")
    
    rows = []
    for idx, row in df_questions.iterrows():
        row_class = "table-row-even" if idx % 2 == 0 else "table-row-odd"
        rows.append(
            html.Tr([
                html.Td(row['id']),
                html.Td(row['id_subject']),
                html.Td(row['state']),
                html.Td(row['level']),
                html.Td(row['question'], style={"maxWidth": "300px", "overflow": "hidden", "textOverflow": "ellipsis"}),
                html.Td(row['solution']),
                html.Td(row['why']),
                html.Td(row['answer1']),
                html.Td(row['answer2']),
                html.Td(row['answer3']),
                html.Td(row['answer4']),
                html.Td([
                    dbc.ButtonGroup([
                        dbc.Button(
                            html.I(className="bi bi-pencil"),
                            id={"type": "edit-btn", "index": f"{subject_id}-{row['id']}"},
                            color="primary",
                            size="sm",
                            className="me-1"
                        ),
                        dbc.Button(
                            html.I(className="bi bi-trash"),
                            id={"type": "delete-btn", "index": f"{subject_id}-{row['id']}"},
                            color="danger",
                            size="sm"
                        )
                    ])
                ])
            ], className=row_class)
        )
    
    table = dbc.Table([
        html.Thead([
            html.Tr([
                html.Th("ID"),
                html.Th("ID Subject"),
                html.Th("Estado"),
                html.Th("Nivel"),
                html.Th("Pregunta"),
                html.Th("Solución"),
                html.Th("Explicación"),
                html.Th("Respuesta 1"),
                html.Th("Respuesta 2"),
                html.Th("Respuesta 3"),
                html.Th("Respuesta 4"),
                html.Th("Acciones")
            ])
        ]),
        html.Tbody(rows)
    ], striped=True, hover=True, responsive=True, size="sm")
    
    return table
from dash import callback, Output, Input, State, ALL, no_update
import dash_bootstrap_components as dbc

@callback(
    Output("question-modal", "is_open"),
    Output("notification-container", "children", allow_duplicate=True),
    Input("modal-save", "n_clicks"),
    State("temp-question-data", "data"),
    State("input-question", "value"),
    State("input-state", "value"),
    State("input-level", "value"),
    State("input-solution", "value"),
    State("input-answer1", "value"),
    State("input-answer2", "value"),
    State("input-answer3", "value"),
    State("input-answer4", "value"),
    State("input-why", "value"),
    prevent_initial_call=True
)
def save_question(n_clicks, temp_data, question, state, level, solution, answer1, answer2, answer3, answer4, why):
    if not n_clicks:
        return no_update, no_update

    data = {
    "id_subject": temp_data.get("subject_id") if temp_data else None,
    "state": state,
    "level": level,
    "question": question,
    "solution": solution,
    "why": why,
    "answer1": answer1,
    "answer2": answer2,
    "answer3": answer3,
    "answer4": answer4,
    }

    success = create_question(data)

    if success:
        notification = dbc.Alert("Pregunta guardada correctamente", color="success", dismissable=True, duration=3000)
        return False, notification  # Cierra el modal y muestra mensaje
    else:
        notification = dbc.Alert("Error al guardar la pregunta", color="danger", dismissable=True, duration=3000)
        return no_update, notification
    

@callback(
    Output("delete-modal", "is_open"),
    Output("notification-container", "children", allow_duplicate=True),
    Input("delete-confirm", "n_clicks"),
    State("temp-delete-data", "data"),
    prevent_initial_call=True
)
def confirm_delete(n_clicks, delete_data):
    if not n_clicks or not delete_data:
        return no_update, no_update

    question_id = delete_data.get("question_id")
    success = delete_question(question_id)  

    if success:
        notification = dbc.Alert("Pregunta eliminada correctamente", color="success", dismissable=True, duration=3000)
        return False, notification  # Cierra el modal y muestra mensaje
    else:
        notification = dbc.Alert("Error al eliminar la pregunta", color="danger", dismissable=True, duration=3000)
        return no_update, notification
    