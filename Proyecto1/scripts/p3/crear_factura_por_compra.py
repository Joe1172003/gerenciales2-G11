if not records:
    raise UserError("Selecciona las ordenes de compra que deseas facturar.")

prefixes = ("QMGT-MAT-", "QMMX-MAT-", "QMSV-MAT-")

# Revisar toda la seleccion antes de crear facturas
for order in records:
    if not (order.origin or "").startswith(prefixes):
        raise UserError("%s no pertenece a la carga de materiales. Excluye el piloto y otras compras." % order.name)
    if order.company_id != env.company:
        raise UserError("%s pertenece a otra empresa." % order.name)
    if order.state not in ("purchase", "done"):
        raise UserError("%s no esta confirmada." % order.name)
    lines = order.order_line.filtered(lambda line: not line.display_type)
    if not lines:
        raise UserError("%s no tiene productos." % order.name)
    for line in lines:
        if float_compare(line.qty_received, line.product_qty,
                         precision_rounding=line.product_uom.rounding) != 0:
            raise UserError("%s tiene cantidades recibidas diferentes de las compradas." % order.name)
    existing = order.invoice_ids.filtered(
        lambda bill: bill.move_type == "in_invoice" and bill.state != "cancel"
    )
    if existing:
        linked_orders = existing.invoice_line_ids.purchase_line_id.order_id
        if len(existing) != 1 or linked_orders != order or order.invoice_status != "invoiced":
            raise UserError("Revisa las facturas existentes de %s antes de continuar." % order.name)
    elif order.invoice_status != "to invoice":
        raise UserError("%s no tiene cantidades pendientes de facturar." % order.name)

bills = env["account.move"]
for order in records:
    bill = order.invoice_ids.filtered(
        lambda invoice: invoice.move_type == "in_invoice" and invoice.state != "cancel"
    )
    if not bill:
        # Una llamada por orden evita agrupar compras del mismo proveedor
        order.action_create_invoice()
        bill = order.invoice_ids.filtered(
            lambda invoice: invoice.move_type == "in_invoice" and invoice.state != "cancel"
        )
    if len(bill) != 1 or bill.invoice_line_ids.purchase_line_id.order_id != order:
        raise UserError("No se obtuvo una factura individual para %s." % order.name)
    if float_compare(bill.amount_total, order.amount_total,
                     precision_rounding=order.currency_id.rounding) != 0:
        raise UserError("El total de la factura no coincide con %s." % order.name)
    bills |= bill

action = {
    "type": "ir.actions.act_window",
    "name": "Facturas de las compras seleccionadas",
    "res_model": "account.move",
    "view_mode": "list,form",
    "domain": [("id", "in", bills.ids)],
    "context": {"default_move_type": "in_invoice"},
    "target": "current",
}
