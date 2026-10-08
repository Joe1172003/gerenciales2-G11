' ============================================================================
' Invoke Code: LimpiarProductos  (lenguaje VB.NET)
' Recibe una hoja "productos" tal como la leyo Read Range y agrega sus filas,
' ya limpias y con nombres tecnicos de Odoo, a dt_productos y dt_existencias.
'
' Argumentos (boton "Edit Arguments" del Invoke Code):
'   in_hoja            In    DataTable   <- la hoja leida con Read Range (con encabezados)
'   in_productos       In    DataTable   <- dt_productos (se le agregan filas)
'   in_existencias     In    DataTable   <- dt_existencias (se le agregan filas)
'   in_ubicacion       In    String      <- ubicacion de inventario, ej. "GT/Existencias"
'   in_noPublicar      In    Boolean     <- True en ensayos para no llenar la tienda
'   out_agregados      Out   Int32
'   out_repetidos      Out   Int32
'
' Lo que resuelve:
'   - External ID es el ID externo de Odoo: correr el bot dos veces actualiza.
'     Si viniera vacio se usa rpa_prd_ + Name.
'   - Product Type (Goods / Service / Combo) se manda tal cual: Odoo lo reconoce.
'     Goods se marca como "rastrear inventario" (is_storable) para poder tener existencias.
'   - Barcode guardado como decimal (54398267125.00001) -> 54398267125.
'   - Product Values: el auxiliar no lo definio y viene vacio; se ignora.
'   - Cantidad a la mano: va a dt_existencias (se importa en Inventario fisico),
'     solo para productos almacenables y con cantidad distinta de 0.
'   - Esta publicado: True/False (acepta 1, si, verdadero). Con in_noPublicar = True
'     siempre queda False.
' ============================================================================

Dim cultura As System.Globalization.CultureInfo = System.Globalization.CultureInfo.InvariantCulture

Dim Norm As Func(Of String, String) = Function(s As String)
    Dim t As String = If(s, "").Replace("*", " ").Trim().ToLowerInvariant().Normalize(System.Text.NormalizationForm.FormD)
    Dim sb As New System.Text.StringBuilder()
    For Each ch As Char In t
        If System.Globalization.CharUnicodeInfo.GetUnicodeCategory(ch) <> System.Globalization.UnicodeCategory.NonSpacingMark Then sb.Append(ch)
    Next
    Return System.Text.RegularExpressions.Regex.Replace(sb.ToString(), "\s+", " ").Trim()
End Function

Dim Slug As Func(Of String, String) = Function(s As String)
    Return System.Text.RegularExpressions.Regex.Replace(Norm(s), "[^a-z0-9]+", "_").Trim("_"c)
End Function

Dim Texto As Func(Of Object, String) = Function(v As Object)
    If v Is Nothing OrElse IsDBNull(v) Then Return ""
    If TypeOf v Is Double Then
        Dim d As Double = CDbl(v)
        If Math.Abs(d - Math.Round(d)) < 0.0001 Then Return Math.Round(d).ToString("0", cultura)
        Return d.ToString("0.############", cultura)
    End If
    If TypeOf v Is Boolean Then Return If(CBool(v), "True", "False")
    Dim s As String = v.ToString().Trim()
    Dim dd As Double
    If System.Text.RegularExpressions.Regex.IsMatch(s, "^-?\d+\.\d+$") AndAlso Double.TryParse(s, System.Globalization.NumberStyles.Float, cultura, dd) AndAlso Math.Abs(dd - Math.Round(dd)) < 0.0001 Then
        Return Math.Round(dd).ToString("0", cultura)
    End If
    Return s
End Function

Dim mapa As New Dictionary(Of String, String)
For Each c As System.Data.DataColumn In in_hoja.Columns
    Dim k As String = Norm(c.ColumnName)
    If Not mapa.ContainsKey(k) Then mapa.Add(k, c.ColumnName)
Next

Dim Valor As Func(Of System.Data.DataRow, String, String) = Function(r As System.Data.DataRow, claves As String)
    For Each k As String In claves.Split("|"c)
        If mapa.ContainsKey(k) Then
            Dim t As String = Texto(r(mapa(k)))
            If t <> "" Then Return t
        End If
    Next
    Return ""
End Function

Dim almacenables As New HashSet(Of String) From {"goods", "consu", "bienes", "consumible", "producto", "storable", "almacenable"}
Dim verdaderos As New HashSet(Of String) From {"true", "1", "yes", "si", "verdadero", "x"}

Dim idsProductos As New HashSet(Of String)
For Each fila As System.Data.DataRow In in_productos.Rows
    idsProductos.Add(fila("id").ToString())
Next

out_agregados = 0
out_repetidos = 0

For Each r As System.Data.DataRow In in_hoja.Rows
    Dim nombre As String = Valor(r, "name|nombre")
    If nombre = "" Then Continue For

    Dim xid As String = Valor(r, "external id|id externo|id")
    If xid = "" Then xid = "rpa_prd_" & Slug(nombre)
    If idsProductos.Contains(xid) Then
        out_repetidos += 1
        Continue For
    End If

    Dim tipo As String = Valor(r, "product type|tipo de producto")
    If tipo = "" Then tipo = "Goods"
    Dim esAlmacenable As Boolean = almacenables.Contains(Norm(tipo))
    Dim publicado As Boolean = (Not in_noPublicar) AndAlso verdaderos.Contains(Norm(Valor(r, "esta publicado|is published|published")))
    Dim codigo As String = Valor(r, "internal reference|referencia interna")

    in_productos.Rows.Add(xid, nombre, tipo, codigo,
        Valor(r, "barcode|codigo de barras"),
        Valor(r, "sales price|precio de venta"),
        Valor(r, "cost|costo"),
        Valor(r, "weight|peso"),
        Valor(r, "sales description|descripcion de venta"),
        If(esAlmacenable, "True", "False"),
        If(publicado, "True", "False"))

    idsProductos.Add(xid)
    out_agregados += 1

    Dim cantidad As String = Valor(r, "cantidad a la mano|quantity on hand|on hand")
    If esAlmacenable AndAlso cantidad <> "" AndAlso cantidad <> "0" Then
        Dim producto As String = codigo
        If producto = "" Then producto = nombre
        in_existencias.Rows.Add(producto, in_ubicacion, cantidad)
    End If
Next
