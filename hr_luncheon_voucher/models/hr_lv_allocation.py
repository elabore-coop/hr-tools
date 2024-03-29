from datetime import datetime, timedelta, time
from dateutil.rrule import rrule, DAILY
from pytz import UTC

from odoo import fields, models, api


class LuncheonVouchersAllocation(models.Model):
    _name = "hr.lv.allocation"
    _description = "Luncheon Vouchers Allocation"

    name = fields.Char('Name')
    distrib_campaign_name = fields.Char('Distribution campaign')
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("confirmed", "Confirmed"),
            ("distributed", "Distributed"),
        ],
        string="Status",
        readonly=True,
        copy=False,
        default="draft",
        help="The status is set to 'Draft', when an allocation request is created. The status is 'Confirmed', when an allocation request is confirmed by HR manager. The status is 'Distributed', when the luncheon vouchers have been distributed.",
    )
    date_from = fields.Datetime(
        string="Start Date",
        store=True,
        readonly=False,
        copy=False,
        states={
            "confirmed": [("readonly", True)],
            "distributed": [("readonly", True)],
        },
    )
    date_to = fields.Datetime(
        string="End Date",
        store=True,
        readonly=False,
        copy=False,
        states={
            "confirmed": [("readonly", True)],
            "distributed": [("readonly", True)],
        },
    )
    employee_id = fields.Many2one(
        "hr.employee",
        store=True,
        string="Employee",
        index=True,
        readonly=False,
        ondelete="restrict",
        states={
            "confirmed": [("readonly", True)],
            "distributed": [("readonly", True)],
        },
    )
    number_acquired_lv = fields.Integer(
        string="Acquired Vouchers",
        store=True,
        readonly=False,
        states={
            "confirmed": [("readonly", True)],
            "distributed": [("readonly", True)],
        },
    )
    number_dued_lv = fields.Integer(
        string="Dued Vouchers",
        store=True,
        readonly=False,
        states={
            "confirmed": [("readonly", True)],
            "distributed": [("readonly", True)],
        },
    )
    number_distributed_lv = fields.Integer(
        string="Distributed Vouchers",
        store=True,
        readonly=False,
        states={
            "confirmed": [("readonly", False)],
            "distributed": [("readonly", True)],
        },
    )

    lv_balance = fields.Integer('Vouchers balance', compute="_get_lv_balance", help="Vouchers available after distribution. Dued vouchers - Distributed vouchers")

    @api.depends("number_dued_lv", "number_distributed_lv")
    def _get_lv_balance(self):
        for allocation in self:
            allocation.lv_balance = allocation.number_dued_lv - allocation.number_distributed_lv

    @api.model_create_multi
    def create(self, values):
        res = super(LuncheonVouchersAllocation, self).create(values)
        res._calculate_number_acquired_lv()
        res._calculate_number_dued_lv()
        res._default_number_distributed_lv()
        return res

    @api.depends("employee_id")
    def _default_number_distributed_lv(self):
        for record in self:
            record.number_distributed_lv = record.employee_id.default_monthly_lv

    def _has_cancelling_voucher_event(self, day):
        category_no_voucher_ids = self.env["calendar.event.type"].search([("remove_luncheon_voucher", "=", True)])
        events = self.env["calendar.event"].search(
            [
                ("categ_ids", "in", category_no_voucher_ids.ids),
                ("partner_ids", "in", self.employee_id.user_id.partner_id.id)
            ]
        )
        day_start = fields.Datetime.to_datetime(day.date())
        day_end = fields.Datetime.to_datetime(day.date()) + timedelta(hours=24)
        cancelling_events = events.filtered(lambda x: not((x.start < day_start) and (x.stop <= day_start)) and not((x.start >= day_end) and (x.stop > day_end)) )
        if len(cancelling_events) > 0:
            return True
        else:
            return False

    def _calculate_number_acquired_lv(self):
        nb_eligible_days = 0
        dfrom = datetime.combine(fields.Date.from_string(self.date_from), time.min).replace(tzinfo=UTC)
        dto = datetime.combine(fields.Date.from_string(self.date_to), time.max).replace(tzinfo=UTC)
        period_days = rrule(DAILY, dfrom, until=dto)
        calendar_resource = self.employee_id.resource_calendar_id
        for day in period_days:
            # Check if this days is a working day
            if not calendar_resource.is_working_day(day):
                continue
            # The employee should work this day but...
            if self.env.company.hr_half_day_cancels_voucher and not calendar_resource.is_full_working_day(day):
                # The luncheon voucher is acquired only if the employee has worked the entire day 
                continue
            # Check leaves
            if not calendar_resource.is_worked_day(self.employee_id, day):
                continue
            # The employee has worked this day but...
            if self.env.company.hr_half_day_cancels_voucher and not calendar_resource.all_attendances_worked(self.employee_id.resource_id, day):
                # The luncheon voucher is acquired only if the employee has worked the entire day
                continue
            # Check there is no event cancelling the voucher
            if self._has_cancelling_voucher_event(day):
                continue
            # All checks passed, the days is eligible for a voucher
            nb_eligible_days += 1
        self.number_acquired_lv = nb_eligible_days

    def _calculate_number_dued_lv(self):
        for record in self:
            if record.state == "distributed":
                record.number_dued_lv = record.employee_id.dued_lv
            else:
                record.number_dued_lv = (
                    record.employee_id.dued_lv + record.number_acquired_lv
                )

    def confirm_allocation(self):
        for record in self:
            if record.state == "draft":
                record.state = "confirmed"
                record.employee_id._compute_total_acquired_lv()
                record.employee_id._compute_dued_lv()

    def back_to_draft(self):
        for record in self:
            if record.state in ["confirmed","distributed"]:
                record.state = "draft"
                record.employee_id._compute_total_acquired_lv()
                record.employee_id._compute_distributed_lv()
                record.employee_id._compute_dued_lv()

    def distribute_allocation(self):
        for record in self:
            if record.state == "confirmed":
                record.state = "distributed"
                record.employee_id._compute_distributed_lv()
                record.employee_id._compute_dued_lv()

    def adjust_distribution(self):
        for record in self:
            for record in self:
                if record.state == "draft":
                    record.number_distributed_lv = record.employee_id.dued_lv + record.number_acquired_lv

