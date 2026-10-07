-- Consultas SQL para el proyecto 1: ERP y gestor documental
-- NOTA para los demas: aqui deben de agregar todas las consultas que se les pidan en el proyecto
-- Nota de como trabaje: Base: quetzalmart (Cloud SQL, PostgreSQL 16) - usuario: consulta (solo lectura)


-- 1. Base de datos en la nube (Cloud SQL)
SELECT current_database() AS base,
       version()          AS motor,
       (SELECT count(*) FROM pg_settings WHERE name LIKE 'cloudsql.%') AS parametros_cloudsql;


-- 2. Modulos del ERP instalados
SELECT name AS modulo, state AS estado
FROM ir_module_module
WHERE name IN ('sale_management', 'purchase', 'stock', 'account', 'hr', 'crm',
               'website', 'website_sale', 'mass_mailing', 'base_automation',
               'website_crm', 'l10n_gt', 'dms')
ORDER BY name;


-- 3. Empresa, pais, moneda y plan contable
SELECT c.name           AS empresa,
       p.code           AS pais,
       cur.name         AS moneda,
       cur.symbol       AS simbolo,
       c.chart_template AS plan_contable
FROM res_company c
JOIN res_partner cp   ON cp.id = c.partner_id
JOIN res_country p    ON p.id = cp.country_id
JOIN res_currency cur ON cur.id = c.currency_id;


-- 4. Monedas activas y su tasa respecto al quetzal
SELECT cur.name AS moneda, cur.symbol AS simbolo, r.name AS fecha, r.rate AS unidades_por_gtq
FROM res_currency cur
LEFT JOIN res_currency_rate r ON r.currency_id = cur.id
WHERE cur.active
ORDER BY cur.name;


-- 5. Sucursales (almacenes de la misma compania)
SELECT w.code AS codigo, w.name AS sucursal, p.city AS ciudad, pa.code AS pais
FROM stock_warehouse w
JOIN res_partner p  ON p.id = w.partner_id
JOIN res_country pa ON pa.id = p.country_id
ORDER BY w.id;


-- 6. Impuestos de Guatemala
SELECT coalesce(name->>'es_419', name->>'en_US')               AS impuesto,
       amount                                                   AS porcentaje,
       type_tax_use                                             AS uso,
       coalesce(description->>'es_419', description->>'en_US') AS etiqueta
FROM account_tax
WHERE active
ORDER BY type_tax_use, amount DESC;


-- 7. Gestor documental: carpetas y cantidad de documentos
SELECT d.complete_name AS carpeta, count(f.id) AS documentos
FROM dms_directory d
LEFT JOIN dms_file f ON f.directory_id = d.id
GROUP BY d.complete_name
ORDER BY d.complete_name;


-- 8. Documentos con su categoria y etiquetas
SELECT d.name AS carpeta,
       f.name AS documento,
       coalesce(c.name->>'es_419', c.name->>'en_US') AS categoria,
       string_agg(coalesce(t.name->>'es_419', t.name->>'en_US'), ', ' ORDER BY t.id) AS etiquetas
FROM dms_file f
JOIN dms_directory d         ON d.id = f.directory_id
LEFT JOIN dms_category c     ON c.id = f.category_id
LEFT JOIN dms_file_tag_rel r ON r.fid = f.id
LEFT JOIN dms_tag t          ON t.id = r.tid
GROUP BY d.name, f.name, c.name
ORDER BY d.name, f.name;


-- 9. Documentos por tipo (minimo 5 de cada uno)
SELECT coalesce(t.name->>'es_419', t.name->>'en_US') AS tipo, count(r.fid) AS documentos
FROM dms_tag t
LEFT JOIN dms_file_tag_rel r ON r.tid = t.id
WHERE t.name->>'en_US' IN ('Proveedor', 'Outsourcing', 'Empleado')
GROUP BY 1
ORDER BY 1;


-- 10. Documentos por categoria
SELECT coalesce(c.name->>'es_419', c.name->>'en_US') AS categoria, count(f.id) AS documentos
FROM dms_category c
LEFT JOIN dms_file f ON f.category_id = c.id
GROUP BY 1
ORDER BY 1;


-- 11. Filtro por etiqueta: documentos vencidos
SELECT f.name AS documento, d.name AS carpeta
FROM dms_file f
JOIN dms_directory d    ON d.id = f.directory_id
JOIN dms_file_tag_rel r ON r.fid = f.id
JOIN dms_tag t          ON t.id = r.tid
WHERE t.name->>'en_US' = 'Vencido'
ORDER BY f.name;


-- 12. Filtro por dos etiquetas: facturas de proveedor de la sucursal Guatemala
SELECT f.name AS documento
FROM dms_file f
WHERE EXISTS (SELECT 1 FROM dms_file_tag_rel r JOIN dms_tag t ON t.id = r.tid
              WHERE r.fid = f.id AND t.name->>'en_US' = 'Proveedor')
  AND EXISTS (SELECT 1 FROM dms_file_tag_rel r JOIN dms_tag t ON t.id = r.tid
              WHERE r.fid = f.id AND t.name->>'en_US' = 'QM Guatemala')
