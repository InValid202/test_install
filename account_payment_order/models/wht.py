# -*- coding: utf-8 -*-

from odoo import fields, models, api, _


class WHT(models.Model):
    _inherit = 'account.wht'

    payment_order_count = fields.Integer(
        string='Payment Order Count',
        compute='_compute_payment_order',
    )

    def _compute_payment_order(self):
        """docstring for _compute_payment_order"""
        for rec in self:
            APL = self.env['account.payment.other.line']
            payline = APL.search([('wht_id', '=', rec.id)])
            if payline:
                payment = payline.mapped('payment_id')
                rec.payment_order_count = len(payment)
            else:
                rec.payment_order_count = 0

    def action_view_payment_order(self):
        APL = self.env['account.payment.other.line']
        payline = APL.search([('wht_id', '=', self.id)])
        payment = payline.mapped('payment_id')
        objs = payment
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
