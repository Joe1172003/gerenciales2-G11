# Datos de la empresa, idioma y usuario admin
# Necesita la variable QM_ADMIN_PW con la contraseña del admin
import os
gt = env.ref('base.gt')
gtq = env.ref('base.GTQ')
gtq.active = True
company = env.ref('base.main_company')
company.write({
    'name': 'QuetzalMart',
    'country_id': gt.id,
    'currency_id': gtq.id,
    'city': 'Ciudad de Guatemala',
    'street': 'Zona 10',
    'email': 'contacto@quetzalmart.example.com',
    'website': 'https://quetzalmart-g11.duckdns.org',
})
company.partner_id.write({'lang': 'es_419', 'tz': 'America/Guatemala'})
admin = env.ref('base.user_admin')
admin.write({'lang': 'es_419', 'tz': 'America/Guatemala', 'password': os.environ['QM_ADMIN_PW']})
env['ir.default'].set('res.partner', 'lang', 'es_419')
env['ir.default'].set('res.partner', 'tz', 'America/Guatemala')
env['ir.config_parameter'].set_param('web.base.url', 'https://quetzalmart-g11.duckdns.org')
env['ir.config_parameter'].set_param('web.base.url.freeze', 'True')
env.cr.commit()
print('OK', company.name, company.country_id.code, company.currency_id.name)