ORDER BY f.name;


-- 13. Grupos de acceso del gestor y carpetas donde aplican
SELECT coalesce(g.name->>'es_419', g.name->>'en_US') AS grupo,
       g.perm_create AS crear, g.perm_write AS editar, g.perm_unlink AS borrar,
       string_agg(d.name, ', ' ORDER BY d.id) AS carpetas
FROM dms_access_group g
LEFT JOIN dms_directory_groups_rel dg ON dg.gid = g.id
LEFT JOIN dms_directory d             ON d.id = dg.aid
GROUP BY g.id, g.name, g.perm_create, g.perm_write, g.perm_unlink
ORDER BY g.id;


-- 14. Usuarios del sistema
SELECT u.login,
       p.name AS nombre,
       EXISTS (SELECT 1 FROM res_groups_users_rel gu
               JOIN ir_model_data x ON x.res_id = gu.gid AND x.model = 'res.groups'
               WHERE gu.uid = u.id AND x.module = 'base' AND x.name = 'group_system') AS administrador
FROM res_users u
JOIN res_partner p ON p.id = u.partner_id
WHERE u.active AND NOT u.share
ORDER BY u.id;

-- 15. Catalogo cargado y publicado en la tienda
SELECT count(*)                                AS productos,
       count(*) FILTER (WHERE is_published)    AS publicados,
       count(*) FILTER (WHERE is_storable)     AS con_inventario
FROM product_template
WHERE active AND default_code LIKE 'QMP%';


-- 16. Productos por categoria
SELECT c.complete_name AS categoria, count(t.id) AS productos
FROM product_template t
JOIN product_category c ON c.id = t.categ_id
WHERE t.default_code LIKE 'QMP%'
GROUP BY 1
ORDER BY 1;


-- 17. Existencias por sucursal
SELECT w.code AS sucursal,
       w.name AS almacen,
       count(DISTINCT q.product_id)   AS productos,
       sum(q.quantity)::numeric(12,2) AS unidades
FROM stock_warehouse w
JOIN stock_quant q ON q.location_id = w.lot_stock_id
GROUP BY w.code, w.name
ORDER BY w.code;


-- 18. Metodos de entrega publicados en la tienda
SELECT coalesce(name->>'es_419', name->>'en_US') AS metodo,
       delivery_type AS tipo,
       fixed_price   AS precio,
       is_published  AS publicado
FROM delivery_carrier
WHERE active
ORDER BY id;


-- 19. Proveedor de pago y transacciones
SELECT p.code  AS proveedor,
       p.state AS modo,
       count(t.id)                              AS transacciones,
       count(*) FILTER (WHERE t.state = 'done') AS exitosas
FROM payment_provider p
LEFT JOIN payment_transaction t ON t.provider_id = p.id
WHERE p.state <> 'disabled'
GROUP BY p.code, p.state;


-- 20. Pedidos hechos desde el sitio web
SELECT o.name           AS pedido,
       p.complete_name  AS cliente,
       o.amount_total   AS total,
       o.state          AS estado,
       o.date_order     AS fecha
FROM sale_order o
JOIN res_partner p ON p.id = o.partner_id
WHERE o.website_id IS NOT NULL
ORDER BY o.id DESC;


-- 21. Facturas emitidas y su estado de pago
SELECT m.name          AS factura,
       m.amount_total  AS total,
       m.payment_state AS pago,
       m.invoice_date  AS fecha
FROM account_move m
WHERE m.move_type = 'out_invoice' AND m.state = 'posted'
ORDER BY m.id DESC;


-- 22. PDF que la regla de automatizacion guardo en el gestor
SELECT count(*) AS pdf_en_carpeta
FROM dms_file f
JOIN dms_directory d ON d.id = f.directory_id
WHERE d.name = 'Facturas emitidas';


-- 23. Oportunidades que entraron por el formulario de contacto
SELECT l.name         AS oportunidad,
       l.contact_name AS contacto,
       l.email_from   AS correo,
       l.create_date  AS fecha
FROM crm_lead l
WHERE l.type = 'opportunity'
ORDER BY l.id DESC
LIMIT 10;


-- ================================
-- Ariel - compras y materiales
-- ================================

-- 1. Compras confirmadas
SELECT COUNT(*) AS compras_confirmadas
FROM purchase_order
WHERE state IN ('purchase', 'done');


-- 2. Facturas de proveedor publicadas
SELECT COUNT(*) AS facturas_proveedor_publicadas
FROM account_move
WHERE move_type = 'in_invoice'
    AND state = 'posted';


-- 3. Solicitudes de cotizacion sin confirmar
SELECT COUNT(*) AS solicitudes_sin_confirmar
FROM purchase_order
WHERE state IN ('draft', 'sent');


-- 4. Compras confirmadas por sucursal
SELECT sw.code AS codigo,
    sw.name AS sucursal,
    COUNT(*) AS compras_confirmadas
