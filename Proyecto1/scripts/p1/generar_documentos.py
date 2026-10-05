# Genera los HTML de las facturas de proveedores y los contratos de outsourcing
# subir_documentos.sh los convierte a PDF y los sube al gestor
import json
from pathlib import Path

BASE = Path(__file__).resolve().parents[2] / 'documentos'
HTML = BASE / 'html'

ESTILO = """
<style>
  body { font-family: 'DejaVu Sans', Arial, sans-serif; font-size: 11pt; color: #1f2933; margin: 28px; }
  .cab { display: table; width: 100%; border-bottom: 3px solid VAR_COLOR; padding-bottom: 10px; }
  .cab div { display: table-cell; vertical-align: top; }
  .marca { font-size: 18pt; font-weight: bold; color: VAR_COLOR; }
  .der { text-align: right; }
  h1 { font-size: 15pt; margin: 18px 0 6px; color: VAR_COLOR; }
  h2 { font-size: 12pt; margin: 16px 0 4px; }
  table.det { width: 100%; border-collapse: collapse; margin-top: 12px; }
  table.det th { background: VAR_COLOR; color: #fff; padding: 6px; text-align: left; font-size: 10pt; }
  table.det td { border-bottom: 1px solid #d9e2ec; padding: 6px; font-size: 10pt; }
  .num, table.det th.num { text-align: right; }
  .tot td { border: none; font-weight: bold; }
  .caja { background: #f0f4f8; padding: 10px; margin-top: 12px; }
  .firmas { display: table; width: 100%; margin-top: 60px; }
  .firmas div { display: table-cell; width: 50%; text-align: center; }
  .linea { border-top: 1px solid #333; margin: 0 30px; padding-top: 4px; }
  .pie { margin-top: 30px; font-size: 8pt; color: #829ab1; text-align: center; }
  p { text-align: justify; line-height: 1.45; }
</style>
"""

PIE = ''

CLIENTE = {
    'QM Guatemala': ('QuetzalMart, S.A. - Sucursal QM Guatemala', 'Zona 10, Ciudad de Guatemala', 'NIT 9876543-2'),
    'QM México': ('QuetzalMart, S.A. - Sucursal QM México', 'Col. Roma Norte, Ciudad de México', 'RFC QME-260101-AB1'),
    'QM El Salvador': ('QuetzalMart, S.A. - Sucursal QM El Salvador', 'Col. Escalón, San Salvador', 'NIT 0614-010126-101-1'),
}

