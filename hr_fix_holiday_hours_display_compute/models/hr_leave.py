from odoo import api, fields, models
from odoo.addons.resource.models.resource import float_to_time, HOURS_PER_DAY


class HolidaysRequest(models.Model):
    _inherit = "hr.leave"

    @api.multi
    @api.depends('number_of_days')
    def _compute_number_of_hours_display(self):
        for holiday in self:
            calendar = holiday.employee_id.resource_calendar_id or self.env.user.company_id.resource_calendar_id
            if holiday.date_from and holiday.date_to:
                number_of_hours = calendar.get_work_hours_count(holiday.date_from, holiday.date_to)
                holiday.number_of_hours_display = number_of_hours or (holiday.number_of_days * HOURS_PER_DAY)
            else:
                holiday.number_of_hours_display = 0