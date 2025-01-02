# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

# Copyright (c) 2005-2006 Axelor SARL. (http://www.axelor.com)

from odoo import api, models

class HrLeave(models.Model):
    _inherit = "hr.leave"

    @api.constrains("state", "number_of_days", "holiday_status_id")
    def _check_holidays(self):
        for holiday in self:
            if holiday.holiday_status_id.allows_negative:
                continue
            super()._check_holidays()