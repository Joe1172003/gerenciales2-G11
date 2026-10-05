# Crea o actualiza usuarios de Odoo a partir de /tmp/usuarios.json
# formato: [{"login", "name", "password", "perfil": "admin" o "bot"}]
# si el usuario ya existe no le cambia la contraseña
import json

PERFILES = {
    # integrantes: mismos permisos que el admin y contabilidad completa
    'admin': None,
    # bot de UiPath: contactos, productos e inventario, sin acceso a Ajustes
    'bot': [
        'base.group_user',
        'base.group_partner_manager',
        'stock.group_stock_manager',
        'sales_team.group_sale_salesman',
        'website.group_website_restricted_editor',
    ],
}

admin = env.ref('base.user_admin')
grupos_admin = admin.groups_id | env.ref('account.group_account_user')
Users = env['res.users'].with_context(no_reset_password=True)

with open('/tmp/usuarios.json', encoding='utf-8') as fh:
    datos = json.load(fh)

for d in datos:
    if d['perfil'] == 'admin':
        grupos = grupos_admin
    else:
        grupos = env['res.groups'].browse([env.ref(x).id for x in PERFILES[d['perfil']]])
    vals = {
        'name': d['name'],
        'email': d.get('email', d['login']),
        'lang': 'es_419',
        'tz': 'America/Guatemala',
        'groups_id': [(6, 0, grupos.ids)],
    }
    user = Users.search([('login', '=', d['login'])], limit=1)
    if user:
        user.write(vals)
        accion = 'actualizado'
    else:
        user = Users.create(dict(vals, login=d['login'], password=d['password']))
        accion = 'creado'
    print('OK', accion, user.login, '| admin' if user.has_group('base.group_system') else '| sin Ajustes')

# el admin tambien necesita ver el plan de cuentas
admin.write({'groups_id': [(4, env.ref('account.group_account_user').id)]})
env.cr.commit()
