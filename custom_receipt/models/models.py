# -*- coding: utf-8 -*-

from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)


class CustomReceipt(models.Model):
    _inherit = 'account.move'

    paid_on_date = fields.Date(string='Paid on Date', compute='_compute_paid_on_date', invisble=True)

    def _compute_paid_on_date(self):
        try:
            for record in self:
                if record.state == 'posted' and record.payment_state == 'in_payment':
                    payment = self.env['account.payment'].search([('ref', '=', record.payment_reference)], limit=1)
                    record.paid_on_date = payment.date
                    # print(record.paid_on_date)
                else:
                    record.paid_on_date = False
        except Exception as e:
            for record in self:
                _logger.error(f"Failed to compute paid_on_date for record {record.id}: {e}")
                record.paid_on_date = False




