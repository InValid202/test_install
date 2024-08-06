# -*- coding: utf-8 -*-

from odoo import fields, models, api, _


class Cheque(models.Model):
    _inherit = 'account.cheque'

    payment_order_id = fields.Many2one(
        comodel_name='account.payment.order',
        string='Payment Order',
    )
