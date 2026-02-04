from validaciones import validar_opcion
from control_CSV import actualizar_movimientos
from inventario import (
    generar_pendientes_freshservice,
    listar_pendientes_freshservice,
    resumen_inventario,
    buscar_equipo_por_serie
)

def menu_principal():
    opciones = {1, 2, 3, 4, 5}

    while True:
        print("\n==============================")
        print("   SISTEMA INVENTARIO NOTEBOOK")
        print("==============================")
        print("1) Actualización de Actas")
        print("2) Cruce con FreshService (Generar pendientes)")
        print("3) Listar pendientes FreshService")
        print("4) Buscar equipo por número de serie")
        print("5) Salir")

        entrada = input("Seleccione una opción: ")
        opcion = validar_opcion(entrada, opciones)

        if opcion is None:
            print("Opción inválida. Intente nuevamente.")
            continue

        match opcion:
            case 1:
                menu_actualizacion_actas()
            case 2:
                generar_pendientes_freshservice()
            case 3:
                listar_pendientes_freshservice()
            case 4:
                buscar_equipo_por_serie()
            case 5:
                print("Saliendo del sistema...")
                break


def menu_actualizacion_actas():
    print("\n--- Actualización de Actas ---")

    # 1) Alimenta movimientos sin duplicar registros
    actualizar_movimientos()

    # 2) Muestra resumen resumen
    r = resumen_inventario()
    print("\nResumen actual:")
    print(f"Total movimientos: {r['total_movimientos']}")
    print(f"Total equipos (series únicas): {r['total_series']}")
    print(f"Entregados: {r['entregados']}")
    print(f"Disponibles: {r['disponibles']}") # esto es hipotetico ya que debo revisar en una segunda etapa los dados de baja
