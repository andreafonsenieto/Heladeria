"""
Base de datos SQLite para la Heladería.
Gestiona ventas con información de clima, temperatura, hora y fecha.
"""

import sqlite3
from pathlib import Path
import random
from datetime import date, datetime, timedelta

DB_PATH = Path(__file__).parent / "heladeria.db"


def get_connection():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Crea las tablas si no existen, migra columnas si faltan y agrega datos de ejemplo."""
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS ventas (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha       TEXT    NOT NULL,          -- YYYY-MM-DD
            hora        INTEGER DEFAULT 15,        -- 10 a 22 (hora del día)
            dia_semana  TEXT    NOT NULL,
            clima       TEXT    NOT NULL,          -- Soleado, Nublado, Lluvioso, etc.
            temperatura REAL,                      -- °C
            producto    TEXT    NOT NULL,
            cantidad    INTEGER NOT NULL,
            ingreso     REAL    NOT NULL
        )
    """)

    # Verificar si ya existe la columna 'hora'
    cur.execute("PRAGMA table_info(ventas)")
    columns = [col[1] for col in cur.fetchall()]
    if "hora" not in columns:
        cur.execute("ALTER TABLE ventas ADD COLUMN hora INTEGER DEFAULT 15")

    # Verificar si ya hay datos de ejemplo
    cur.execute("SELECT COUNT(*) FROM ventas")
    total_filas = cur.fetchone()[0]

    if total_filas == 0:
        _insertar_datos_ejemplo(cur)
    else:
        # Si las ventas existentes tienen hora en None o todas en 15, enriquecerlas con horas realistas
        cur.execute("SELECT COUNT(DISTINCT hora) FROM ventas WHERE hora IS NOT NULL")
        distinct_horas = cur.fetchone()[0]
        if distinct_horas <= 1:
            _enriquecer_horas_existentes(cur)

    conn.commit()
    conn.close()


def _calcular_temp_por_hora(temp_base, hora, clima):
    """Calcula la temperatura horaria realista según la curva solar del día."""
    # En la madrugada/mañana es más fresco, pico de calor entre 14h y 16h, baja al atardecer
    curva_solar = {
        10: -3.5, 11: -2.0, 12: -0.5,
        13: +1.5, 14: +3.0, 15: +3.5, 16: +2.8, 17: +1.2,
        18: -0.5, 19: -2.0, 20: -3.2, 21: -4.0, 22: -5.0
    }
    variacion = curva_solar.get(hora, 0.0)
    ruido = random.uniform(-0.8, 0.8)
    temp_hora = temp_base + variacion + ruido
    if clima == "Caluroso":
        temp_hora = max(27.0, temp_hora)
    elif clima == "Lluvioso":
        temp_hora = min(22.0, temp_hora)
    return round(max(14.0, min(38.0, temp_hora)), 1)


def _enriquecer_horas_existentes(cur):
    """Actualiza registros existentes que no tengan horas variadas."""
    cur.execute("SELECT id, clima, temperatura FROM ventas")
    filas = cur.fetchall()
    
    # Distribución horaria ponderada (mayor afluencia 14h-18h y 20h-21h)
    horas_posibles = [10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21]
    pesos_hora =     [ 2,  3,  5,  7, 12, 14, 13, 11,  9,  8,  9,  7]

    for fila in filas:
        h = random.choices(horas_posibles, weights=pesos_hora, k=1)[0]
        t_ajustada = _calcular_temp_por_hora(fila["temperatura"] or 24.0, h, fila["clima"])
        cur.execute("UPDATE ventas SET hora = ?, temperatura = ? WHERE id = ?", (h, t_ajustada, fila["id"]))


