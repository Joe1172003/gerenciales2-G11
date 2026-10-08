import xmlrpc.client
import random
from datetime import datetime, timedelta

# ==========================================
# CONFIGURACIÓN DEL SERVIDOR ODOO
# ==========================================
URL = ""  # URL de tu servidor Odoo
DB = ""
USER = ""  # Tu correo de admin
PASS = ""  # Usa la nueva si ya la cambiaste

# ==========================================
# CONEXIÓN
# ==========================================
common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(URL))
uid = common.authenticate(DB, USER, PASS, {})
models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(URL))

if not uid:
    print("Error de autenticación. Verifica tus credenciales.")
    exit()

print("Conectado con éxito a Odoo!")


def ejecutar(modelo, metodo, *args, **kwargs):
    return models.execute_kw(DB, uid, PASS, modelo, metodo, args, kwargs)


# 1. Obtener los 60 clientes importados
cliente_ids = ejecutar('res.partner', 'search', [
                       ('email', 'ilike', '@example.com')])
if not cliente_ids:
    print("No se encontraron clientes con referencia 'CLI...'. Importa el CSV primero.")
    exit()

# 2. Obtener productos de la tienda
producto_ids = ejecutar('product.product', 'search', [('sale_ok', '=', True)])
if not producto_ids:
    print("No hay productos disponibles para la venta. Espera a que Persona 2 los suba.")
    exit()

# 3. Obtener equipos de venta (Guatemala, México, El Salvador)
equipos_ids = ejecutar('crm.team', 'search', [])

print(f"Encontrados {len(cliente_ids)} clientes, {len(producto_ids)} productos y {len(equipos_ids)} equipos de venta.")

# ==========================================
# GENERAR 150 VENTAS CONFIRMADAS Y 20 COTIZACIONES
# ==========================================
TOTAL_VENTAS = 150
TOTAL_COTIZACIONES = 20

ventas_creadas = []
cotizaciones_creadas = []


def crear_orden(es_cotizacion=False):
    cliente = random.choice(cliente_ids)
    equipo = random.choice(equipos_ids) if equipos_ids else False

    # Datos de la orden
    order_data = {
        'partner_id': cliente,
        'team_id': equipo,
    }

    order_id = ejecutar('sale.order', 'create', order_data)

    # Agregar de 1 a 4 productos aleatorios a la orden
    for _ in range(random.randint(1, 4)):
        prod_id = random.choice(producto_ids)
        line_data = {
            'order_id': order_id,
            'product_id': prod_id,
            'product_uom_qty': random.randint(1, 5)
        }
        ejecutar('sale.order.line', 'create', line_data)

    return order_id


print("Creando 150 ventas...")
for i in range(TOTAL_VENTAS):
    oid = crear_orden(es_cotizacion=False)
    # Confirmar venta
    ejecutar('sale.order', 'action_confirm', [oid])
    ventas_creadas.append(oid)
    if (i+1) % 30 == 0:
        print(f"Creadas y confirmadas {i+1}/150 ventas")

print("Creando 20 cotizaciones...")
for i in range(TOTAL_COTIZACIONES):
    oid = crear_orden(es_cotizacion=True)
    # Quedan en estado 'draft' por defecto
    cotizaciones_creadas.append(oid)
    if (i+1) % 5 == 0:
        print(f"Creadas {i+1}/20 cotizaciones")

# ==========================================
# GENERAR 50 FACTURAS DESDE LAS VENTAS
# ==========================================
print("Generando y publicando 50 facturas...")
ventas_a_facturar = random.sample(ventas_creadas, 50)

for idx, oid in enumerate(ventas_a_facturar):
    # Crear la factura desde la orden de venta
    invoice_ids = ejecutar('sale.order', '_create_invoices', [oid])
    if invoice_ids:
        # Publicar la factura (estado 'posted')
        ejecutar('account.move', 'action_post', [invoice_ids[0]])
    if (idx+1) % 10 == 0:
        print(f"Facturadas {idx+1}/50")

print("Proceso finalizado. Verifica los datos en Odoo.")
