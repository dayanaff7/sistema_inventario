def es_numero(texto: str) -> bool:
    return texto.strip().isdigit()

def validar_opcion(texto: str, opciones_validas: set[int]) -> int | None:
    """
    Retorna la opción como int si es válida, si no retorna None.
    """
    if not es_numero(texto):
        return None

    opcion = int(texto)
    if opcion not in opciones_validas:
        return None

    return opcion

def limpiar_texto(valor: str) -> str:
    return (valor or "").strip()

def validar_no_vacio(valor: str) -> bool:
    return bool(limpiar_texto(valor))