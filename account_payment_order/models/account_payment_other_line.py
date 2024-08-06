# -*- coding: utf-8 -*-

from odoo import fields, models, api, _


class AccountPaymentOtherLine(models.Model):
    _name = 'account.payment.other.line'
    _description = 'Account Payment Other Line'

    payment_id = fields.Many2one(
        comodel_name='account.payment.order',
        string='Payment Order',
    )
    payment_method_id = fields.Many2one(
        'account.payment.method.multi',
        string='Method',
        required='False'
    )
#     payment_mode_id = fields.Many2one(
#         comodel_name="account.payment.mode",
#         required=True,
#         check_company=True,
#     )
    company_id = fields.Many2one(
        related="payment_id.company_id", store=True, readonly=True
    )
    label = fields.Char(
        string='Label',
    )
    bank_id = fields.Many2one(
        'res.bank',
        string="Bank"
    )
    cheque_number = fields.Char(
        'Number'
    )
    cheque_date = fields.Date(
        'Date'
    )
    cheque_id = fields.Many2one(
        'account.cheque',
        string='Cheque',
        readonly=False,
        domain="[('state', '=','draft')]",
    )
    wht_id = fields.Many2one(
        'account.wht',
        string='WHT No.',
        readonly=False,
        domain="[('state', '=','draft')]",
    )
    paid_total = fields.Float(
        string = 'Total',
        required='True',
    )
#     is_cheque = fields.Boolean(
#         string='Is Cheque',
#         related='payment_mode_id.is_cheque',
#     )
#     is_wht = fields.Boolean(
#         string='WHT',
#         related='payment_mode_id.is_wht',
#     )
    payment_method_line_type = fields.Selection(
        [('cash','Cash'),
         ('cheque','Cheque'),
         ('bank','Bank'),
         ('discount','Discount'),
         ('wht', 'WHT'),
         ('ap','AP'),
         ('ar','AR'),
         ('advance_receipt', 'Advance Receipt'),
         ('other','Other')],
        'Payment Type',
        related='payment_method_id.type',
    )
