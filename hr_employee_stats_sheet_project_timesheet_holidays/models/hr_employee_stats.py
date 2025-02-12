from odoo import models

class HrEmployeeStats(models.Model):
    _inherit = "hr.employee.stats"
 
    def get_total_hours_domain(self):
        '''
        if project_timesheet_holidays is installed, exclude timesheet generated from holidays to calculated total hours
        '''
        domain = super().get_total_hours_domain()
        if self.env.company.leave_timesheet_task_id:
            domain.append(("task_id", "!=", self.env.company.leave_timesheet_task_id.id),)
        return domain

