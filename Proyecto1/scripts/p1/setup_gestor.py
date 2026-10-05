# Estructura del gestor documental: grupos, almacenamiento, carpetas, categorias y etiquetas
env = env(context=dict(env.context, lang='es_419'))


def get_or_create(model, domain, vals):
    rec = env[model].search(domain, limit=1)
    if rec:
        rec.write(vals)
        return rec
    return env[model].create(vals)


# Gerencia ve todo, Compras y RRHH solo su carpeta
gerencia = get_or_create('dms.access.group', [('name', '=', 'Gerencia')], {
    'name': 'Gerencia', 'perm_create': True, 'perm_write': True, 'perm_unlink': True,
    'group_ids': [(6, 0, [env.ref('base.group_system').id])],
})
compras = get_or_create('dms.access.group', [('name', '=', 'Compras')], {
    'name': 'Compras', 'perm_create': True, 'perm_write': True, 'perm_unlink': False,
    'group_ids': [(6, 0, [env.ref('purchase.group_purchase_user').id])],
})
rrhh = get_or_create('dms.access.group', [('name', '=', 'Recursos Humanos')], {
    'name': 'Recursos Humanos', 'perm_create': True, 'perm_write': True, 'perm_unlink': False,
    'group_ids': [(6, 0, [env.ref('hr.group_hr_user').id])],
})

# los administradores tambien manejan el gestor
env.ref('base.group_system').write({'implied_ids': [(4, env.ref('dms.group_dms_manager').id)]})

storage = get_or_create('dms.storage', [('name', '=', 'Almacenamiento QuetzalMart')], {
    'name': 'Almacenamiento QuetzalMart', 'save_type': 'database',
})

raiz = get_or_create('dms.directory', [('name', '=', 'Documentos QuetzalMart'), ('is_root_directory', '=', True)], {
    'name': 'Documentos QuetzalMart', 'is_root_directory': True, 'storage_id': storage.id,
    'group_ids': [(6, 0, gerencia.ids)],
})

subcarpetas = [
    ('Facturas de proveedores', compras),
    ('Contratos de outsourcing', None),
    ('Contratos de empleados', rrhh),
    ('Facturas emitidas', None),
]
for nombre, grupo_extra in subcarpetas:
    get_or_create('dms.directory', [('name', '=', nombre), ('parent_id', '=', raiz.id)], {
        'name': nombre, 'parent_id': raiz.id, 'inherit_group_ids': True,
        'group_ids': [(6, 0, grupo_extra.ids if grupo_extra else [])],
    })

for nombre in ('Finanzas', 'Legal', 'Recursos Humanos'):
    get_or_create('dms.category', [('name', '=', nombre)], {'name': nombre})

# etiquetas sin categoria para poder usarlas en cualquier documento
etiquetas = [
    ('QM Guatemala', 1), ('QM México', 2), ('QM El Salvador', 3),  # sucursal
    ('Vigente', 10), ('Vencido', 9),                               # estado
    ('Proveedor', 4), ('Outsourcing', 5), ('Empleado', 6),         # tipo
]
Tag = env['dms.tag']
for nombre, color in etiquetas:
    vals = {'name': nombre}
    if 'color' in Tag._fields:
        vals['color'] = color
    get_or_create('dms.tag', [('name', '=', nombre)], vals)

env.cr.commit()
for d in env['dms.directory'].search([], order='parent_path'):
    print('OK carpeta', d.complete_name, '| grupos:', ', '.join(d.complete_group_ids.mapped('name')))
print('OK categorias', ', '.join(env['dms.category'].search([]).mapped('name')))
print('OK etiquetas', ', '.join(Tag.search([]).mapped('name')))