FACTURAS = [
    {
        'codigo': 'PRV001', 'proveedor': 'Distribuidora Maya Alimentos, S.A.', 'id_fiscal': 'NIT 4521873-6',
        'direccion': 'Calzada Roosevelt 22-43, Zona 11, Guatemala', 'color': '#B45309',
        'serie': 'A-4471', 'fecha': '2026-09-08', 'vence': '2026-10-08', 'sucursal': 'QM Guatemala',
        'moneda': 'Q', 'iva': 0.12, 'estado': 'Vigente',
        'lineas': [('Arroz blanco 1 lb, fardo x 25', 40, 162.50), ('Frijol negro 1 lb, fardo x 25', 35, 187.00),
                   ('Aceite vegetal 900 ml, caja x 12', 20, 238.80), ('Azúcar morena 2.5 kg, fardo x 10', 25, 205.00)],
    },
    {
        'codigo': 'PRV002', 'proveedor': 'Bebidas del Pacífico, S.A.', 'id_fiscal': 'NIT 7810342-1',
        'direccion': 'Km 14.5 Carretera al Pacífico, Villa Nueva', 'color': '#0369A1',
        'serie': 'B-1290', 'fecha': '2026-08-20', 'vence': '2026-09-19', 'sucursal': 'QM Guatemala',
        'moneda': 'Q', 'iva': 0.12, 'estado': 'Vencido',
        'lineas': [('Agua pura 600 ml, paquete x 24', 60, 72.00), ('Jugo de naranja 1 L, caja x 12', 30, 168.00),
                   ('Refresco de cola 2.5 L, paquete x 6', 45, 98.40)],
    },
    {
        'codigo': 'PRV003', 'proveedor': 'Limpieza Total Centroamérica, S.A. de C.V.', 'id_fiscal': 'NIT 0614-230519-102-4',
        'direccion': 'Boulevard del Ejército Km 7, Soyapango, San Salvador', 'color': '#047857',
        'serie': 'CCF-0832', 'fecha': '2026-09-15', 'vence': '2026-10-15', 'sucursal': 'QM El Salvador',
        'moneda': 'US$', 'iva': 0.13, 'estado': 'Vigente',
        'lineas': [('Detergente en polvo 1 kg, caja x 12', 25, 21.60), ('Cloro 1 galón, caja x 4', 30, 9.80),
                   ('Desinfectante multiusos 1 L, caja x 12', 20, 18.90), ('Escobas de nylon', 15, 2.75)],
    },
    {
        'codigo': 'PRV004', 'proveedor': 'Empaques y Plásticos del Norte, S.A. de C.V.', 'id_fiscal': 'RFC EPN-110304-KJ8',
        'direccion': 'Av. Constitución 1450, Monterrey, Nuevo León', 'color': '#7C3AED',
        'serie': 'MX-20931', 'fecha': '2026-09-02', 'vence': '2026-10-02', 'sucursal': 'QM México',
        'moneda': 'MX$', 'iva': 0.16, 'estado': 'Vigente',
        'carga_manual': True,  # esta la subo a mano
        'lineas': [('Bolsa camiseta biodegradable, millar', 50, 385.00), ('Bote de basura con tapa 60 L', 30, 289.00),
                   ('Pelota de plástico infantil 23 cm, caja x 24', 15, 456.00)],
    },
    {
        'codigo': 'PRV005', 'proveedor': 'Suministros Comerciales Quetzal, S.A.', 'id_fiscal': 'NIT 6102987-4',
        'direccion': '6a. Avenida 3-15, Zona 9, Guatemala', 'color': '#BE123C',
        'serie': 'SC-0577', 'fecha': '2026-09-21', 'vence': '2026-10-21', 'sucursal': 'QM Guatemala',
        'moneda': 'Q', 'iva': 0.12, 'estado': 'Vigente',
        'lineas': [('Papel térmico 80 mm, caja x 50 rollos', 10, 395.00), ('Etiquetas de precio, rollo x 1000', 40, 28.50),
                   ('Uniforme de cajero (camisa y gabacha)', 18, 145.00), ('Canasta plástica de compras', 30, 42.00)],
    },
]

