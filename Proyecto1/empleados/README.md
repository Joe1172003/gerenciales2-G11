# Empleados de QuetzalMart: cómo importarlos

Persona 5. Estos archivos los genera `scripts/p5/generar_empleados.py`.

Hay **5 departamentos**, **6 cargos** y **35 empleados**: 15 en QM Guatemala, 10 en QM México y 10 en QM El Salvador.

Impórtalos con **tu usuario**, no con el del bot, y **en este orden**. Para cada archivo, entra a la vista de lista, abre el engranaje ⚙ y elige **Importar registros**. Sube el archivo, presiona **Probar** y, si sale todo en verde, presiona **Importar**.

| # | Archivo | Dónde se importa | Qué hace |
|---|---------|------------------|----------|
| 1 | `1_departamentos.xlsx` | Empleados → Configuración → Departamentos | Crea los 5 departamentos |
| 2 | `2_cargos.xlsx` | Empleados → Configuración → Puestos de trabajo | Crea los 6 cargos, cada uno con su departamento |
| 3 | `3_empleados.xlsx` | Empleados → Empleados | Crea los 35 empleados con su cargo, departamento y sucursal |
| 4 | `4_jefes_departamento.xlsx` | Empleados → Configuración → Departamentos | Asigna el jefe de cada departamento. Odoo lo pone solo como "Gerente" de los empleados de ese departamento |

## Antes de presionar Importar en el archivo 3

La columna `category_ids` lleva las etiquetas **QM Guatemala / QM México / QM El Salvador** y **Empleado**. Si Odoo avisa que esas etiquetas no existen, toca el ícono de opciones de esa columna y elige **crear los valores que no existan**. También puedes crear las 4 etiquetas a mano en Empleados → Configuración → Etiquetas.

## Si algo sale mal

La columna `id` es el ID externo, así que volver a importar el mismo archivo **actualiza** los registros en vez de duplicarlos. Puedes corregir y reimportar sin miedo.

## Después de importar

1. Toma capturas de la vista previa del importador y de la lista final. Sirven para la sección 3 del Manual 1 (carga masiva).
2. Sube los 5 contratos de `documentos/pdf/contrato_empleado_EMP0XX.pdf` a **Documentos → Documentos QuetzalMart → Contratos de empleados**. Ponles la categoría **Recursos Humanos** y las etiquetas **Empleado**, la sucursal y **Vigente**.

| Contrato | Empleado | Sucursal |
|----------|----------|----------|
| EMP001 | Ana Lucía Morales Pérez, Gerente de Sucursal | QM Guatemala |
| EMP005 | Sofía Alejandra Herrera Batz, Cajero | QM Guatemala |
| EMP016 | Alejandro Sánchez Villarreal, Gerente de Sucursal | QM México |
| EMP019 | Ximena Hernández Zúñiga, Cajero | QM México |
| EMP026 | Roberto Carlos Hernández Flores, Gerente de Sucursal | QM El Salvador |

3. Comprueba los resultados con las consultas 5.1 a 5.6 de `sql/p5_consultas.sql`.
