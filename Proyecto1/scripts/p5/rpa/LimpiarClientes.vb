' ============================================================================
' Invoke Code: LimpiarClientes  (lenguaje VB.NET)
' Recibe una hoja "clientes" tal como la leyo Read Range y agrega sus filas,
' ya limpias y con nombres tecnicos de Odoo, a dt_clientes y dt_etiquetas.
'
' Argumentos (boton "Edit Arguments" del Invoke Code):
'   in_hoja          In    DataTable   <- la hoja leida con Read Range (con encabezados)
'   in_clientes      In    DataTable   <- dt_clientes (se le agregan filas)
'   in_etiquetas     In    DataTable   <- dt_etiquetas (se le agregan filas)
'   out_agregados    Out   Int32
'   out_repetidos    Out   Int32
'
' Lo que resuelve:
'   - Encabezados con * o en otro orden ("Name*", "Company Type*"): se buscan por nombre.
'   - Filas vacias al final de la hoja: se saltan (sin Name no hay cliente).
'   - Numeros guardados como decimales (Zip 10407.0): se escriben como 10407.
'   - Cliente repetido en otro archivo: se omite (mismo ID externo).
'   - ID externo: rpa_cli_ + Reference (o Tax ID, o Email, o Name). Si el bot
'     corre dos veces, Odoo actualiza en lugar de duplicar.
'   - Tags: se agrega siempre RPA, y cada etiqueta nueva va a dt_etiquetas.
'   - Related Company: el auxiliar confirmo que siempre viene vacia.
' ============================================================================

Dim cultura As System.Globalization.CultureInfo = System.Globalization.CultureInfo.InvariantCulture

' Normaliza un texto: minusculas, sin *, sin tildes y sin espacios dobles
Dim Norm As Func(Of String, String) = Function(s As String)
    Dim t As String = If(s, "").Replace("*", " ").Trim().ToLowerInvariant().Normalize(System.Text.NormalizationForm.FormD)
    Dim sb As New System.Text.StringBuilder()
    For Each ch As Char In t
        If System.Globalization.CharUnicodeInfo.GetUnicodeCategory(ch) <> System.Globalization.UnicodeCategory.NonSpacingMark Then sb.Append(ch)
    Next
    Return System.Text.RegularExpressions.Regex.Replace(sb.ToString(), "\s+", " ").Trim()
End Function

' Texto apto para ID externo: solo a-z, 0-9 y _
Dim Slug As Func(Of String, String) = Function(s As String)
    Return System.Text.RegularExpressions.Regex.Replace(Norm(s), "[^a-z0-9]+", "_").Trim("_"c)
End Function

' Convierte el valor de una celda en texto limpio (10407.0 -> 10407)
Dim Texto As Func(Of Object, String) = Function(v As Object)
    If v Is Nothing OrElse IsDBNull(v) Then Return ""
    If TypeOf v Is Double Then
        Dim d As Double = CDbl(v)
        If Math.Abs(d - Math.Round(d)) < 0.0001 Then Return Math.Round(d).ToString("0", cultura)
        Return d.ToString("0.############", cultura)
    End If
    Dim s As String = v.ToString().Trim()
    Dim dd As Double
    If System.Text.RegularExpressions.Regex.IsMatch(s, "^-?\d+\.\d+$") AndAlso Double.TryParse(s, System.Globalization.NumberStyles.Float, cultura, dd) AndAlso Math.Abs(dd - Math.Round(dd)) < 0.0001 Then
        Return Math.Round(dd).ToString("0", cultura)
    End If
    Return s
End Function

' Encabezado normalizado -> nombre real de la columna en la hoja
Dim mapa As New Dictionary(Of String, String)
For Each c As System.Data.DataColumn In in_hoja.Columns
    Dim k As String = Norm(c.ColumnName)
    If Not mapa.ContainsKey(k) Then mapa.Add(k, c.ColumnName)
Next

' Busca el valor probando varios nombres posibles de encabezado ("name|nombre")
Dim Valor As Func(Of System.Data.DataRow, String, String) = Function(r As System.Data.DataRow, claves As String)
    For Each k As String In claves.Split("|"c)
        If mapa.ContainsKey(k) Then
            Dim t As String = Texto(r(mapa(k)))
            If t <> "" Then Return t
        End If
    Next
    Return ""
End Function

Dim idsClientes As New HashSet(Of String)
For Each fila As System.Data.DataRow In in_clientes.Rows
    idsClientes.Add(fila("id").ToString())
Next
Dim idsEtiquetas As New HashSet(Of String)
For Each fila As System.Data.DataRow In in_etiquetas.Rows
    idsEtiquetas.Add(fila("id").ToString())
Next

out_agregados = 0
out_repetidos = 0

For Each r As System.Data.DataRow In in_hoja.Rows
    Dim nombre As String = Valor(r, "name|nombre")
    If nombre = "" Then Continue For

    Dim referencia As String = Valor(r, "reference|referencia")
    Dim correo As String = Valor(r, "email|correo")
    Dim nit As String = Valor(r, "tax id|nit")
    Dim baseId As String = referencia
    If baseId = "" Then baseId = nit
    If baseId = "" Then baseId = correo
    If baseId = "" Then baseId = nombre
    Dim xid As String = "rpa_cli_" & Slug(baseId)

    If idsClientes.Contains(xid) Then
        out_repetidos += 1
        Continue For
    End If

    Dim etiquetas As New List(Of String)
    etiquetas.Add("rpa_tag_rpa")
    For Each parte As String In Valor(r, "tags|etiquetas").Split(","c)
        Dim nombreEtiqueta As String = parte.Trim()
        If nombreEtiqueta = "" Then Continue For
        Dim tid As String = "rpa_tag_" & Slug(nombreEtiqueta)
        If Not etiquetas.Contains(tid) Then etiquetas.Add(tid)
        If Not idsEtiquetas.Contains(tid) Then
            in_etiquetas.Rows.Add(tid, nombreEtiqueta)
            idsEtiquetas.Add(tid)
        End If
    Next

    in_clientes.Rows.Add(xid, nombre,
        Valor(r, "company type|tipo de compania"),
        Valor(r, "related company|compania relacionada"),
        correo,
        Valor(r, "phone|telefono"),
        Valor(r, "street|calle"),
        Valor(r, "street2|calle 2|calle2"),
        Valor(r, "city|ciudad"),
        Valor(r, "state|estado|departamento"),
        Valor(r, "zip|codigo postal"),
        Valor(r, "country|pais"),
        nit,
        Valor(r, "website|sitio web"),
        String.Join(",", etiquetas),
        referencia,
        Valor(r, "notes|notas"))

    idsClientes.Add(xid)
    out_agregados += 1
Next
