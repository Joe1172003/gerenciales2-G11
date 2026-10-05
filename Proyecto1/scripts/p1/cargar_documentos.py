# Sube los PDF al gestor con su carpeta, categoria y etiquetas
# Los que tienen carga_manual se suben a mano desde Odoo
import base64
import json

# se sube con el usuario admin esto lo configure yo asi
env = env(user=env.ref('base.user_admin').id, context=dict(env.context, lang='es_419'))
raiz = env['dms.directory'].search([('name', '=', 'Documentos QuetzalMart'), ('is_root_directory', '=', True)], limit=1)

with open('/tmp/docs/manifiesto.json', encoding='utf-8') as fh:
    documentos = json.load(fh)

for doc in documentos:
    if doc['carga_manual']:
        print('OK omitido (carga manual):', doc['nombre'])
        continue
    carpeta = env['dms.directory'].search([('name', '=', doc['carpeta']), ('parent_id', '=', raiz.id)], limit=1)
    categoria = env['dms.category'].search([('name', '=', doc['categoria'])], limit=1)
    etiquetas = env['dms.tag'].search([('name', 'in', doc['etiquetas'])])
    if len(etiquetas) != len(doc['etiquetas']) or not carpeta or not categoria:
        raise ValueError(f"Falta carpeta, categoría o etiqueta para {doc['nombre']}")
    with open(f"/tmp/docs/pdf/{doc['archivo']}.pdf", 'rb') as fh:
        contenido = base64.b64encode(fh.read())
    vals = {'category_id': categoria.id, 'tag_ids': [(6, 0, etiquetas.ids)]}
    existente = env['dms.file'].search([('name', '=', doc['nombre']), ('directory_id', '=', carpeta.id)], limit=1)
    if existente:
        existente.write(vals)
        print('OK actualizado:', doc['nombre'])
    else:
        env['dms.file'].create(dict(vals, name=doc['nombre'], directory_id=carpeta.id, content=contenido))
        print('OK subido:', doc['nombre'])

env.cr.commit()
