' ============================================================================
' Invoke Code: CrearTablas  (lenguaje VB.NET)
' Crea las 4 tablas vacias donde el bot va juntando lo que lee.
'
' Argumentos (boton "Edit Arguments" del Invoke Code):
'   out_clientes     Out   DataTable
'   out_etiquetas    Out   DataTable
'   out_productos    Out   DataTable
'   out_existencias  Out   DataTable
'   out_bitacora     Out   DataTable
' Los encabezados son los nombres tecnicos de Odoo: el importador los reconoce
' solo, sin importar el idioma del usuario.
' ============================================================================
out_clientes = New System.Data.DataTable("clientes")
For Each col As String In "id,name,company_type,parent_id,email,phone,street,street2,city,state_id,zip,country_id,vat,Website Link,category_id/id,ref,comment".Split(","c)
    out_clientes.Columns.Add(col, GetType(String))
Next

out_etiquetas = New System.Data.DataTable("etiquetas")
out_etiquetas.Columns.Add("id", GetType(String))
out_etiquetas.Columns.Add("name", GetType(String))
out_etiquetas.Rows.Add("rpa_tag_rpa", "RPA")

out_productos = New System.Data.DataTable("productos")
For Each col As String In "id,name,type,default_code,barcode,list_price,standard_price,weight,description_sale,is_storable,is_published".Split(","c)
    out_productos.Columns.Add(col, GetType(String))
Next

out_existencias = New System.Data.DataTable("existencias")
For Each col As String In "product_id,location_id,inventory_quantity".Split(","c)
    out_existencias.Columns.Add(col, GetType(String))
Next

' Bitacora: una fila por cada paso del bot (lo que leyo, lo que importo, errores)
out_bitacora = New System.Data.DataTable("bitacora")
For Each col As String In "Fecha,Paso,Archivo,Hoja,Resultado".Split(","c)
    out_bitacora.Columns.Add(col, GetType(String))
Next
