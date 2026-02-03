📌 Sistema de Inventario de Notebooks (Actas + Freshservice)

Este proyecto permite gestionar y auditar el registro de entrega y devolución de notebooks mediante actas (archivos CSV), generando un historial consolidado de movimientos y realizando un cruce con Freshservice para detectar equipos que aún no han sido registrados en el inventario TI.

Está pensado para resolver una necesidad real: en empresas con operación en terreno (faenas), históricamente pueden existir equipos en circulación sin control formal de activos.

✅ Funcionalidades
1) Actualización de Actas

Lee archivos:

archivos/entregas.csv

archivos/devoluciones.csv

Consolida y actualiza un historial único:

archivos/movimientos.csv

Evita duplicar registros (deduplicación por id_movimiento)

Ordena los movimientos por fecha (antiguo → nuevo)

Regla especial (misma fecha + misma serie):

ENTREGA se registra antes que DEVOLUCIÓN

2) Cruce con Freshservice (Generar pendientes)

Lee:

archivos/movimientos.csv

archivos/freshservice.csv (columna Número de serie)

Detecta seriales presentes en actas pero ausentes en Freshservice

Genera:

archivos/pendientes.csv

El archivo pendientes.csv contiene solo el último movimiento por serie (1 fila por equipo pendiente)

3) Listar pendientes Freshservice

Muestra en consola el contenido de archivos/pendientes.csv

Permite revisar rápidamente:

serial

tipo de movimiento (ENTREGA/DEVOLUCIÓN)


Proyecto_Inventario/
│── main.py
│── menu.py
│── inventario.py
│── control_CSV.py
│── validaciones.py
└── archivos/
    │── entregas.csv
    │── devoluciones.csv
    │── freshservice.csv
    │── movimientos.csv      (se genera/actualiza)
    └── pendientes.csv       (se genera)

📄 Formato de archivos CSV
archivos/entregas.csv

Debe contener las columnas:

Nombre

Rut

Centro de Costo

Fecha (formato d/m/YYYY)

Notebook Marca

N°Serie

archivos/devoluciones.csv

Debe contener las columnas:

Nombre

Rut

Centro de Costo

Fecha Devolucion (formato d/m/YYYY)

Notebook Marca

N°Serie

archivos/freshservice.csv

Debe contener la columna:

Número de serie

▶️ Cómo ejecutar

Ubícate en la carpeta del proyecto:

cd Proyecto_Inventario


Ejecuta el sistema:

python main.py


Menú disponible:

1) Actualización de Actas

2) Cruce con Freshservice (Generar pendientes)

3) Listar pendientes Freshservice

4) Salir

🧠 Lógica clave del sistema
Historial de movimientos

movimientos.csv almacena el historial completo: una misma serie puede aparecer varias veces porque un equipo puede entregarse, devolverse y volver a entregarse.

Estado actual del equipo

El estado del equipo se determina por el último movimiento registrado:

último movimiento = ENTREGA → estado actual: ENTREGADO

último movimiento = DEVOLUCIÓN → estado actual: DISPONIBLE

Detección de pendientes en Freshservice

Un equipo se considera pendiente si:

aparece en movimientos.csv

no aparece en freshservice.csv

🧪 Notas

Si aún no existe movimientos.csv, primero ejecuta la opción 1.

Si no existe pendientes.csv, primero ejecuta la opción 2.

El proyecto utiliza únicamente librerías estándar de Python (csv, os, datetime).

✍️ Autor

Proyecto desarrollado por Dayanna Flores Flores (en base a una necesidad real de control y auditoría de activos TI).




fecha

colaborador / rut
