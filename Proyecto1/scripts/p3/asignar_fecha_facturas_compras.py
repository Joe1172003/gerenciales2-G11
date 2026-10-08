if not records:
    raise UserError("Selecciona las facturas de las compras.")

fecha = "2026-10-06"
prefijos = ("QMGT-MAT-", "QMMX-MAT-", "QMSV-MAT-")

for factura in records:
    if factura.move_type != "in_invoice" or factura.state != "draft":
        raise UserError("La seleccion debe contener solo facturas de proveedor en borrador.")
    if factura.company_id != env.company:
        raise UserError("Hay una factura de otra empresa.")
    compras = factura.invoice_line_ids.purchase_line_id.order_id
    if len(compras) != 1:
        raise UserError("Cada factura debe estar vinculada a una sola compra.")
    if not (compras.origin or "").startswith(prefijos):
        raise UserError("Una factura no pertenece a la carga de materiales. Excluye el piloto.")
    if compras.state not in ("purchase", "done"):
        raise UserError("Hay una compra sin confirmar.")
    if factura.invoice_date and str(factura.invoice_date) != fecha:
        raise UserError("Hay una factura con otra fecha. Revisala antes de continuar.")

records.filtered(lambda factura: not factura.invoice_date).write({"invoice_date": fecha})

action = {
    "type": "ir.actions.act_window",
    "name": "Facturas de las compras seleccionadas",
    "res_model": "account.move",
    "view_mode": "list,form",
    "domain": [("id", "in", records.ids)],
    "context": {"default_move_type": "in_invoice"},
    "target": "current",
}
