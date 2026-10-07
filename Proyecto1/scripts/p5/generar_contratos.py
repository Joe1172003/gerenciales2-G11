"""
Persona 5 - Genera 5 contratos laborales en PDF para el gestor documental.

Los nombres salen de generar_empleados.py, asi coinciden con los empleados
importados en Odoo. Salida: documentos/pdf/contrato_empleado_EMP0XX.pdf

Se suben en Documentos > Documentos QuetzalMart > Contratos de empleados,
con categoria Recursos Humanos y etiquetas Empleado + <sucursal> + Vigente.

Uso:  python scripts/p5/generar_contratos.py
"""
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from generar_empleados import CON_CONTRATO, empleados

RAIZ = Path(__file__).resolve().parents[2]
SALIDA = RAIZ / "documentos" / "pdf"

PAIS = {
    "GT": {"empresa": "QuetzalMart, Sociedad Anónima", "ciudad": "Ciudad de Guatemala",
           "ley": "el Código de Trabajo de Guatemala (Decreto 1441)", "moneda": "Q",
           "direccion": "Avenida Reforma 8-60, zona 9, Ciudad de Guatemala"},
    "MX": {"empresa": "QuetzalMart México, sucursal de QuetzalMart, S.A.", "ciudad": "Tapachula, Chiapas",
           "ley": "la Ley Federal del Trabajo de los Estados Unidos Mexicanos", "moneda": "MXN $",
           "direccion": "Av. Central Norte 45, Centro, Tapachula, Chiapas"},
    "SV": {"empresa": "QuetzalMart El Salvador, sucursal de QuetzalMart, S.A.", "ciudad": "San Salvador",
           "ley": "el Código de Trabajo de la República de El Salvador", "moneda": "US$",
           "direccion": "Boulevard de los Héroes 1120, San Salvador"},
}

# codigo -> (numero de contrato, fecha de inicio, salario mensual, horario)
CONDICIONES = {
    "EMP001": ("CE-GT-2025-001", "6 de enero de 2025", "12,000.00", "lunes a viernes de 8:00 a 17:00 horas"),
    "EMP005": ("CE-GT-2025-014", "3 de marzo de 2025", "4,250.00", "turnos rotativos de 8 horas, de lunes a sábado"),
    "EMP016": ("CE-MX-2025-001", "1 de julio de 2025", "28,000.00", "lunes a viernes de 8:00 a 17:00 horas"),
    "EMP019": ("CE-MX-2025-006", "15 de julio de 2025", "10,200.00", "turnos rotativos de 8 horas, de lunes a sábado"),
    "EMP026": ("CE-SV-2025-001", "4 de agosto de 2025", "1,400.00", "lunes a viernes de 8:00 a 17:00 horas"),
}

AZUL = colors.HexColor("#1F4E78")


def estilos():
    s = getSampleStyleSheet()
    return {
        "marca": ParagraphStyle("marca", parent=s["Title"], fontSize=20, textColor=AZUL, spaceAfter=2),
        "sub": ParagraphStyle("sub", parent=s["Normal"], alignment=TA_CENTER, fontSize=9, textColor=colors.grey),
        "titulo": ParagraphStyle("titulo", parent=s["Heading2"], alignment=TA_CENTER, spaceBefore=10),
        "clausula": ParagraphStyle("clausula", parent=s["Heading4"], textColor=AZUL, spaceBefore=6, spaceAfter=2),
        "texto": ParagraphStyle("texto", parent=s["Normal"], alignment=TA_JUSTIFY, fontSize=10, leading=14),
        "nota": ParagraphStyle("nota", parent=s["Normal"], alignment=TA_CENTER, fontSize=7.5, textColor=colors.grey),
    }


