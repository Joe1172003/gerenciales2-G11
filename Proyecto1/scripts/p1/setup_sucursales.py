# Crea las 3 sucursales como almacenes y configura el sitio web
company = env.ref('base.main_company')
settings = env['res.config.settings'].create({
    'group_stock_multi_locations': True,
})
settings.execute()

Partner = env['res.partner']
def direccion(nombre, ciudad, pais):
    p = Partner.search([('name', '=', nombre), ('parent_id', '=', company.partner_id.id)], limit=1)
    vals = {'name': nombre, 'type': 'delivery', 'parent_id': company.partner_id.id,
            'city': ciudad, 'country_id': env.ref(pais).id}
    return p.write(vals) and p if p else Partner.create(vals)

sucursales = [
    ('QM Guatemala', 'QMGT', 'Ciudad de Guatemala', 'base.gt'),
    ('QM México', 'QMMX', 'Ciudad de México', 'base.mx'),
    ('QM El Salvador', 'QMSV', 'San Salvador', 'base.sv'),
]
Warehouse = env['stock.warehouse']
central = env.ref('stock.warehouse0')
for nombre, code, ciudad, pais in sucursales:
    partner = direccion(nombre, ciudad, pais)
    wh = central if code == 'QMGT' else Warehouse.search([('code', '=', code)], limit=1)
    vals = {'name': nombre, 'code': code, 'partner_id': partner.id}
    if wh:
        wh.write(vals)
    else:
        Warehouse.create(dict(vals, company_id=company.id))

es = env['res.lang']._activate_lang('es_419')
web = env['website'].search([], limit=1)
web.write({
    'name': 'QuetzalMart',
    'domain': 'https://quetzalmart-g11.duckdns.org',
    'default_lang_id': es.id,
    'language_ids': [(6, 0, es.ids)],
})
env.cr.commit()
for w in Warehouse.search([], order='id'):
    print('OK', w.code, w.name, w.partner_id.country_id.code)
print('OK web', web.name, web.default_lang_id.code)
