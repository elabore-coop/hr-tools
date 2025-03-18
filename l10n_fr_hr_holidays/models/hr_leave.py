# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from dateutil.relativedelta import relativedelta
from odoo import fields, models, _
from odoo.exceptions import UserError

class HrLeave(models.Model):
    _inherit = 'hr.leave'

    resource_calendar_id = fields.Many2one('resource.calendar', compute='_compute_resource_calendar_id', store=True, readonly=False, copy=False)
    company_id = fields.Many2one('res.company', compute='_compute_company_id', store=True)
    l10n_fr_date_to_changed = fields.Boolean()

    def _compute_company_id(self):
        for holiday in self:
            holiday.company_id = holiday.employee_company_id \
                or holiday.mode_company_id \
                or holiday.department_id.company_id \
                or self.env.company

    def _compute_resource_calendar_id(self):
        for leave in self:
            calendar = False
            if leave.holiday_type == 'employee':
                calendar = leave.employee_id.resource_calendar_id
                # YTI: Crappy hack: Move this to a new dedicated hr_holidays_contract module
                # We use the request dates to find the contracts, because date_from
                # and date_to are not set yet at this point. Since these dates are
                # used to get the contracts for which these leaves apply and
                # contract start- and end-dates are just dates (and not datetimes)
                # these dates are comparable.
                if 'hr.contract' in self.env and leave.employee_id:
                    contracts = self.env['hr.contract'].search([
                        '|', ('state', 'in', ['open', 'close']),
                             '&', ('state', '=', 'draft'),
                                  ('kanban_state', '=', 'done'),
                        ('employee_id', '=', leave.employee_id.id),
                        ('date_start', '<=', leave.request_date_to),
                        '|', ('date_end', '=', False),
                             ('date_end', '>=', leave.request_date_from),
                    ])
                    if contracts:
                        # If there are more than one contract they should all have the
                        # same calendar, otherwise a constraint is violated.
                        calendar = contracts[:1].resource_calendar_id
            elif leave.holiday_type == 'department':
                calendar = leave.department_id.company_id.resource_calendar_id
            elif leave.holiday_type == 'company':
                calendar = leave.mode_company_id.resource_calendar_id
            leave.resource_calendar_id = calendar or self.env.company.resource_calendar_id

    def _l10n_fr_leave_applies(self):
        # The french l10n is meant to be computed only in very specific cases:
        # - there is only one employee affected by the leave
        # - the company is french
        # - the leave_type is the reference leave_type of that company
        self.ensure_one()
        return self.employee_id and \
               self.company_id.country_id.code == 'FR' and \
               self.resource_calendar_id != self.company_id.resource_calendar_id and \
               self.holiday_status_id == self.company_id._get_fr_reference_leave_type()

    def _get_fr_date_from_to(self, date_from, date_to):
        self.ensure_one()
        # What we need to compute is how much we will need to push date_to in order to account for the lost days
        # This gets even more complicated in two_weeks_calendars

        # The following computation doesn't work for resource calendars in
        # which the employee works zero hours.
        if not (self.resource_calendar_id.attendance_ids):
            raise UserError(_("An employee cannot take a paid time off in a period they work no hours."))

        if self.request_unit_half and self.request_date_from_period == 'am':
            # In normal workflows request_unit_half implies that date_from and date_to are the same
            # request_unit_half allows us to choose between `am` and `pm`
            # In a case where we work from mon-wed and request a half day in the morning
            # we do not want to push date_to since the next work attendance is actually in the afternoon
            date_from_weektype = str(self.env['resource.calendar.attendance'].get_week_type(date_from))
            date_from_dayofweek = str(date_from.weekday())
            # Get morning and afternoon attendances for that day
            attendances_am = self.resource_calendar_id.attendance_ids.filtered(lambda a:
                a.dayofweek == date_from_dayofweek
                and a.day_period == 'morning'
                and (not self.resource_calendar_id.two_weeks_calendar or a.week_type == date_from_weektype))
            attendances_pm = self.resource_calendar_id.attendance_ids.filtered(lambda a:
                a.dayofweek == date_from_dayofweek
                and a.day_period == 'afternoon'
                and (not self.resource_calendar_id.two_weeks_calendar or a.week_type == date_from_weektype))
            if attendances_am and not attendances_pm:
                # If the employee does not work in the afternoon, postpone date_to to the next working day
                next_date = date_from + relativedelta(days=1)
                while not self.resource_calendar_id._works_on_date(next_date):
                    next_date += relativedelta(days=1)
                return (date_from, next_date)
            elif attendances_am and attendances_pm:
                # The employee also works in the afternoon, no postponement
                return (date_from, date_to)

        # Special handling for two-weeks calendars
        if self.resource_calendar_id.two_weeks_calendar:
            # Count the number of days actually worked by the employee between date_from and date_to
            current_date = date_from
            days_count = 0
            while current_date <= date_to:
                if self.resource_calendar_id._works_on_date(current_date):
                    days_count += 1
                current_date += relativedelta(days=1)
            # Adjust date_to so it matches the expected number of days
            # If the expected number of days is less than the period, reduce date_to
            if days_count > 0:
                # Find the date_to that gives the right number of worked days
                current_date = date_from
                counted = 0
                while counted < days_count:
                    if self.resource_calendar_id._works_on_date(current_date):
                        counted += 1
                    if counted == days_count:
                        break
                    current_date += relativedelta(days=1)
                return (date_from, current_date)
        # Check calendars for working days until we find the right target, start at date_to + 1 day
        # Postpone date_target until the next working day
        date_start = date_from
        date_target = date_to
        # It is necessary to move the start date up to the first work day of
        # the employee calendar as otherwise days worked on by the company
        # calendar before the actual start of the leave would be taken into
        # account.
        while not self.resource_calendar_id._works_on_date(date_start):
            date_start += relativedelta(days=1)
        while not self.resource_calendar_id._works_on_date(date_target + relativedelta(days=1)):
            date_target += relativedelta(days=1)

        # Undo the last day increment
        return (date_start, date_target)

    def _compute_date_from_to(self):
        super()._compute_date_from_to()
        for leave in self:
            if leave._l10n_fr_leave_applies():
                new_date_from, new_date_to = leave._get_fr_date_from_to(leave.date_from, leave.date_to)
                if new_date_from != leave.date_from:
                    leave.date_from = new_date_from
                if new_date_to != leave.date_to:
                    leave.date_to = new_date_to
                    leave.l10n_fr_date_to_changed = True
                else:
                    leave.l10n_fr_date_to_changed = False

    #@overwrite
    def _get_calendar(self):
        """
        In France, paid time off for part-time employees is counted on the company's working days (not the employee's own schedule).
        The company's calendar must be used for the legal leave day count.
        """
        self.ensure_one()
        if self._l10n_fr_leave_applies():
            return self.company_id.resource_calendar_id or self.env.company.resource_calendar_id
        return super()._get_calendar()

    #@overwrite
    def _get_number_of_days_batch(self, date_from, date_to, employee_ids):
        """
        Returns a dict with the number of legal leave days for each employee, 
        based on the company's calendar. In France, part-time employees accrue and take leave on company working days,
        not only on their own working days. Handles half-day requests and rounds according to French rules.
        """
        employee = self.env['hr.employee'].browse(employee_ids)
        # Force the company in the domain, as we are likely in a compute_sudo context
        domain = [
            ('time_type', '=', 'leave'),
            ('company_id', 'in', self.env.company.ids + self.env.context.get('allowed_company_ids', []))
        ]
        calendar = self._get_calendar()
        result = employee._get_work_days_data_batch(date_from, date_to, calendar=calendar, domain=domain)
        for employee_id in result:
            # For non-French context: a half-day leave always counts as 0.5 day
            if self.request_unit_half and result[employee_id]['hours'] > 0 and not self._l10n_fr_leave_applies():
                result[employee_id]['days'] = 0.5
            # For French context: round the number of days to the nearest half-day (legal rule)
            elif self.request_unit_half and result[employee_id]['hours'] > 0 and self._l10n_fr_leave_applies():
                result[employee_id]['days'] = self._round_to_nearest_half(result[employee_id]['days'])
        return result

    def _round_to_nearest_half(self, x):
        """Round a float to the nearest 0.5."""
        return round(x * 2) / 2
