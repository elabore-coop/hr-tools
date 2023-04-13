import math
import pytz
from datetime import datetime, timedelta
from pytz import timezone
from odoo import models, fields


class ResourceCalendarAttendance(models.Model):
    _inherit = "resource.calendar.attendance"

    effective_attendance_period = fields.Boolean('Effective Attendance Period', store=True)


class ResourceCalendar(models.Model):
    _inherit = "resource.calendar"

    def _retrieve_day_matching_attendances(self, day):
        domain = [
            ("calendar_id", "=", self.id),
            ("dayofweek", "=", day.weekday()),
            ("effective_attendance_period", "=", True)
        ]
        if self.two_weeks_calendar:
            # Employee has Even/Odd weekly calendar
            week_type = 1 if int(math.floor((day.toordinal() - 1) / 7) % 2) else 0
            domain.append(("week_type", "=", week_type))
        result = self.env["resource.calendar.attendance"].search(domain)
        return result

    def is_working_day(self, day):
        day_attendances = self._retrieve_day_matching_attendances(day)
        if len(day_attendances) == 0:
            # This day of the week is not supposed to be a working day
            return False
        else:
            # This day of the week is supposed to be a working day
            return True

    def is_full_working_day(self, day):
        day_attendances = self._retrieve_day_matching_attendances(day)
        morning_worked = len(day_attendances.filtered(lambda x: x.day_period == "morning")) > 0
        afternoon_worked = len(day_attendances.filtered(lambda x: x.day_period == "afternoon")) > 0
        return morning_worked and afternoon_worked

    def _compute_datetime_in_utc_tz(self, date):
        user_tz = pytz.timezone(self.env.context.get('tz', 'utc') or 'utc')
        return user_tz.localize(date).astimezone(pytz.utc)        

    def _is_worked_attendance(self, resource, day, attendance):
        attendance_start = fields.Datetime.to_datetime(day.date()) + timedelta(hours=attendance.hour_from)
        attendance_end = fields.Datetime.to_datetime(day.date()) + timedelta(hours=attendance.hour_to)
        utc_start = self._compute_datetime_in_utc_tz(attendance_start)
        utc_end = self._compute_datetime_in_utc_tz(attendance_end)
        resource_leaves = self.env["resource.calendar.leaves"].sudo().search(
            [
                ("company_id", "=", resource.company_id.id),
                ("date_from", "<=", utc_start),
                ("date_to", ">=", utc_end),
                "|",
                ("resource_id", "=", resource.id),
                ("resource_id", "=", None),
            ]
        )
        if resource_leaves:
            return False
        else:
            # a part or the whole attendance is worked
            return True

    def is_worked_day(self, resource, day):
        day_attendances = self._retrieve_day_matching_attendances(day)
        # If at least one attendance is worked, return True
        for attendance in day_attendances:
            if self._is_worked_attendance(resource, day, attendance):
                return True
        return False

    def all_attendances_worked(self, resource, day):
        day_attendances = self._retrieve_day_matching_attendances(day)
        # If at least one attendance is not worked, return False
        for attendance in day_attendances:
            if not self._is_worked_attendance(resource, day, attendance):
                return False
        return True