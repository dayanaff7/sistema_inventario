# control_csv.py
import csv
import os
from datetime import datetime

# Rutas de archivos
RUTA_MOV = "archivos/movimientos.csv"
RUTA_ENT = "archivos/entregas.csv"
RUTA_DEV = "archivos/devoluciones.csv"

# Columnas finales del archivo movimientos.csv
CAMPOS_MOV = [
    "id_movimiento",
    "tipo_movimiento",
    "fecha",          # siempre YYYY-MM-DD
    "nombre",
    "rut",
    "centro_costo",
    "marca",
    "serie"
]


# -----------------------------
# Normalizaciones
# -----------------------------
def normalizar_fecha(fecha_str: str) -> str:
    """
    Funcion que permite convertir fechas tipo '7/01/2025' o '13/10/2024' a 'YYYY-MM-DD'.
    """
    fecha_str = (fecha_str or "").strip()
    dt = datetime.strptime(fecha_str, "%d/%m/%Y")
    return dt.strftime("%Y-%m-%d")


def construir_id(tipo: str, serie: str, rut: str, fecha_norm: str) -> str:
    """
    ID estable para deduplicar (mismo evento -> mismo id).
    """
    tipo = (tipo or "").strip().upper()
    serie = (serie or "").strip()
    rut = (rut or "").strip()
    fecha_norm = (fecha_norm or "").strip()
    return f"{tipo}|{serie}|{rut}|{fecha_norm}"


def asegurar_archivo_movimientos(ruta_movimientos: str):
    """
    Crea movimientos.csv con encabezados si no existe.
    """
    if os.path.exists(ruta_movimientos):
        return
    with open(ruta_movimientos, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=CAMPOS_MOV)
        writer.writeheader()


def leer_movimientos_existentes(ruta_movimientos: str) -> list[dict]:
    if not os.path.exists(ruta_movimientos):
        return []
    with open(ruta_movimientos, "r", encoding="utf-8", newline="") as f:
        lector = csv.DictReader(f)
        return [fila for fila in lector]


def leer_ids_existentes(ruta_movimientos: str) -> set:
    """
    Devuelve un set con todos los id_movimiento existentes.
    """
    ids = set()
    if not os.path.exists(ruta_movimientos):
        return ids

    with open(ruta_movimientos, "r", encoding="utf-8", newline="") as f:
        lector = csv.DictReader(f)
        for fila in lector:
            mid = (fila.get("id_movimiento") or "").strip()
            if mid:
                ids.add(mid)
    return ids


def sobrescribir_movimientos(ruta_movimientos: str, movimientos: list[dict]):
    """
    Reescribe el archivo completo ya ordenado.
    """
    with open(ruta_movimientos, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=CAMPOS_MOV)
        writer.writeheader()
        writer.writerows(movimientos)


def ordenar_por_fecha_y_prioridad(movimientos: list[dict]) -> list[dict]:
    """
    Orden:
    1) fecha ascendente (antiguo -> nuevo)
    2) misma fecha: agrupar por serie
    3) En caso que sea la misma fecha y misma serie: ENTREGA debe ir primero, DEVOLUCION después (Caso hipotético)
    4) estabilidad: id_movimiento
    """
    prioridad = {"ENTREGA": 0, "DEVOLUCION": 1}

    def key_mov(m):
        fecha = datetime.strptime((m.get("fecha") or "").strip(), "%Y-%m-%d")
        serie = (m.get("serie") or "").strip()
        tipo = (m.get("tipo_movimiento") or "").strip().upper()
        prio = prioridad.get(tipo, 99)
        mid = (m.get("id_movimiento") or "").strip()
        return (fecha, serie, prio, mid)

    return sorted(movimientos, key=key_mov)


# -----------------------------
# Cargas desde CSV origen
# -----------------------------
def cargar_entregas(ruta: str) -> list[dict]:
    movimientos = []
    with open(ruta, "r", encoding="utf-8", newline="") as f:
        lector = csv.DictReader(f)
        for fila in lector:
            fecha_norm = normalizar_fecha(fila.get("Fecha", ""))
            mov = {
                "tipo_movimiento": "ENTREGA",
                "fecha": fecha_norm,
                "nombre": (fila.get("Nombre") or "").strip(),
                "rut": (fila.get("Rut") or "").strip(),
                "centro_costo": (fila.get("Centro de Costo") or "").strip(),
                "marca": (fila.get("Notebook Marca") or "").strip(),
                "serie": (fila.get("N°Serie") or "").strip(),
            }
            mov["id_movimiento"] = construir_id(
                mov["tipo_movimiento"], mov["serie"], mov["rut"], mov["fecha"]
            )
            movimientos.append(mov)
    return movimientos


def cargar_devoluciones(ruta: str) -> list[dict]:
    movimientos = []
    with open(ruta, "r", encoding="utf-8", newline="") as f:
        lector = csv.DictReader(f)
        for fila in lector:
            fecha_norm = normalizar_fecha(fila.get("Fecha Devolucion", ""))
            mov = {
                "tipo_movimiento": "DEVOLUCION",
                "fecha": fecha_norm,
                "nombre": (fila.get("Nombre") or "").strip(),
                "rut": (fila.get("Rut") or "").strip(),
                "centro_costo": (fila.get("Centro de Costo") or "").strip(),
                "marca": (fila.get("Notebook Marca") or "").strip(),
                "serie": (fila.get("N°Serie") or "").strip(),
            }
            mov["id_movimiento"] = construir_id(
                mov["tipo_movimiento"], mov["serie"], mov["rut"], mov["fecha"]
            )
            movimientos.append(mov)
    return movimientos


# -----------------------------
# Función principal
# -----------------------------
def actualizar_movimientos():
    """
    Actualiza archivos/movimientos.csv:
    - acumula nuevos registros
    - evita duplicados por id_movimiento
    - ordena por fecha (y por prioridad ENTREGA antes que DEVOLUCION si coincide fecha+serie)
    - deja el más nuevo al final
    """
    asegurar_archivo_movimientos(RUTA_MOV)

    # Cargar historial existente
    existentes = leer_movimientos_existentes(RUTA_MOV)
    ids_existentes = { (m.get("id_movimiento") or "").strip() for m in existentes if m.get("id_movimiento") }

    # Cargar nuevos desde entregas/devoluciones
    nuevos = []
    if os.path.exists(RUTA_ENT):
        nuevos += cargar_entregas(RUTA_ENT)
    if os.path.exists(RUTA_DEV):
        nuevos += cargar_devoluciones(RUTA_DEV)

    # Agregar solo los que no existen
    agregados = 0
    for mov in nuevos:
        mid = mov.get("id_movimiento")
        if not mid:
            continue
        if mid in ids_existentes:
            continue

        existentes.append(mov)
        ids_existentes.add(mid)
        agregados += 1

    # Ordenar y reescribir completo
    existentes = ordenar_por_fecha_y_prioridad(existentes)
    sobrescribir_movimientos(RUTA_MOV, existentes)

    print(f"Movimientos nuevos agregados: {agregados}")
    print("movimientos.csv actualizado y ordenado (antiguo -> nuevo).")
