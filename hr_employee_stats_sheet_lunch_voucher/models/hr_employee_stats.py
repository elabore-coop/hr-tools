from odoo import fields, models, api

class HrEmployeeStats(models.Model):
    _inherit = "hr.employee.stats"

    lunch_voucher = fields.Integer("Lunch Voucher", compute="_compute_lunch_voucher")

    @api.depends("total_hours")
    def _compute_lunch_voucher(self):
        for stat in self:
            stat.lunch_voucher = 0
            if stat.date and stat.employee_id:
                stat._get_lunch_voucher()
    
    def _get_lunch_voucher(self):
        #do not factorize this method with _compute_lunch_voucher to be used in other modules
        self.ensure_one()
        if self.total_hours >= self.env.company.lunch_voucher_min_worked_hours:
            self.lunch_voucher = 1 
