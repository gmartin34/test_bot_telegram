from datetime import datetime, timedelta
import calendar
import pandas as pd


def get_month_names():
    """Retorna un diccionario con los nombres de los meses en español"""
    return {
        1: 'Enero', 2: 'Febrero', 3: 'Marzo', 4: 'Abril',
        5: 'Mayo', 6: 'Junio', 7: 'Julio', 8: 'Agosto',
        9: 'Septiembre', 10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre'
    }


def get_current_month_year():
    """Retorna el mes y año actual"""
    now = datetime.now()
    return now.month, now.year


def get_month_date_range(month, year):
    """
    Retorna el primer y último día del mes especificado
    
    Args:
        month: Número del mes (1-12)
        year: Año
    
    Returns:
        tuple: (fecha_inicio, fecha_fin)
    """
    first_day = datetime(year, month, 1)
    last_day = datetime(year, month, calendar.monthrange(year, month)[1])
    return first_day, last_day


def get_last_n_months(n=12):
    """
    Retorna una lista de los últimos n meses
    
    Returns:
        list: Lista de tuplas (mes, año, nombre_mes)
    """
    months = []
    current_date = datetime.now()
    
    for i in range(n):
        date = current_date - timedelta(days=30*i)
        month_name = get_month_names()[date.month]
        months.append({
            'month': date.month,
            'year': date.year,
            'name': f"{month_name} {date.year}",
            'value': f"{date.year}-{date.month:02d}"
        })
    
    return months[::-1]  # Invertir para tener orden cronológico


def get_week_date_range(weeks_ago=0):
    """
    Retorna el rango de fechas para una semana específica
    
    Args:
        weeks_ago: Número de semanas atrás (0 = semana actual)
    
    Returns:
        tuple: (fecha_inicio, fecha_fin)
    """
    today = datetime.now().date()
    start_of_week = today - timedelta(days=today.weekday() + 7*weeks_ago)
    end_of_week = start_of_week + timedelta(days=6)
    return start_of_week, end_of_week


def format_date_range(start_date, end_date):
    """
    Formatea un rango de fechas para mostrar
    
    Args:
        start_date: Fecha de inicio
        end_date: Fecha de fin
    
    Returns:
        str: Rango formateado
    """
    if isinstance(start_date, str):
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
    if isinstance(end_date, str):
        end_date = datetime.strptime(end_date, '%Y-%m-%d')
    
    return f"{start_date.strftime('%d/%m/%Y')} - {end_date.strftime('%d/%m/%Y')}"


def calculate_days_between(date1, date2):
    """
    Calcula los días entre dos fechas
    
    Args:
        date1: Primera fecha
        date2: Segunda fecha
    
    Returns:
        int: Número de días
    """
    if isinstance(date1, str):
        date1 = datetime.strptime(date1, '%Y-%m-%d')
    if isinstance(date2, str):
        date2 = datetime.strptime(date2, '%Y-%m-%d')
    
    return abs((date2 - date1).days)


def get_days_in_month(month, year):
    """Retorna el número de días en un mes específico"""
    return calendar.monthrange(year, month)[1]


def is_weekend(date):
    """Determina si una fecha es fin de semana"""
    if isinstance(date, str):
        date = datetime.strptime(date, '%Y-%m-%d')
    return date.weekday() >= 5


def get_business_days_in_month(month, year):
    """Calcula los días laborables en un mes"""
    days_in_month = get_days_in_month(month, year)
    business_days = 0
    
    for day in range(1, days_in_month + 1):
        date = datetime(year, month, day)
        if not is_weekend(date):
            business_days += 1
    
    return business_days


def group_by_period(df, date_column, period='month'):
    """
    Agrupa un DataFrame por período de tiempo
    
    Args:
        df: DataFrame con datos
        date_column: Nombre de la columna de fecha
        period: 'day', 'week', 'month', 'year'
    
    Returns:
        DataFrame agrupado
    """
    df[date_column] = pd.to_datetime(df[date_column])
    
    if period == 'day':
        df['period'] = df[date_column].dt.date
    elif period == 'week':
        df['period'] = df[date_column].dt.to_period('W')
    elif period == 'month':
        df['period'] = df[date_column].dt.to_period('M')
    elif period == 'year':
        df['period'] = df[date_column].dt.to_period('Y')
    
    return df