FROM purchase_order po
LEFT JOIN stock_picking_type spt ON spt.id = po.picking_type_id
LEFT JOIN stock_warehouse sw ON sw.id = spt.warehouse_id
WHERE po.state IN ('purchase', 'done')
GROUP BY sw.code, sw.name
ORDER BY sw.code;


-- 5. Materiales de sucursal
SELECT COUNT(*) AS materiales
FROM product_template t
JOIN product_category c ON c.id = t.categ_id
WHERE t.active
    AND c.name = 'Materiales de sucursal';


-- 6. Proveedores
SELECT COUNT(*) AS proveedores
FROM res_partner
WHERE active
    AND supplier_rank > 0;


-- 7. Recepcion y factura de las compras
-- Cuenta las compras recibidas completas y las que tienen una factura publicada
-- Señala compras con recepción incompleta, sin factura publicada o con varias facturas
WITH revision AS (
    SELECT po.id,
        COUNT(DISTINCT sp.id) FILTER (
            WHERE spt.code = 'incoming' AND sp.state = 'done'
        ) AS recepciones_hechas,
        COUNT(DISTINCT sp.id) FILTER (
            WHERE spt.code = 'incoming'
                AND sp.state NOT IN ('done', 'cancel')
        ) AS recepciones_pendientes,
        COUNT(DISTINCT pol.id) AS lineas,
        BOOL_AND(
            ABS(COALESCE(pol.qty_received, 0)
                - pol.product_qty) <= 0.000001
        ) AS cantidades_completas,
        COUNT(DISTINCT am.id) AS facturas,
        COUNT(DISTINCT am.id) FILTER (
            WHERE am.state = 'posted'
        ) AS facturas_publicadas
    FROM purchase_order po
    LEFT JOIN purchase_order_line pol
        ON pol.order_id = po.id AND pol.display_type IS NULL
    LEFT JOIN stock_move sm ON sm.purchase_line_id = pol.id
    LEFT JOIN stock_picking sp ON sp.id = sm.picking_id
    LEFT JOIN stock_picking_type spt ON spt.id = sp.picking_type_id
    LEFT JOIN account_move_line aml ON aml.purchase_line_id = pol.id
    LEFT JOIN account_move am
        ON am.id = aml.move_id
        AND am.move_type = 'in_invoice'
        AND am.state <> 'cancel'
    WHERE po.state IN ('purchase', 'done')
    GROUP BY po.id
),
resultado AS (
    SELECT *,
        COALESCE(
            lineas > 0
            AND recepciones_hechas > 0
            AND recepciones_pendientes = 0
            AND cantidades_completas,
            FALSE
        ) AS recepcion_completa
    FROM revision
)
SELECT COUNT(*) AS compras_revisadas,
    COUNT(*) FILTER (
        WHERE recepcion_completa
    ) AS compras_recibidas_completas,
    COUNT(*) FILTER (
        WHERE NOT recepcion_completa
    ) AS compras_con_recepcion_incompleta,
    COUNT(*) FILTER (
        WHERE facturas = 1 AND facturas_publicadas = 1
    ) AS compras_con_una_factura_publicada,
    COUNT(*) FILTER (
        WHERE facturas_publicadas = 0
    ) AS compras_sin_factura_publicada,
    COUNT(*) FILTER (
        WHERE facturas > 1
    ) AS compras_con_varias_facturas
FROM resultado;


-- 8. Resumen de cantidades
-- Muestra en una fila proveedores, materiales, compras confirmadas,
-- recepciones validadas, facturas publicadas y cotizaciones sin confirmar
WITH compras AS (
    SELECT id
    FROM purchase_order
    WHERE state IN ('purchase', 'done')
),
recepciones AS (
    SELECT DISTINCT sp.id
    FROM compras c
    JOIN purchase_order_line pol ON pol.order_id = c.id
    JOIN stock_move sm ON sm.purchase_line_id = pol.id
    JOIN stock_picking sp ON sp.id = sm.picking_id
    JOIN stock_picking_type spt ON spt.id = sp.picking_type_id
    WHERE spt.code = 'incoming'
      AND sp.state = 'done'
)
SELECT (SELECT COUNT(*)
        FROM res_partner
        WHERE active AND supplier_rank > 0) AS proveedores,
    (SELECT COUNT(*)
        FROM product_template t
        JOIN product_category c ON c.id = t.categ_id
        WHERE t.active
        AND c.name = 'Materiales de sucursal') AS materiales,
    (SELECT COUNT(*) FROM compras) AS compras_confirmadas,
    (SELECT COUNT(*) FROM recepciones) AS recepciones_validadas,
    (SELECT COUNT(*)
        FROM account_move
        WHERE move_type = 'in_invoice'
        AND state = 'posted') AS facturas_publicadas,
    (SELECT COUNT(*)
        FROM purchase_order
        WHERE state IN ('draft', 'sent')) AS cotizaciones_sin_confirmar;
