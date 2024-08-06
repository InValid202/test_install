# © 2013-2014 ACSONE SA (<https://acsone.eu>).
# © 2014 Serv. Tecnol. Avanzados - Pedro M. Baeza
# © 2016 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class AccountMove(models.Model):
    _inherit = "account.move"

    payment_order_id = fields.Many2one(
        comodel_name="account.payment.order",
        string="Payment Order",
        copy=False,
        readonly=True,
        check_company=True,
    )
    payment_order_ok = fields.Boolean(compute="_compute_payment_order_ok")
    # we restore this field from <=v11 for now for preserving behavior
    # TODO: Check if we can remove it and base everything in something at
    # payment mode or company level
    reference_type = fields.Selection(
        selection=[("none", "Free Reference"), ("structured", "Structured Reference")],
        readonly=True,
        states={"draft": [("readonly", False)]},
        default="none",
    )
    payment_order_count = fields.Integer(
        string='Payment Order Count',
        compute='_compute_payment_order',
    )
    payment_type = fields.Selection(
        selection=[("inbound", "Inbound"), ("outbound", "Outbound")],
        readonly=True,
    )

    def _compute_payment_order(self):
        """docstring for _compute_payment_order"""
        for rec in self:
            PayOrder = self.env['account.payment.order']
            APL = self.env["account.payment.line"]
            for line in rec.line_ids:
                pay_line = APL.search([('move_line_id', '=', line.id)])
                if pay_line:
                    pay_order = pay_line.mapped('order_id')
                    PayOrder |= pay_order
            rec.payment_order_count = len(PayOrder)

    def action_view_payment_order(self):
        PayOrder = self.env['account.payment.order']
        APL = self.env["account.payment.line"]
        for line in self.line_ids:
            pay_line = APL.search([('move_line_id', '=', line.id)])
            if pay_line:
                pay_order = pay_line.mapped('order_id')
                PayOrder |= pay_order
        objs = PayOrder
        action = self.sudo().env.ref('account_payment_order.account_payment_order_outbound_action').read()[0]
        view_id = self.sudo().env.ref('account_payment_order.account_payment_order_form').id
        if len(objs) > 1:
            action['domain'] = [('id', 'in', objs.ids)]
        elif len(objs) == 1:
            action['views'] = [(view_id, 'form')]
            action['res_id'] = objs.ids[0]
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action

    @api.depends("payment_mode_id", "line_ids", "line_ids.payment_mode_id")
    def _compute_payment_order_ok(self):
        for move in self:
            payment_mode = move.line_ids.filtered(lambda x: not x.reconciled).mapped(
                "payment_mode_id"
            )[:1]
            if not payment_mode:
                payment_mode = move.payment_mode_id
            move.payment_order_ok = payment_mode.payment_order_ok

    def _prepare_new_payment_order(self, payment_mode=None):
        self.ensure_one()
        if payment_mode is None:
            payment_mode = self.env["account.payment.mode"]
        vals = {"payment_mode_id": payment_mode.id or self.payment_mode_id.id}
        # other important fields are set by the inherit of create
        # in account_payment_order.py
        return vals

    def get_account_payment_domain(self, payment_mode, partner):
        return [("payment_mode_id", "=", payment_mode.id), ('partner_id', '=', partner), ("state", "=", "draft")]

    @api.depends('amount_residual', 'move_type', 'state', 'company_id')
    def _compute_payment_state(self):
        res = super(AccountMove, self)._compute_payment_state()
        PayOrder = self.env['account.payment.order']
        APL = self.env["account.payment.line"]
        for rec in self:
            for line in rec.line_ids:
                pay_line = APL.search([('move_line_id', '=', line.id)])
                if pay_line:
                    pay_order = pay_line.mapped('order_id')
                    PayOrder |= pay_order
            objs = PayOrder
            if objs:
                for obj in objs:
                    if obj.state not in ('draft', 'cancel'):
                        rec.payment_state == 'in_payment'
        return res

    def create_account_payment_line(self):
        apoo = self.env["account.payment.order"]
        result_payorder_ids = []
        action_payment_type = "debit"
        partner = False
        payorder = False
        for move in self:
            if move.state != "posted":
                raise UserError(_("The invoice %s is not in Posted state") % move.name)
            applicable_lines = move.line_ids.filtered(
                lambda x: (
                    not x.reconciled
                    and x.payment_mode_id.payment_order_ok
                    and x.account_id.account_type in ("asset_receivable", "liability_payable")
                    and not any(
                        p_state in ("draft", "open", "generated")
                        for p_state in x.payment_line_ids.mapped("state")
                    )
                )
            )
            if not applicable_lines:
                raise UserError(
                    _(
                        "No Payment Line created for invoice %s because "
                        "it already exists or because this invoice is "
                        "already paid."
                    )
                    % move.name
                )
            partner_line = applicable_lines.mapped("partner_id")
            if not partner:
                partner = partner_line.id
            elif partner != partner_line.id:
                raise UserError(_("Payment for the same partner only"))
            payment_modes = applicable_lines.mapped("payment_mode_id")
            if not payment_modes:
                raise UserError(_("No Payment Mode on invoice %s") % move.name)
            for payment_mode in payment_modes:
                if not payorder:
                    payorder = apoo.search(
                        move.get_account_payment_domain(payment_mode, partner), limit=1
                    )
                new_payorder = False
                if not payorder:
                    payorder = apoo.create(
                        move._prepare_new_payment_order(payment_mode)
                    )
                    new_payorder = True
                result_payorder_ids.append(payorder.id)
                action_payment_type = payorder.payment_type
                count = 0
                for line in applicable_lines.filtered(
                    lambda x: x.payment_mode_id == payment_mode
                ):
                    line.create_payment_line_from_move_line(payorder)
                    count += 1
                if new_payorder:
                    move.message_post(
                        body=_(
                            "%(count)d payment lines added to the new draft payment "
                            "order %(name)s which has been automatically created.",
                            count=count,
                            name=payorder.name,
                        )
                    )
                else:
                    move.message_post(
                        body=_(
                            "%(count)d payment lines added to the existing draft "
                            "payment order %(name)s.",
                            count=count,
                            name=payorder.name,
                        )
                    )
        payorder.partner_id = partner
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "account_payment_order.account_payment_order_%s_action"
            % action_payment_type,
        )
        if len(result_payorder_ids) == 1:
            action.update(
                {
                    "view_mode": "form,tree,pivot,graph",
                    "res_id": payorder.id,
                    "views": False,
                }
            )
        else:
            action.update(
                {
                    "view_mode": "tree,form,pivot,graph",
                    "domain": "[('id', 'in', %s)]" % result_payorder_ids,
                    "views": False,
                }
            )
        return action
