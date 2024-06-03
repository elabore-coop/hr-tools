# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, _

class Holidays(models.Model):
    _inherit = "hr.leave"

    def _timesheet_prepare_line_values(self, index, work_hours_data, day_date, work_hours_count):
        res = super()._timesheet_prepare_line_values(index, work_hours_data, day_date, work_hours_count)
        res['name'] = _("%s (%s/%s)",self.holiday_status_id.name, index + 1, len(work_hours_data))
        return res
