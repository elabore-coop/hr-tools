from odoo import fields, models, api

class HrTimesheetSheet(models.Model):
    _inherit = "hr_timesheet.sheet"

    lunch_voucher_count = fields.Integer("Lunch voucher Count", compute="_compute_lunch_voucher_count")

    @api.depends("employee_stats_ids.lunch_voucher")    
    def _compute_lunch_voucher_count(self):
        for sheet in self:
            sheet.lunch_voucher_count = 0
            if sheet.employee_stats_ids:
                for stat in sheet.employee_stats_ids:
                    sheet.lunch_voucher_count += stat.lunch_voucher

