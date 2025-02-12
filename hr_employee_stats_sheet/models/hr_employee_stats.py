import logging

from odoo import api, fields, models, _
from datetime import timedelta

_logger = logging.getLogger(__name__)


class HrEmployeeStats(models.Model):
    _name = "hr.employee.stats"
    _description = "Employee Stats"
    _order = "date desc"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char("Name", compute="_compute_name", store=True)
    dayofweek = fields.Integer("Day of Week", compute="_compute_dayofweek")
    is_public_holiday = fields.Boolean("Public Holiday", compute="_compute_dayofweek")
    employee_id = fields.Many2one("hr.employee", "Employee", required=True)
    department_id = fields.Many2one("hr.department", "Department")
    timesheet_line_ids = fields.One2many(
        "account.analytic.line",
        "employee_id",
        "Timesheet lines",
        compute="_compute_timesheet_line_ids",
    )
    date = fields.Date("Date", required=True)
    company_id = fields.Many2one(
        "res.company",
        "Company",
        default=lambda self: self.env.company,
        required=True,
    )
    sheet_id = fields.Many2one("hr_timesheet.sheet", "Timesheet")
    total_hours = fields.Float("Total Hours", compute="_compute_hours")
    total_planned_hours = fields.Float("Total Planning Hours", compute="_compute_hours")
    total_leave_hours = fields.Float("Total Leave Hours", compute="_compute_hours")
    total_recovery_hours = fields.Float(
        "Total Recovery Hours", compute="_compute_hours"
    )
    gap_hours = fields.Float("Gap Hours", compute="_compute_hours")

    def _get_holiday_status_id(self):
        recovery_type_id = self.env.company.recovery_type_id
        if recovery_type_id:
            return recovery_type_id.id
        else:
            return False

    def _compute_timesheet_line_ids(self):
        for stat in self:
            stat.timesheet_line_ids = self.env["account.analytic.line"].search(
                [
                    ("employee_id", "=", stat.employee_id.id),
                    ("date", "=", stat.date),
                ]
            )

    def _get_intersects(
        self, datetime1_start, datetime1_end, datetime2_start, datetime2_end
    ):
        latest_start = max(datetime1_start, datetime2_start)
        earliest_end = min(datetime1_end, datetime2_end)
        delta = (earliest_end - latest_start).total_seconds() / 3600
        return max(0, delta)

    def get_total_hours_domain(self):
        return [
            ("employee_id", "=", self.employee_id.id),
            ("date", "=", self.date),
        ]

    @api.depends("timesheet_line_ids")
    def _get_total_hours(self):
        timesheet_line = self.env["account.analytic.line"]
        for stat in self:
            if stat.date and stat.employee_id:
                timesheet_line_ids = timesheet_line.search(
                    stat.get_total_hours_domain()
                )
                total_hours = sum(timesheet_line_ids.mapped("unit_amount"))
            else:
                total_hours = 0
        return total_hours

    def _get_total_planned_hours(self):
        for stat in self:
            if stat.employee_id and stat.date and not stat.is_public_holiday:
                dayofweek = int(stat.date.strftime("%u")) - 1
                calendar_id = stat.employee_id.resource_calendar_id
                week_number = stat.date.isocalendar()[1] % 2
                if calendar_id.two_weeks_calendar:
                    hours = calendar_id.attendance_ids.search(
                        [
                            ("dayofweek", "=", dayofweek),
                            ("calendar_id", "=", calendar_id.id),
                            ("week_type", "=", week_number),
                        ]
                    )
                else:
                    hours = calendar_id.attendance_ids.search(
                        [
                            ("dayofweek", "=", dayofweek),
                            ("calendar_id", "=", calendar_id.id),
                        ]
                    )
                total_planned_hours = sum(
                    hours.mapped(lambda r: r.hour_to - r.hour_from)
                )
            else:
                total_planned_hours = 0
        return total_planned_hours

    def _get_total_recovery_hours(self):
        recovery = self.env["hr.leave"]
        for stat in self:
            if stat.date and stat.employee_id and stat._get_holiday_status_id():
                recovery_ids = recovery.search(
                    [
                        ("employee_id", "=", stat.employee_id.id),
                        ("request_date_from", ">=", stat.date),
                        ("request_date_from", "<=", stat.date),
                        ("holiday_status_id", "=", stat._get_holiday_status_id()),
                    ]
                )
                total_recovery_hours = sum(
                    recovery_ids.mapped("number_of_hours_display")
                )
            else:
                total_recovery_hours = 0
            return total_recovery_hours

    def _get_total_leave_hours(self):
        leave = self.env["hr.leave"]
        for stat in self:
            if stat.date and stat.employee_id:
                leave_ids = leave.search(
                    [
                        ("employee_id", "=", stat.employee_id.id),
                        ("holiday_status_id", "!=", stat._get_holiday_status_id()),
                        ("request_date_from", ">=", stat.date),
                        ("request_date_to", "<=", stat.date),
                    ]
                )
                # retire des congés les jours où j'ai travaillé (car présence dans l'app présence) alors que j'étais noté en congé
                # TODO faire pareil avec les feuilles de temps?
                intersect_hours = sum(leave_ids.mapped("number_of_hours_display"))
                # for leave_id in leave_ids:
                #     for attendance_id in stat.attendance_ids:
                #         intersect_hours -= stat._get_intersects(
                #             leave_id.date_from,
                #             leave_id.date_to,
                #             attendance_id.check_in,
                #             attendance_id.check_out,
                #         )
                total_leave_hours = intersect_hours
            else:
                total_leave_hours = 0
            return total_leave_hours

    @api.depends("employee_id", "date")
    def _compute_name(self):
        for stat in self:
            stat.name = "%s - %s" % (stat.employee_id.name, stat.date)

    @api.depends("date","employee_id")
    def _compute_dayofweek(self):
        for stat in self:
            if not stat.date:
                stat.dayofweek = None
                stat.is_public_holiday = False
                continue
            stat.dayofweek = int(stat.date.strftime("%u")) - 1
            stat.is_public_holiday = bool(stat.sheet_id.employee_id._get_public_holidays(stat.date, stat.date - timedelta(days=1)))

    def _get_gap_hours(self, total_hours, total_recovery_hours, total_leave_hours, total_planned_hours):
        self.ensure_one()
        balance = (
            total_hours
            + total_recovery_hours
            + total_leave_hours
            - total_planned_hours
        )
        return balance

    @api.depends(
        "employee_id",
        "date",
        "total_hours",
        "total_planned_hours",
        "timesheet_line_ids",
    )
    def _compute_hours(self):
        for stat in self:
            total_hours = stat._get_total_hours()
            total_recovery_hours = stat._get_total_recovery_hours()
            total_planned_hours = stat._get_total_planned_hours()
            total_leave_hours = stat._get_total_leave_hours()
            # balance = (
            #     total_hours
            #     + total_recovery_hours
            #     + total_leave_hours
            #     - total_planned_hours
            # )
            stat.total_hours = total_hours
            stat.total_planned_hours = total_planned_hours
            #stat.gap_hours = balance
            stat.gap_hours = stat._get_gap_hours(total_hours, total_recovery_hours, total_leave_hours, total_planned_hours)
            stat.total_recovery_hours = total_recovery_hours
            stat.total_leave_hours = total_leave_hours
