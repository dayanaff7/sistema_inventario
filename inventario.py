# inventario.py
import csv
import os
from datetime import datetime

RUTA_MOV = "archivos/movimientos.csv"
RUTA_FRESH = "archivos/freshservice.csv"
RUTA_PEND = "archivos/pendientes.csv"


# -----------------------------
# Helpers
# -----------------------------
def _normalizar_serie(serie: str) -> str:
    return (serie or "").strip()


def _parsear_fecha_yyyy_mm_dd(fecha_str: str) -> datetime:
    return datetime.strptime((fecha_str or "").strip(), "%Y-%m-%d")


# -----------------------------
# Parte 1: Resumen inventario (movimientos)
# -----------------------------
def cargar_movimientos(ruta: str = RUTA_MOV) -> list[dict]:
    if not os.path.exists(ruta):
        return []

    with open(ruta, "r", encoding="utf-8", newline="") as f:
        lector = csv.DictReader(f)
        return list(lector)


def ordenar_movimientos(movimientos: list[dict]) -> list[dict]:
    # Orden ascendente: antiguo -> nuevo
    return sorted(movimientos, key=lambda m: _parsear_fecha_yyyy_mm_dd(m.get("fecha", "")))


def calcular_estado_actual(movimientos: list[dict]) -> dict:
    """
    Estado actual por serie según el último movimiento.
    Retorna dict: { serie: "ENTREGADO"|"DISPONIBLE" }
    """
    estado_por_serie = {}
    movimientos_ordenados = ordenar_movimientos(movimientos)

    for mov in movimientos_ordenados:
        serie = _normalizar_serie(mov.get("serie"))
        tipo = (mov.get("tipo_movimiento") or "").strip().upper()

        if not serie:
            continue

        if tipo == "ENTREGA":
            estado_por_serie[serie] = "ENTREGADO"
        elif tipo == "DEVOLUCION":
            estado_por_serie[serie] = "DISPONIBLE"

    return estado_por_serie


def resumen_inventario() -> dict:
    """
    Retorna un resumen para mostrar en el menú.
    """
    movimientos = cargar_movimientos()

    if not movimientos:
        return {
            "total_movimientos": 0,
            "total_series": 0,
            "entregados": 0,
            "disponibles": 0
        }

    estado = calcular_estado_actual(movimientos)
    entregados = sum(1 for v in estado.values() if v == "ENTREGADO")
    disponibles = sum(1 for v in estado.values() if v == "DISPONIBLE")

    return {
        "total_movimientos": len(movimientos),
        "total_series": len(estado),
        "entregados": entregados,
        "disponibles": disponibles
    }


# -----------------------------
# Parte 2: Freshservice (pendientes)
# -----------------------------
def leer_seriales_freshservice(ruta: str = RUTA_FRESH) -> set:
    """
    Lee freshservice.csv y retorna un set con las seriales inventariadas.
    Columna confirmada: 'Número de serie'
    """
    seriales = set()

    if not os.path.exists(ruta):
        print("No se encontró freshservice.csv en la carpeta archivos.")
        return seriales

    with open(ruta, "r", encoding="utf-8", newline="") as f:
        lector = csv.DictReader(f)

        if lector.fieldnames is None or "Número de serie" not in lector.fieldnames:
            print("El archivo freshservice.csv no tiene la columna 'Número de serie'.")
            print(f"Columnas detectadas: {lector.fieldnames}")
            return seriales

        for fila in lector:
            serie = _normalizar_serie(fila.get("Número de serie"))
            if serie:
                seriales.add(serie)

    return seriales


