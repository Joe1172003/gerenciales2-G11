' ============================================================================
' Invoke Code: GuardarArchivos  (lenguaje VB.NET)
' Escribe las 5 tablas como archivos CSV (UTF-8 sin BOM) en la carpeta de salida.
' Odoo los importa igual que un Excel. Se usa codigo porque las actividades
' Write Range / Write CSV de esta version solo escriben en archivos que ya existen.
'
' Argumentos:
'   in_carpeta      In  String     <- str_salida
'   in_etiquetas    In  DataTable  <- dt_etiquetas
'   in_clientes     In  DataTable  <- dt_clientes
'   in_productos    In  DataTable  <- dt_productos
'   in_existencias  In  DataTable  <- dt_existencias
'   in_bitacora     In  DataTable  <- dt_bitacora
' ============================================================================
Dim tablas As New Dictionary(Of String, System.Data.DataTable) From {
    {"1_etiquetas.csv", in_etiquetas},
    {"2_clientes.csv", in_clientes},
    {"3_productos.csv", in_productos},
    {"4_existencias.csv", in_existencias},
    {"bitacora.csv", in_bitacora}
}

For Each par As KeyValuePair(Of String, System.Data.DataTable) In tablas
    Dim sb As New System.Text.StringBuilder()
    Dim encabezados As New List(Of String)
    For Each c As System.Data.DataColumn In par.Value.Columns
        encabezados.Add("""" & c.ColumnName.Replace("""", """""") & """")
    Next
    sb.AppendLine(String.Join(",", encabezados))

    For Each r As System.Data.DataRow In par.Value.Rows
        Dim valores As New List(Of String)
        For Each c As System.Data.DataColumn In par.Value.Columns
            Dim v As String = If(IsDBNull(r(c)), "", r(c).ToString())
            valores.Add("""" & v.Replace("""", """""") & """")
        Next
        sb.AppendLine(String.Join(",", valores))
    Next

    System.IO.File.WriteAllText(System.IO.Path.Combine(in_carpeta, par.Key), sb.ToString(), New System.Text.UTF8Encoding(False))
Next
