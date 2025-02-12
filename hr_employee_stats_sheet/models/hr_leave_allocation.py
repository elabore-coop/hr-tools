# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields

class HrLeaveAllocation(models.Model):
    _inherit = "hr.leave.allocation"

    timesheet_sheet_id = fields.Many2one("hr_timesheet.sheet", string="Timesheet Sheet", readonly=True)
