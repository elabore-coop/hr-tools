# -*- coding: utf-8 -*-
import random
from datetime import datetime, date, timedelta, time
from dateutil.rrule import rrule, DAILY
from pytz import timezone, UTC, utc

from odoo import fields, models, api, _


class LuncheonVouchersAllocation(models.Model):
    _name = "hr.lv.allocation"
    _description = "Luncheon Vouchers Allocation"
    _order = "create_date desc"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _mail_post_access = "read"

    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("confirmed", "Confirmed"),
            ("distributed", "Distributed"),
        ],
        string="Status",
        readonly=True,
        tracking=True,
        copy=False,
        default="draft",
        help="The status is set to 'Draft', when an allocation request is created."
        + "\nThe status is 'Confirmed', when an allocation request is confirmed by HR manager."
        + "\nThe status is 'Distributed', when the luncheon vouchers have been distributed.",
    )

    date_from = fields.Datetime(
        string=_("Start Date"),
        index=True,
        copy=False,
        states={"draft": [("readonly", False)]},
        tracking=True,
    )
    date_to = fields.Datetime(
        string=_("End Date"),
        store=True,
        readonly=False,
        copy=False,
        tracking=True,
        states={
            "confirmed": [("readonly", True)],
            "distributed": [("readonly", True)],
        },
    )
    employee_id = fields.Many2one(
        "hr.employee",
        store=True,
        string=_("Employee"),
        index=True,
        readonly=False,
        ondelete="restrict",
        tracking=True,
        states={
            "confirmed": [("readonly", True)],
            "distributed": [("readonly", True)],
        },
    )

    number_acquired_lv = fields.Integer(
        string=_("Acquired Vouchers"),
        store=True,
        readonly=False,
        tracking=True,
        states={
            "confirmed": [("readonly", True)],
            "distributed": [("readonly", True)],
        },
    )

    number_dued_lv = fields.Integer(
        string=_("Dued Vouchers"),
        store=True,
        readonly=False,
        tracking=True,
        states={
            "confirmed": [("readonly", True)],
            "distributed": [("readonly", True)],
        },
    )

    number_distributed_lv = fields.Integer(
        string=_("Distributed Vouchers"),
        store=True,
        readonly=False,
        tracking=True,
        states={
            "confirmed": [("readonly", True)],
            "distributed": [("readonly", True)],
        },
    )

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

    def _calculate_number_acquired_lv(self):
        for record in self:
            # Retrieve all leaves on the whole period
            # domain = [
            #     ("time_type", "=", "leave"),
            #     ("calendar_id", "=", self.employee_id.sudo().resource_id.calendar_id),
            #     ("resource_id", "=", self.employee_id.sudo().resource_id.id),
            #     (
            #         "date_from",
            #         "<=",
            #         fields.Datetime.to_string(self.date_from.astimezone(utc)),
            #     ),
            #     (
            #         "date_to",
            #         ">=",
            #         fields.Datetime.to_string(self.date_to.astimezone(utc)),
            #     ),
            # ]
            # leaves = self.env["hr.leave"].search(domain)

            # Loop on all days between date_from and date_to
            for day in rrule(DAILY, self.date_from, until=self.date_to):
                # Keep only the full days of work
                # for leave in leaves:
                #     # if day is in a leave period, no luncheon voucher acquired:
                #     if day >= leave.date_from and day <= leave.date_to:
                #         break
                #     # leave period concerns one day:
                #     if leave.date_from >= day and leave.date_to <= day:
                #         # if leave period greater than half day, no luncheon voucher acquired:
                #         if leave.number_of_hours_display >= 3.5:
                #             break
                #         domain = [()]
                #         if self.env["calendar.event"].search(domain):
                #             continue
                # Remove days with events not eligible to luncheon vouchers

                # All condition match, addition of a acquired luncheon voucher
                record.number_acquired_lv += random.randint(0, 1)

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
            # record.employee_id.total_acquired_lv += record.number_acquired_lv
            # record.employee_id. dued_lv
            record.state = "confirmed"
            record.employee_id._compute_total_acquired_lv()

    def back_to_draft(self):
        for record in self:
            record.state = "draft"
            record.employee_id._compute_total_acquired_lv()

    def distribute_allocation(self):
        for record in self:
            record.state = "distributed"
            record.employee_id._compute_distributed_lv()
