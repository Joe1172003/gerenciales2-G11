-- Consulta 1: Conteo de ventas confirmadas
SELECT COUNT(*) AS ventas
FROM sale_order WHERE state = 'sale';

-- Consulta 2: Conteo de cotizaciones
SELECT COUNT(*) AS cotizaciones FROM sale_order
WHERE state IN ('draft', 'sent');

-- Consulta 3: Conteo de clientes distintos y productos vendidos
SELECT COUNT(DISTINCT o.partner_id) AS clientes,
       COUNT(DISTINCT l.product_id) AS productos
FROM sale_order o
JOIN sale_order_line l ON l.order_id = o.id
WHERE o.state = 'sale';

-- Consulta 4: Conteo de facturas emitidas y publicadas
SELECT COUNT(*) AS facturas FROM account_move
WHERE move_type = 'out_invoice'
  AND state = 'posted';

-- Consulta 5: Conteo de oportunidades en el CRM agrupadas por equipo
SELECT t.name->>'en_US' AS equipo,
       COUNT(l.id) AS oportunidades
FROM crm_lead l
JOIN crm_team t ON t.id = l.team_id
GROUP BY 1;

-- Consulta 6: Últimos 10 correos enviados desde el sistema (para verificar reglas)
SELECT subject, model, create_date
FROM mail_message WHERE subject IS NOT NULL
ORDER BY id DESC LIMIT 10;