def generar_pendientes_freshservice():
    """
    Genera pendientes.csv con SOLO el último movimiento por serie
    que NO existe en Freshservice.
    """
    if not os.path.exists(RUTA_MOV):
        print("No existe movimientos.csv. Primero ejecuta 'Actualización de Actas'.")
        return

    seriales_fresh = leer_seriales_freshservice(RUTA_FRESH)
    if not seriales_fresh:
        print("No se pudieron obtener seriales desde freshservice.csv.")
        return

    movimientos = cargar_movimientos(RUTA_MOV)

    # Aseguramos orden (por si el archivo no estuviera ordenado)
    movimientos = ordenar_movimientos(movimientos)

    # Último movimiento por serie (pendiente)
    ultimo_por_serie = {}

    for mov in movimientos:
        serie = _normalizar_serie(mov.get("serie"))
        if not serie:
            continue

        if serie in seriales_fresh:
            continue

        # Se pisa para quedarnos con el último movimiento
        ultimo_por_serie[serie] = mov

    if not ultimo_por_serie:
        print("No existen equipos pendientes de registrar en Freshservice.")
        return

    pendientes = list(ultimo_por_serie.values())

    with open(RUTA_PEND, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=pendientes[0].keys())
        writer.writeheader()
        writer.writerows(pendientes)

    print(f"pendientes.csv generado: {len(pendientes)} equipos (último movimiento por serie).")

def listar_pendientes_freshservice():
    """
    Lee archivos/pendientes.csv y lo lista por pantalla.
    Si el archivo no existe, sugiere ejecutar la opción 2.
    """
    if not os.path.exists(RUTA_PEND):
        print("No existe pendientes.csv.")
        print("Primero ejecuta la opción 2: 'Cruce con FreshService (Generar pendientes)'.")
        return

    with open(RUTA_PEND, "r", encoding="utf-8", newline="") as f:
        lector = csv.DictReader(f)
        pendientes = list(lector)

    if not pendientes:
        print("pendientes.csv existe, pero está vacío (no hay pendientes).")
        return

    print("\n=========== PENDIENTES FRESHSERVICE ===========")
    print(f"Total equipos pendientes: {len(pendientes)}\n")

    # Encabezado  
    print(f"{'SERIE':<18} {'TIPO':<12} {'FECHA':<12} {'RUT':<14} {'NOMBRE'}")
    print("-" * 70)

    for mov in pendientes:
        serie = (mov.get("serie") or "").strip()
        tipo = (mov.get("tipo_movimiento") or "").strip()
        fecha = (mov.get("fecha") or "").strip()
        rut = (mov.get("rut") or "").strip()
        nombre = (mov.get("nombre") or "").strip()

        print(f"{serie:<18} {tipo:<12} {fecha:<12} {rut:<14} {nombre}")

    print("-" * 70)
    print("Tip: estos equipos aparecen en actas pero NO están registrados en Freshservice.")

def buscar_equipo_por_serie():
    """
    Busca todos los movimientos de una serie ingresada por el usuario.
    La búsqueda es insensible a mayúsculas/minúsculas.
    """
    if not os.path.exists(RUTA_MOV):
        print("No existe movimientos.csv. Primero ejecute 'Actualización de Actas'.")
        return

    serie_input = input("Ingrese número de serie del equipo: ").strip().upper()

    if not serie_input:
        print("La serie no puede estar vacía.")
        return

    movimientos = cargar_movimientos(RUTA_MOV)

    encontrados = [
        mov for mov in movimientos
        if (mov.get("serie") or "").strip().upper() == serie_input
    ]

    if not encontrados:
        print(f"No se encontraron movimientos para la serie {serie_input}.")
        return

    print("\n==============================================")
    print(f" Movimientos del equipo - Serie: {serie_input}")
    print("==============================================")
    print(f"{'FECHA':<12} {'TIPO':<12} {'RUT':<14} {'NOMBRE':<25} {'CENTRO COSTO'}")
    print("-" * 90)

    for mov in encontrados:
        fecha = mov.get("fecha", "")
        tipo = mov.get("tipo_movimiento", "")
        rut = mov.get("rut", "")
        nombre = mov.get("nombre", "")
        cc = mov.get("centro_costo", "")

        print(f"{fecha:<12} {tipo:<12} {rut:<14} {nombre:<25} {cc}")

    print("-" * 90)
    print(f"Total movimientos encontrados: {len(encontrados)}")
