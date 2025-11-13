from dashboard.utils.db_utils import execute_query, execute_query_df, execute_scalar
from dashboard.auth.auth_utils import hash_password, verify_password, generate_token
from datetime import datetime, timedelta


def verify_user_credentials(username, password):
    """
    Verifica las credenciales del usuario
    
    Returns:
        dict con información del usuario si las credenciales son correctas, None si no
    """
    query = """
    SELECT id, username, password_hash, email, role, is_active, last_login
    FROM dashboard_users
    WHERE username = %s AND is_active = 1
    """
    
    result = execute_query(query, (username,))
    
    if result and len(result) > 0:
        user = result[0]
        user_dict = {
            'id': user[0],
            'username': user[1],
            'password_hash': user[2],
            'email': user[3],
            'role': user[4],
            'is_active': user[5],
            'last_login': user[6]
        }
        
        # Verificar contraseña
        if verify_password(password, user_dict['password_hash']):
            # Actualizar último login
            update_last_login(user_dict['id'])
            return user_dict
    
    return None


def update_last_login(user_id):
    """
    Actualiza la fecha de último login del usuario
    """
    query = """
    UPDATE dashboard_users 
    SET last_login = %s 
    WHERE id = %s
    """
    
    from database.db_connection import db_connection
    db = db_connection()
    cursor = db.cursor()
    
    try:
        cursor.execute(query, (datetime.now(), user_id))
        db.commit()
    except Exception as e:
        print(f"Error actualizando último login: {e}")
        db.rollback()
    finally:
        cursor.close()
        db.close()


def get_user_by_email(email):
    """
    Obtiene un usuario por su email
    """
    query = """
    SELECT id, username, email, is_active
    FROM dashboard_users
    WHERE email = %s
    """
    
    result = execute_query(query, (email,))
    
    if result and len(result) > 0:
        return {
            'id': result[0][0],
            'username': result[0][1],
            'email': result[0][2],
            'is_active': result[0][3]
        }
    
    return None


def create_password_reset_token(user_id):
    """
    Crea un token de recuperación de contraseña
    """
    token = generate_token(64)
    expiry = datetime.now() + timedelta(hours=1)
    
    # Primero, invalidar tokens anteriores
    invalidate_query = """
    UPDATE password_reset_tokens 
    SET is_used = 1 
    WHERE user_id = %s AND is_used = 0
    """
    
    # Crear nuevo token
    insert_query = """
    INSERT INTO password_reset_tokens (user_id, token, expiry_date, is_used)
    VALUES (%s, %s, %s, 0)
    """
    
    from database.db_connection import db_connection
    db = db_connection()
    cursor = db.cursor()
    
    try:
        cursor.execute(invalidate_query, (user_id,))
        cursor.execute(insert_query, (user_id, token, expiry))
        db.commit()
        return token
    except Exception as e:
        print(f"Error creando token de recuperación: {e}")
        db.rollback()
        return None
    finally:
        cursor.close()
        db.close()


def verify_reset_token(token):
    """
    Verifica si un token de recuperación es válido
    
    Returns:
        dict con información del token si es válido, None si no
    """
    query = """
    SELECT t.id, t.user_id, t.expiry_date, u.username, u.email
    FROM password_reset_tokens t
    JOIN dashboard_users u ON t.user_id = u.id
    WHERE t.token = %s AND t.is_used = 0 AND t.expiry_date > %s
    """
    
    result = execute_query(query, (token, datetime.now()))
    
    if result and len(result) > 0:
        return {
            'token_id': result[0][0],
            'user_id': result[0][1],
            'expiry_date': result[0][2],
            'username': result[0][3],
            'email': result[0][4]
        }
    
    return None


def update_user_password(user_id, new_password):
    """
    Actualiza la contraseña de un usuario
    """
    password_hash = hash_password(new_password)
    
    query = """
    UPDATE dashboard_users 
    SET password_hash = %s, updated_at = %s
    WHERE id = %s
    """
    
    from database.db_connection import db_connection
    db = db_connection()
    cursor = db.cursor()
    
    try:
        cursor.execute(query, (password_hash, datetime.now(), user_id))
        db.commit()
        return True
    except Exception as e:
        print(f"Error actualizando contraseña: {e}")
        db.rollback()
        return False
    finally:
        cursor.close()
        db.close()


def mark_token_as_used(token_id):
    """
    Marca un token como usado
    """
    query = """
    UPDATE password_reset_tokens 
    SET is_used = 1, used_at = %s
    WHERE id = %s
    """
    
    from database.db_connection import db_connection
    db = db_connection()
    cursor = db.cursor()
    
    try:
        cursor.execute(query, (datetime.now(), token_id))
        db.commit()
    except Exception as e:
        print(f"Error marcando token como usado: {e}")
        db.rollback()
    finally:
        cursor.close()
        db.close()


def get_all_users():
    """
    Obtiene todos los usuarios del sistema
    """
    query = """
    SELECT id, username, email, role, is_active, created_at, last_login
    FROM dashboard_users
    ORDER BY created_at DESC
    """
    
    return execute_query_df(query)


def create_user(username, password, email, role='viewer'):
    """
    Crea un nuevo usuario
    """
    password_hash = hash_password(password)
    
    query = """
    INSERT INTO dashboard_users (username, password_hash, email, role, is_active, created_at)
    VALUES (%s, %s, %s, %s, 1, %s)
    """
    
    from database.db_connection import db_connection
    db = db_connection()
    cursor = db.cursor()
    
    try:
        cursor.execute(query, (username, password_hash, email, role, datetime.now()))
        db.commit()
        return True
    except Exception as e:
        print(f"Error creando usuario: {e}")
        db.rollback()
        return False
    finally:
        cursor.close()
        db.close()