CONTRATOS = [
    {
        'empresa': 'Servicios de Limpieza Brillante, S.A.', 'id_fiscal': 'NIT 5532190-8', 'representante': 'Marta Lucía Ajú',
        'servicio': 'limpieza', 'detalle': 'limpieza diaria de piso de ventas, bodegas, sanitarios y áreas de carga, '
        'incluyendo insumos de limpieza y personal de dos turnos', 'sucursal': 'QM Guatemala',
        'inicio': '2026-01-01', 'fin': '2026-12-31', 'monto': 'Q 18,500.00 mensuales', 'estado': 'Vigente',
        'numero': 'OUT-2026-001', 'color': '#0E7490',
    },
    {
        'empresa': 'Seguridad Integral Centinela, S.A. de C.V.', 'id_fiscal': 'NIT 0614-150312-103-9', 'representante': 'José Ernesto Rivas',
        'servicio': 'seguridad', 'detalle': 'vigilancia armada las 24 horas, monitoreo de cámaras y control de acceso '
        'de proveedores en el área de carga', 'sucursal': 'QM El Salvador',
        'inicio': '2026-02-01', 'fin': '2027-01-31', 'monto': 'US$ 2,950.00 mensuales', 'estado': 'Vigente',
        'numero': 'OUT-2026-002', 'color': '#1E3A8A',
    },
    {
        'empresa': 'Transportes Rápidos del Istmo, S.A.', 'id_fiscal': 'NIT 3378451-2', 'representante': 'Carlos Humberto Pérez',
        'servicio': 'transporte', 'detalle': 'traslado semanal de mercadería entre el almacén central QM Guatemala y las '
        'sucursales de México y El Salvador, con seguro de carga incluido', 'sucursal': 'QM Guatemala',
        'inicio': '2026-03-01', 'fin': '2027-02-28', 'monto': 'Q 9,800.00 por viaje', 'estado': 'Vigente',
        'numero': 'OUT-2026-003', 'color': '#B45309',
    },
    {
        'empresa': 'TecnoSoporte Chapín, S.A.', 'id_fiscal': 'NIT 8890123-5', 'representante': 'Ana Gabriela Morales',
        'servicio': 'soporte de TI', 'detalle': 'soporte técnico del ERP Odoo, puntos de venta, red y equipo de cómputo, '
        'con tiempo de respuesta máximo de 4 horas hábiles', 'sucursal': 'QM Guatemala',
        'inicio': '2026-01-15', 'fin': '2027-01-14', 'monto': 'Q 7,200.00 mensuales', 'estado': 'Vigente',
        'numero': 'OUT-2026-004', 'color': '#4338CA',
    },
    {
        'empresa': 'Mantenimientos Industriales Azteca, S.A. de C.V.', 'id_fiscal': 'RFC MIA-090722-LP3', 'representante': 'Héctor Daniel Villarreal Cruz',
        'servicio': 'mantenimiento', 'detalle': 'mantenimiento preventivo y correctivo de refrigeradores, cuartos fríos, '
        'aire acondicionado e instalaciones eléctricas', 'sucursal': 'QM México',
        'inicio': '2025-07-01', 'fin': '2026-06-30', 'monto': 'MX$ 32,000.00 mensuales', 'estado': 'Vencido',
        'numero': 'OUT-2025-005', 'color': '#9F1239',
        'carga_manual': True,  # esta la subo a mano
    },
]


def dinero(moneda, valor):
    return f'{moneda} {valor:,.2f}'


def factura_html(f):
    cli = CLIENTE[f['sucursal']]
    filas, subtotal = [], 0
    for desc, cant, precio in f['lineas']:
        total = cant * precio
        subtotal += total
        filas.append(f'<tr><td>{desc}</td><td class="num">{cant}</td>'
                     f'<td class="num">{dinero(f["moneda"], precio)}</td><td class="num">{dinero(f["moneda"], total)}</td></tr>')
    iva = round(subtotal * f['iva'], 2)
    return f"""<html><head><meta charset="utf-8">{ESTILO.replace('VAR_COLOR', f['color'])}</head><body>
<div class="cab"><div><div class="marca">{f['proveedor']}</div>{f['direccion']}<br>{f['id_fiscal']} - Código QuetzalMart {f['codigo']}</div>
<div class="der"><h1>FACTURA</h1>Serie y número: <b>{f['serie']}</b><br>Fecha de emisión: {f['fecha']}<br>Vencimiento: {f['vence']}</div></div>
<div class="caja"><b>Cliente:</b> {cli[0]}<br>{cli[1]} - {cli[2]}<br><b>Condición de pago:</b> crédito 30 días</div>
<table class="det"><tr><th>Descripción</th><th class="num">Cantidad</th><th class="num">Precio unitario</th><th class="num">Total</th></tr>
{''.join(filas)}
<tr class="tot"><td colspan="3" class="num">Subtotal</td><td class="num">{dinero(f['moneda'], subtotal)}</td></tr>
<tr class="tot"><td colspan="3" class="num">IVA {int(f['iva'] * 100)} %</td><td class="num">{dinero(f['moneda'], iva)}</td></tr>
<tr class="tot"><td colspan="3" class="num">TOTAL</td><td class="num">{dinero(f['moneda'], subtotal + iva)}</td></tr></table>
<p style="margin-top:24px">Mercadería entregada en {f['sucursal']}. Favor de emitir el pago a nombre de {f['proveedor'].rstrip('.')}.</p>
{PIE}</body></html>"""


