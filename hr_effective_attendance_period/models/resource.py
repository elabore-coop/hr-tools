from odoo import models, fields


class ResourceCalendarAttendance(models.Model):
    _inherit = "resource.calendar.attendance"

    effective_attendance_period = fields.Boolean('Effective Attendance Period', store=True)