def _insertar_datos_ejemplo(cur):
    """Inserta ventas de ejemplo para los últimos 60 días con horas y temperaturas correlacionadas."""
    productos = ["Helado de Vainilla", "Helado de Chocolate", "Helado de Fresa",
                 "Sundae", "Malteada", "Copa de Frutas", "Paleta", "Cono Mixto"]
    climas = ["Soleado", "Parcialmente Nublado", "Nublado", "Lluvioso", "Caluroso"]
    dias_es = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]

    clima_factor = {
        "Soleado": 1.5,
        "Caluroso": 1.8,
        "Parcialmente Nublado": 1.0,
        "Nublado": 0.7,
        "Lluvioso": 0.4,
    }

    precios_base = {
        "Helado de Vainilla": 8000, "Helado de Chocolate": 8000,
        "Helado de Fresa": 8000, "Sundae": 12000,
        "Malteada": 15000, "Copa de Frutas": 10000,
        "Paleta": 5000, "Cono Mixto": 9000
    }

    horas_operacion = [10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21]
    # Picos en la tarde calurosa (14-17h) y post-cena (20-21h)
    pesos_hora =      [ 2,  3,  5,  7, 14, 15, 13, 10,  8,  7, 10,  6]

    today = date.today()
    rows = []

    for i in range(60):
        d = today - timedelta(days=i)
        clima = random.choice(climas)
        factor = clima_factor[clima]
        dia_idx = d.weekday()
        finde_factor = 1.4 if dia_idx >= 5 else 1.0

        # Base diaria de temperatura según clima
        if clima == "Caluroso":
            temp_base_dia = random.uniform(28.0, 34.0)
        elif clima == "Soleado":
            temp_base_dia = random.uniform(24.0, 29.0)
        elif clima == "Parcialmente Nublado":
            temp_base_dia = random.uniform(20.0, 25.0)
        elif clima == "Nublado":
            temp_base_dia = random.uniform(18.0, 22.0)
        else: # Lluvioso
            temp_base_dia = random.uniform(16.0, 20.0)

        # Entre 5 y 12 ventas por día distribuidas en distintas horas
        num_ventas = random.randint(5, 12)
        for _ in range(num_ventas):
            hora = random.choices(horas_operacion, weights=pesos_hora, k=1)[0]
            temp_hora = _calcular_temp_por_hora(temp_base_dia, hora, clima)

            # Mayor temperatura en esa hora aumenta probabilidad de comprar helados refrescantes
            temp_boost = 1.0 + max(0.0, (temp_hora - 22.0) * 0.04)
            # Picos de tarde aumentan volumen
            hora_boost = 1.3 if 14 <= hora <= 17 else (1.15 if 20 <= hora <= 21 else 0.85)

            producto = random.choice(productos)
            base_cant = 4.0 * factor * finde_factor * temp_boost * hora_boost
            cantidad = max(1, int(random.gauss(base_cant, 1.8)))
            
            precio_unitario = precios_base.get(producto, 8000)
            ingreso = cantidad * precio_unitario

            rows.append((
                d.isoformat(),
                hora,
                dias_es[dia_idx],
                clima,
                temp_hora,
                producto,
                cantidad,
                ingreso,
            ))

    cur.executemany("""
        INSERT INTO ventas (fecha, hora, dia_semana, clima, temperatura, producto, cantidad, ingreso)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, rows)


def insertar_venta(fecha, dia_semana, clima, temperatura, producto, cantidad, precio_unitario, hora=None):
    """Inserta una venta individual en la base de datos."""
    if hora is None:
        hora = datetime.now().hour
    conn = get_connection()
    ingreso = cantidad * precio_unitario
    conn.execute("""
        INSERT INTO ventas (fecha, hora, dia_semana, clima, temperatura, producto, cantidad, ingreso)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (fecha, hora, dia_semana, clima, temperatura, producto, cantidad, ingreso))
    conn.commit()
    conn.close()


def obtener_ventas(fecha_inicio=None, fecha_fin=None):
    """Obtiene ventas registradas, opcionalmente filtradas por rango de fecha."""
    conn = get_connection()
    # Asegurar que la estructura esté inicializada
    cur = conn.cursor()
    cur.execute("PRAGMA table_info(ventas)")
    cols = [c[1] for c in cur.fetchall()]
    if "hora" not in cols:
        conn.close()
        init_db()
        conn = get_connection()

    query = "SELECT * FROM ventas"
    params = []
    if fecha_inicio and fecha_fin:
        query += " WHERE fecha BETWEEN ? AND ?"
        params = [fecha_inicio, fecha_fin]
    query += " ORDER BY fecha DESC, hora DESC, id DESC"
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]