def contrato_html(c):
    cli = CLIENTE[c['sucursal']]
    return f"""<html><head><meta charset="utf-8">{ESTILO.replace('VAR_COLOR', c['color'])}</head><body>
<div class="cab"><div><div class="marca">QuetzalMart, S.A.</div>Departamento Legal - Contratos de servicios</div>
<div class="der"><h1>CONTRATO DE OUTSOURCING</h1>No. <b>{c['numero']}</b><br>Sucursal: {c['sucursal']}</div></div>
<h2>Partes</h2>
<p><b>EL CONTRATANTE:</b> {cli[0]}, con domicilio en {cli[1]}, {cli[2]}, representada por su Gerente General.
<b>EL PRESTADOR:</b> {c['empresa']}, {c['id_fiscal']}, representada por {c['representante']}.</p>
<h2>Primera - Objeto</h2>
<p>EL PRESTADOR se obliga a brindar a EL CONTRATANTE el servicio de <b>{c['servicio']}</b>, que comprende {c['detalle']}.
El personal asignado depende laboralmente de EL PRESTADOR, quien cubre salarios, prestaciones y cuotas de seguridad social.</p>
<h2>Segunda - Plazo</h2>
<p>El contrato tiene vigencia del <b>{c['inicio']}</b> al <b>{c['fin']}</b>. Puede prorrogarse por escrito con 30 días de anticipación.</p>
<h2>Tercera - Contraprestación</h2>
<p>EL CONTRATANTE pagará <b>{c['monto']}</b> más impuestos, contra factura emitida dentro de los primeros cinco días de cada mes.</p>
<h2>Cuarta - Niveles de servicio y confidencialidad</h2>
<p>EL PRESTADOR cumplirá los niveles de servicio anexos, guardará reserva sobre la información de QuetzalMart y responderá por los
daños que su personal cause a las instalaciones o a la mercadería.</p>
<h2>Quinta - Terminación</h2>
<p>Cualquiera de las partes puede dar por terminado el contrato con aviso escrito de 30 días o de inmediato por incumplimiento grave.</p>
<div class="caja">Estado del contrato: <b>{c['estado']}</b></div>
<div class="firmas"><div><div class="linea">Por QuetzalMart, S.A.</div></div><div><div class="linea">{c['representante']}<br>{c['empresa']}</div></div></div>
{PIE}</body></html>"""


def main():
    HTML.mkdir(parents=True, exist_ok=True)
    manifiesto = []
    for f in FACTURAS:
        nombre = f'Factura {f["serie"]} - {f["proveedor"].split(",")[0]}'
        archivo = f'factura_{f["codigo"]}_{f["serie"]}'
        (HTML / f'{archivo}.html').write_text(factura_html(f), encoding='utf-8')
        manifiesto.append({'archivo': archivo, 'nombre': f'{nombre}.pdf', 'carpeta': 'Facturas de proveedores',
                           'categoria': 'Finanzas', 'etiquetas': [f['sucursal'], f['estado'], 'Proveedor'],
                           'carga_manual': f.get('carga_manual', False)})
    for c in CONTRATOS:
        nombre = f'Contrato {c["numero"]} - {c["servicio"][0].upper() + c["servicio"][1:]} - {c["empresa"].split(",")[0]}'
        archivo = f'contrato_{c["numero"]}'
        (HTML / f'{archivo}.html').write_text(contrato_html(c), encoding='utf-8')
        manifiesto.append({'archivo': archivo, 'nombre': f'{nombre}.pdf', 'carpeta': 'Contratos de outsourcing',
                           'categoria': 'Legal', 'etiquetas': [c['sucursal'], c['estado'], 'Outsourcing'],
                           'carga_manual': c.get('carga_manual', False)})
    (BASE / 'manifiesto.json').write_text(json.dumps(manifiesto, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f'{len(manifiesto)} documentos en {HTML}')


if __name__ == '__main__':
    main()