def contrato(e):
    p = PAIS[e["pais"]]
    numero, inicio, salario, horario = CONDICIONES[e["codigo"]]
    st = estilos()
    ruta = SALIDA / f"contrato_empleado_{e['codigo']}.pdf"
    doc = SimpleDocTemplate(str(ruta), pagesize=LETTER, leftMargin=2.2 * cm, rightMargin=2.2 * cm,
                            topMargin=1.5 * cm, bottomMargin=1.4 * cm,
                            title=f"Contrato {numero} - {e['nombre']}", author="QuetzalMart · Recursos Humanos")
    h = []
    h.append(Paragraph("QuetzalMart", st["marca"]))
    h.append(Paragraph(f"Departamento de Recursos Humanos · {e['sucursal']}", st["sub"]))
    h.append(Paragraph("CONTRATO INDIVIDUAL DE TRABAJO POR TIEMPO INDEFINIDO", st["titulo"]))

    datos = Table([
        ["No. de contrato", numero, "Código de empleado", e["codigo"]],
        ["Trabajador(a)", e["nombre"], "Identificación", e["identificacion"]],
        ["Puesto", e["cargo"], "Departamento", e["departamento"]],
        ["Sucursal", e["sucursal"], "Fecha de inicio", inicio],
    ], colWidths=[3.2 * cm, 5.4 * cm, 3.4 * cm, 4.6 * cm])
    datos.setStyle(TableStyle([
        ("FONTSIZE", (0, 0), (-1, -1), 8.5),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTNAME", (2, 0), (2, -1), "Helvetica-Bold"),
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#DCE6F1")),
        ("BACKGROUND", (2, 0), (2, -1), colors.HexColor("#DCE6F1")),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#9DB3CC")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    h += [Spacer(1, 8), datos, Spacer(1, 8)]

    clausulas = [
        ("PRIMERA. Partes.",
         f"Comparecen, por una parte, {p['empresa']}, con domicilio en {p['direccion']}, en adelante "
         f"<b>EL EMPLEADOR</b>, representada por su representante legal; y por la otra, "
         f"<b>{e['nombre']}</b>, con documento de identificación {e['identificacion']}, en adelante "
         f"<b>EL TRABAJADOR</b>. Ambas partes celebran el presente contrato conforme a {p['ley']}."),
        ("SEGUNDA. Puesto y funciones.",
         f"EL TRABAJADOR desempeñará el puesto de <b>{e['cargo']}</b> dentro del departamento de "
         f"{e['departamento']}, en la sucursal {e['sucursal']}, realizando las funciones propias del puesto "
         "y las que razonablemente le asigne su jefe inmediato."),
        ("TERCERA. Plazo.",
         f"El contrato es por tiempo indefinido y surte efectos a partir del {inicio}. Los primeros dos meses "
         "se consideran periodo de prueba."),
        ("CUARTA. Jornada.",
         f"La jornada de trabajo será de {horario}, con los descansos que establece la ley."),
        ("QUINTA. Salario.",
         f"EL TRABAJADOR devengará un salario mensual de <b>{p['moneda']} {salario}</b>, pagadero en dos "
         "quincenas mediante depósito bancario, más las prestaciones de ley que correspondan."),
        ("SEXTA. Confidencialidad.",
         "EL TRABAJADOR se obliga a no divulgar información comercial, de precios, proveedores ni clientes "
         "de QuetzalMart a la que tenga acceso por razón de su puesto, durante y después de la relación laboral."),
        ("SÉPTIMA. Normativa interna.",
         "EL TRABAJADOR declara conocer y acepta cumplir el reglamento interior de trabajo, las normas de "
         "seguridad e higiene y los procedimientos de control de inventario de la empresa."),
    ]
    for t, x in clausulas:
        h.append(Paragraph(t, st["clausula"]))
        h.append(Paragraph(x, st["texto"]))

    h.append(Spacer(1, 10))
    h.append(Paragraph(f"Leído el presente contrato, las partes lo ratifican y firman en {p['ciudad']}, "
                       f"el {inicio}.", st["texto"]))
    h.append(Spacer(1, 28))
    firmas = Table([["_______________________________", "_______________________________"],
                    ["Representante legal", e["nombre"]],
                    [p["empresa"], "EL TRABAJADOR"]], colWidths=[8.3 * cm, 8.3 * cm])
    firmas.setStyle(TableStyle([("ALIGN", (0, 0), (-1, -1), "CENTER"), ("FONTSIZE", (0, 0), (-1, -1), 8.5)]))
    h += [firmas, Spacer(1, 8),
          Paragraph("Documento ficticio elaborado con fines académicos - Sistemas Organizacionales y "
                    "Gerenciales 2 - USAC", st["nota"])]
    doc.build(h)
    return ruta


def main():
    SALIDA.mkdir(parents=True, exist_ok=True)
    por_codigo = {e["codigo"]: e for e in empleados()}
    for cod in CON_CONTRATO:
        e = por_codigo[cod]
        print(f"{contrato(e).name}  ->  {e['nombre']} · {e['cargo']} · {e['sucursal']}")


if __name__ == "__main__":
    main()
