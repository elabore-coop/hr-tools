
# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class HolidaysType(models.Model):
    _inherit = "hr.leave.type"

    # negative time off
    allows_negative = fields.Boolean(string='Allow Negative Leaves',
        help="If checked, users request can exceed the allocated days and balance can go in negative.")

    @api.depends('validity_start', 'validity_stop')
    def _compute_valid(self):
        res = super()._compute_valid()
        for holiday_type in res:
            if not holiday_type.valid:
                holiday_type.valid = holiday_type.allows_negative
