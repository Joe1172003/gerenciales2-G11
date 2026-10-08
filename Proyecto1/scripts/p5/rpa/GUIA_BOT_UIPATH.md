# Bot RPA de QuetzalMart en UiPath: guía para armarlo

Persona 5. Esta guía va en el orden en que conviene trabajar. Toma capturas en cada paso marcado con 📸, porque sirven para la sección 4 del Manual 1.

## Qué hace el bot

```
Carpeta del auxiliar ──► 1. LEER ──────────────────► 2. ARMAR ARCHIVOS ──────► 3. IMPORTAR EN ODOO (navegador, sin API)
(clientes - …,            recorre todas las            1_etiquetas.xlsx            Etiquetas de contacto
 productos - …,           carpetas y libros,           2_clientes.xlsx             Contactos
 proveedores - …)         toma solo las hojas          3_productos.xlsx            Productos
                          "clientes" y "productos"     4_existencias.xlsx          Inventario físico + Aplicar
                                                                                   └► bitacora.xlsx + capturas
```

El auxiliar **no permite usar ninguna API de Odoo desde UiPath**. Por eso el bot hace lo mismo que haría una persona: abre el navegador, entra con el usuario del bot y sube cada archivo con **Importar registros**.

## Archivos de esta carpeta

| Archivo | Para qué |
|---|---|
| `generar_carpeta_prueba.py` | Crea `carpeta_prueba_rpa/`, una carpeta como la que traerá el auxiliar, con todos los casos difíciles |
| `referencia_bot.py` | Hace en Python lo mismo que el bot hace con los Excel. Sirve para probar la importación a mano y para comparar el resultado del bot |
| `CrearTablas.vb` | Código para pegar en el primer **Invoke Code** del bot |
| `LimpiarClientes.vb` | Código para pegar en el **Invoke Code** de las hojas clientes |
| `LimpiarProductos.vb` | Código para pegar en el **Invoke Code** de las hojas productos |
| `ejemplos_auxiliar/` | Los dos Excel de ejemplo que el auxiliar compartió en el foro |

---

## PARTE 0 · Probar la importación a mano (15 min, antes de abrir UiPath)

Primero confirma que Odoo acepta los archivos. Si esto funciona a mano, el bot solo tiene que repetir los mismos clics.

1. En PowerShell, dentro de `Proyecto1`:
   ```
   python scripts\p5\rpa\generar_carpeta_prueba.py
   python scripts\p5\rpa\referencia_bot.py carpeta_prueba_rpa salida_esperada "GT/Existencias" --no-publicar
   ```
   Debe terminar con `TOTAL: 3 etiquetas, 8 clientes, 9 productos, 6 existencias`.

2. **Averigua el nombre real de la ubicación de existencias.** En Odoo ve a **Inventario → Configuración → Ubicaciones** y busca la de QM Guatemala que termina en `/Existencias` (por ejemplo `GT/Existencias` o `QMGT/Existencias`).
   - Si no es `GT/Existencias`, repite el segundo comando con el nombre correcto.
   - Anótalo, porque el bot también lo usa.

