# © 2016 Akretion (<https://www.akretion.com>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api


class AccountInvoicePaymentLineMulti(models.TransientModel):
    _name = "account.invoice.payment.line.multi"
    _description = "Create payment lines from invoice tree view"

    payment_mode_id = fields.Many2one(
        comodel_name='account.payment.mode',
        string='Payment Mode',
    )
    payment_type = fields.Selection(
        selection=[
            ('inbound', 'Inbound'),
            ('outbound', 'Outbound')
        ],
        string='Payment Type',
    )

    @api.model
    def default_get(self, fields):
        res = super(AccountInvoicePaymentLineMulti, self).default_get(fields)
        active_id = self.env.context['active_ids']
        move = self.env['account.move'].browse(active_id)
        if move and move[0].move_type == 'in_invoice':
            payment_type = 'outbound'
        else:
            payment_type = 'inbound'
        res['payment_type'] = payment_type
        return res

    def run(self):
        self.ensure_one()
        assert (
            self._context["active_model"] == "account.move"
        ), "Active model should be account.move"
        invoices = self.env["account.move"].browse(self._context["active_ids"])
        if self.payment_mode_id:
            for inv in invoices:
                inv.update({'payment_mode_id': self.payment_mode_id.id})
        action = invoices.create_account_payment_line()
        return action