3. Abre una **ventana de incógnito** y entra a Odoo con el **usuario del bot** (`bot.rpa@quetzalmart.example.com`). Importa los 4 archivos de `salida_esperada\` **en este orden**. Para cada uno: abre la lista, haz clic en ⚙ → **Importar registros** → **Subir archivo**, presiona **Probar** y luego **Importar**.

   | # | Archivo | Dónde |
   |---|---|---|
   | 1 | `1_etiquetas.xlsx` | Contactos → Configuración → **Etiquetas de contacto** |
   | 2 | `2_clientes.xlsx` | **Contactos** |
   | 3 | `3_productos.xlsx` | Inventario → Productos → **Productos** |
   | 4 | `4_existencias.xlsx` | Inventario → Operaciones → **Inventario físico**. Después de importar, presiona **Aplicar todo** → **Aplicar** |

4. **Mientras lo haces, copia la URL de cada pantalla de importación** (termina en `/import`). El bot va a ir directo a esas 4 direcciones. Anótalas así:
   ```
   URL_ETIQUETAS   = https://quetzalmart-g11.duckdns.org/odoo/…/import
   URL_CLIENTES    = https://quetzalmart-g11.duckdns.org/odoo/contacts/import
   URL_PRODUCTOS   = https://quetzalmart-g11.duckdns.org/odoo/…/import
   URL_EXISTENCIAS = https://quetzalmart-g11.duckdns.org/odoo/…/import
   ```

5. Comprueba el resultado con las consultas **30, 31 y 32** de `sql/consultas.sql`.

> Si **Probar** marca un error, no importes: toma captura y revisa qué columna falla. No hace falta limpiar después, porque cada fila trae su ID externo: cuando el bot importe lo mismo, Odoo **actualiza** en vez de duplicar.

---

## PARTE 1 · Instalar UiPath (20 min)

1. Entra a **uipath.com** → **Try UiPath free** y crea una cuenta con tu correo. Es la licencia **Community**, que es gratis.
2. Descarga e instala **UiPath Studio**. Al abrirlo, inicia sesión con esa cuenta y elige el perfil **UiPath Studio**, no StudioX.
3. Instala la extensión del navegador. UiPath **no funciona con Opera**: usa **Microsoft Edge** o **Google Chrome**. En Studio ve a **Inicio → Herramientas → Extensiones de UiPath** y elige la de Edge o la de Chrome. Después actívala en el navegador.
4. Crea un proyecto nuevo: **Proceso**, nombre `BotQuetzalMart`, ubicación `Proyecto1\scripts\p5\rpa\`, **lenguaje VB**, compatibilidad **Windows**.
5. En **Gestionar paquetes** verifica que estén instalados `UiPath.Excel.Activities`, `UiPath.System.Activities` y `UiPath.UIAutomation.Activities`.
6. En el panel **Actividades**, abre el filtro (embudo) y activa **Mostrar clásicas**. Las actividades de **Libro de trabajo** (*Workbook*) leen Excel sin abrir Excel y aceptan `.xls` y `.xlsx`.

---

## PARTE 2 · El bot lee la carpeta y arma los archivos (1 h y media)

### Variables de `Main.xaml`

Créalas en el panel **Variables**, con alcance en toda la secuencia principal:

| Variable | Tipo | Valor inicial |
|---|---|---|
| `str_carpeta` | String | *(vacío)* |
| `str_salida` | String | *(vacío)* |
| `str_url` | String | `"https://quetzalmart-g11.duckdns.org"` |
| `str_usuario` | String | `"bot.rpa@quetzalmart.example.com"` |
| `str_password` | String | *(vacío, se pide al iniciar)* |
| `str_ubicacion` | String | `"GT/Existencias"` ← el nombre real del paso 0.2 |
| `bool_noPublicar` | Boolean | `True` en ensayos · `False` el día de la calificación |
| `arr_archivos` | String[] | |
| `list_hojas` | List&lt;String&gt; | |
| `dt_hoja`, `dt_clientes`, `dt_etiquetas`, `dt_productos`, `dt_existencias`, `dt_bitacora` | DataTable | |
| `int_agregados`, `int_repetidos` | Int32 | |

### Secuencia (arrastra las actividades en este orden)

1. **Select Folder** (*Seleccionar carpeta*) → Output: `str_carpeta`.
2. **Input Dialog** → Title `"Bot QuetzalMart"`, Label `"Contraseña del usuario del bot"`, **IsPassword ✔** → Result: `str_password`.

   La contraseña no queda guardada en el proyecto ni en el repositorio.
3. **Assign** `str_salida` = `System.IO.Path.Combine("C:\RPA_QuetzalMart\salida", Now.ToString("yyyyMMdd_HHmmss"))`

   **Create Folder** → `str_salida`. Cada corrida queda en su propia carpeta, así no se mezclan archivos viejos.
4. **Invoke Code** → pega el contenido de `CrearTablas.vb`. En **Edit Arguments**:

   | Nombre | Dirección | Tipo | Valor |
   |---|---|---|---|
   | out_clientes | Out | DataTable | dt_clientes |
   | out_etiquetas | Out | DataTable | dt_etiquetas |
   | out_productos | Out | DataTable | dt_productos |
   | out_existencias | Out | DataTable | dt_existencias |
   | out_bitacora | Out | DataTable | dt_bitacora |

5. **Assign** `arr_archivos` =
   ```vb
   System.IO.Directory.GetFiles(str_carpeta, "*.xls*", System.IO.SearchOption.AllDirectories).Where(Function(f) Not System.IO.Path.GetFileName(f).StartsWith("~$")).ToArray()
   ```
   Esto busca en todas las subcarpetas, toma `.xls` y `.xlsx` y salta los temporales de Excel (`~$…`).

6. **For Each** `archivo` **in** `arr_archivos` (TypeArgument String). Dentro va un **Try Catch**; en el **Try**:
   1. **Get Workbook Sheets** (clásica, *Libro de trabajo*) → WorkbookPath `archivo` → Result `list_hojas`.
   2. **For Each** `hoja` **in** `list_hojas` (String). Dentro va un **If** con `hoja.Trim.ToLower = "clientes"`:
      - **Then:**
        1. **Read Range** (clásica, *Libro de trabajo*): WorkbookPath `archivo`, SheetName `hoja`, Range `""`, **AddHeaders ✔** → DataTable `dt_hoja`.
        2. **Invoke Code** → pega `LimpiarClientes.vb`. Argumentos: `in_hoja`=dt_hoja (In), `in_clientes`=dt_clientes (In), `in_etiquetas`=dt_etiquetas (In), `out_agregados`=int_agregados (Out, Int32), `out_repetidos`=int_repetidos (Out, Int32).
        3. **Add Data Row** → DataTable `dt_bitacora`, ArrayRow:
           ```vb
           {Now.ToString("yyyy-MM-dd HH:mm:ss"), "Lectura", archivo.Replace(str_carpeta, ""), hoja, int_agregados.ToString & " agregados, " & int_repetidos.ToString & " repetidos"}
           ```
        4. **Log Message** con el mismo texto, para que se vea en el panel de salida durante la demo.
      - **Else:** otro **If** con `hoja.Trim.ToLower = "productos"`, que hace lo mismo con **Read Range**, **Invoke Code** pegando `LimpiarProductos.vb`, **Add Data Row** y **Log Message**. Sus argumentos: `in_hoja`, `in_productos`=dt_productos, `in_existencias`=dt_existencias, `in_ubicacion`=str_ubicacion (In, String), `in_noPublicar`=bool_noPublicar (In, Boolean), `out_agregados`, `out_repetidos`.
      - Las demás hojas (reclamos, registros, proveedor…) no entran a ningún If y se ignoran.

   En el **Catch** (System.Exception) va **Add Data Row** en `dt_bitacora` con `{Now.ToString("yyyy-MM-dd HH:mm:ss"), "Lectura", archivo, "", "ERROR: " & exception.Message}`. Así, si un archivo viene dañado, el bot lo anota y sigue con el siguiente.

7. **Write Range** (clásica, *Libro de trabajo*) cuatro veces, con **AddHeaders ✔** y SheetName `"Sheet1"`:
   - `dt_etiquetas` → `System.IO.Path.Combine(str_salida, "1_etiquetas.xlsx")`
   - `dt_clientes` → `…"2_clientes.xlsx"`
   - `dt_productos` → `…"3_productos.xlsx"`
   - `dt_existencias` → `…"4_existencias.xlsx"`

**✅ Prueba de la Parte 2.** Ejecuta con **F5** y elige `carpeta_prueba_rpa`. En el panel de salida deben aparecer 5 líneas de lectura y en `C:\RPA_QuetzalMart\salida\<fecha>\` los 4 archivos. Ábrelos y compáralos con `salida_esperada\`: deben tener **las mismas filas** (8 clientes, 9 productos, 6 existencias). 📸

---

## PARTE 3 · El bot importa en Odoo por el navegador (1 h y media)

Haz un workflow aparte para no repetir lo mismo cuatro veces: clic derecho en el proyecto → **Nuevo → Secuencia** → `ImportarArchivo.xaml`.

### Argumentos de `ImportarArchivo.xaml`

| Argumento | Dirección | Tipo |
|---|---|---|
| in_urlImport | In | String |
| in_archivo | In | String |
| in_carpetaCapturas | In | String |
| in_nombre | In | String |
| out_resultado | Out | String |

### Contenido (actividades modernas, dentro de un **Use Browser** que se pasa desde Main)

1. **Navigate To** → `in_urlImport`.
2. **Click** sobre el botón **Cargar archivo de datos** (o **Subir archivo**). Lo indicas en el navegador con **Indicate in browser**.
3. Se abre la ventana de Windows para elegir archivo. **Type Into** en la casilla **Nombre de archivo** de esa ventana, con el texto `in_archivo & "[k(enter)]"`.
4. **Click** en **Probar**.
5. **Check App State**, con un tiempo de espera de 20 segundos, sobre el mensaje **verde** que aparece cuando todo está bien:
   - **Si aparece:**
     1. **Click** en **Importar**.
     2. **Check App State** sobre la notificación *"… registros importados de forma exitosa"*.
     3. **Get Text** de esa notificación → `out_resultado`.
     4. **Take Screenshot** + **Save Image** en `System.IO.Path.Combine(in_carpetaCapturas, in_nombre & ".png")`.
   - **Si no aparece:** hubo errores.
     1. **Get Text** del mensaje rojo → `out_resultado = "ERROR: " & texto`.
     2. **Take Screenshot**, guárdala con el mismo nombre más `_error`.
     3. **Click** en **Cancelar**.

### En `Main.xaml`, después de los Write Range

8. **Use Browser** (Edge o Chrome) con URL `str_url & "/web/login"`. Dentro:
   1. **Check App State** sobre la casilla del correo de la página de login:
      - **Si aparece** (la sesión no está abierta):
        1. **Type Into** en el correo → `str_usuario`.
        2. **Type Into** en la contraseña → `str_password`.
        3. **Click** en **Iniciar sesión**.
      - Si no aparece, la sesión ya estaba abierta y el bot sigue.
   2. Cuatro **Invoke Workflow File** → `ImportarArchivo.xaml`, uno por archivo y **en este orden**: etiquetas, clientes, productos, existencias. Usa las URL que anotaste en el paso 0.4.
      - Si una tabla quedó vacía, no la importes. Pon cada Invoke dentro de un **If** con `dt_productos.Rows.Count > 0` (y la condición equivalente para cada tabla).
      - Después de cada Invoke, **Add Data Row** en la bitácora con `{Now…, "Importación", "2_clientes.xlsx", "", resultado}` (cambiando el nombre del archivo según el caso).
   3. Después de importar las existencias, la página vuelve a **Inventario físico**:
      1. **Click** en **Aplicar todo**.
      2. En la ventana que se abre, **Click** en **Aplicar**.
      3. Agrega a la bitácora la fila `"Existencias aplicadas"`.
9. **Write Range** de `dt_bitacora` → `System.IO.Path.Combine(str_salida, "bitacora.xlsx")`.
10. **Message Box** con un resumen:
    ```vb
    "Listo: " & dt_clientes.Rows.Count & " clientes y " & dt_productos.Rows.Count & " productos. Bitácora en " & str_salida
    ```

**✅ Prueba de la Parte 3.** Ejecuta con `carpeta_prueba_rpa`. Debe verse al bot entrando, subiendo los 4 archivos y aplicando las existencias. Comprueba con las consultas **30 a 32**. 📸 Toma captura de la bitácora, de los contactos con etiqueta RPA y de los productos.

---

## PARTE 4 · Ensayo y día de la calificación

- **Carpeta sorpresa:** pide a otra persona del grupo que arme una carpeta parecida, con otros nombres, filas y hojas, y corre el bot con ella sin tocar nada.
- **Correr dos veces la misma carpeta** no debe duplicar nada. Las consultas 30 y 31 deben dar el mismo número.
- **El día de la calificación:**
  - Pon `bool_noPublicar = False`, para que los productos con "Está publicado = True" aparezcan en la tienda (el enunciado pide verlos en el sitio).
  - Abre Edge o Chrome antes de empezar y no muevas el mouse mientras el bot trabaja.
  - Al terminar, muestra la bitácora, la tienda y las consultas 30 a 32.
- **Usa el usuario del bot solo para el bot** y no le cambies el idioma, porque los botones que indicaste están en español.

## Ventajas del RPA (para el Manual 1, sección 4)

- **Tiempo:** cargar a mano los clientes y productos de varias carpetas toma horas; el bot lo hace en minutos y sin pausas.
- **Precisión:** el bot no se salta filas, no confunde hojas y siempre limpia igual los datos (encabezados con \*, números como 1000.0, filas vacías, repetidos).
- **Sin duplicados:** gracias al ID externo, volver a correrlo actualiza en lugar de duplicar.
- **Trazabilidad:** la bitácora y las capturas dejan registro de qué se leyó, qué se importó y qué falló.
- **Escalable:** con las nuevas sucursales llegan más carpetas, y el bot procesa 10 o 1,000 archivos igual, sin contratar más personal.
- **Seguro y sin API:** usa la misma pantalla de importación y los mismos permisos que una persona, con un usuario dedicado.
