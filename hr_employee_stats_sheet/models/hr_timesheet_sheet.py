from datetime import timedelta

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.addons.resource.models.resource import HOURS_PER_DAY


class HrTimesheetSheet(models.Model):
    _inherit = "hr_timesheet.sheet"

    employee_stats_ids = fields.One2many(
        "hr.employee.stats", "sheet_id", "Employee Stats"
    )
    total_recovery_hours = fields.Float(
        compute="_compute_total_recovery_hours", string="Total Recovery Hours"
    )
    timesheet_sheet_gap_hours = fields.Float(
        "Timesheet sheet gap hours", compute="_compute_hours"
    )
    timesheet_sheet_recovery_hours = fields.Float(
        "Timesheet sheet recovery hours", compute="_compute_hours"
    )

    recovery_allocation_ids = fields.One2many(
        'hr.leave.allocation',
        'timesheet_sheet_id',
        string='Recovery Allocations',
        )
        
    @api.depends("employee_stats_ids.gap_hours", "employee_id")
    def _compute_hours(self):
        for sheet in self:
            sheet.timesheet_sheet_gap_hours = sheet._get_timesheet_sheet_gap_hours()
            sheet.timesheet_sheet_recovery_hours = (
                sheet._get_timesheet_sheet_recovery_hours()
            )

    def _get_timesheet_sheet_gap_hours(self):
        for sheet in self:
            timesheet_sheet_gap_hours = sum(
                sheet.employee_stats_ids.filtered(
                    lambda stat: stat.date <= fields.Date.today()
                ).mapped("gap_hours")
            )
        return timesheet_sheet_gap_hours

    def _get_timesheet_sheet_recovery_hours(self):
        self.ensure_one()
        coef = self.env.company.coef
        # apply coef only if hours to recovery are positive and coef is existing
        if self.timesheet_sheet_gap_hours > 0 and coef > 0:
            timesheet_sheet_recovery_hours = self.timesheet_sheet_gap_hours + (
                self.timesheet_sheet_gap_hours * coef / 100
            )
        else:
            timesheet_sheet_recovery_hours = self.timesheet_sheet_gap_hours
        return timesheet_sheet_recovery_hours

    def search_and_create_employee_stats(self):
        for sheet in self:
            if sheet.employee_id:
                for day in range((sheet.date_end - sheet.date_start).days + 1):
                    date = sheet.date_start + timedelta(days=day)
                    stats = self.env["hr.employee.stats"].search(
                        [
                            ("employee_id", "=", sheet.employee_id.id),
                            ("date", "=", date),
                        ]
                    )
                    if stats and not stats.sheet_id:
                        stats.write({"sheet_id": sheet.id})
                    if not stats:
                        self.env["hr.employee.stats"].create(
                            {
                                "employee_id": sheet.employee_id.id,
                                "date": date,
                                "sheet_id": sheet.id,
                                "company_id": sheet.company_id.id,
                            }
                        )
        return True

    @api.model
    def create(self, vals):
        res = super().create(vals)
        res.search_and_create_employee_stats()
        return res

    def write(self, vals):
        res = super().write(vals)
        if "date_end" in vals or "date_start" in vals or "employee_id" in vals:
            self.search_and_create_employee_stats()
        return res

    def unlink(self):
        for sheet in self:
            sheet.employee_stats_ids.unlink()
        return super().unlink()

    def action_timesheet_draft(self):
        res = super().action_timesheet_draft()
        for sheet in self:
            # set the state of the recovery allocation to refuse if the timesheet sheet is set to draft
            if sheet.state == "draft":
                sheet.recovery_allocation_ids.write({"state": "refuse"})
        return res

    @api.depends("employee_stats_ids.gap_hours", "employee_id")
    def _compute_total_recovery_hours(self):
        recovery_type_id = self.env.company.recovery_type_id
        for sheet in self:
            recovery_ids = self.env["hr.leave"].search(
                [
                    ("holiday_status_id", "=", recovery_type_id.id),
                    ("employee_id", "=", sheet.employee_id.id),
                ]
            )
            recovery_allocation_ids = self.env["hr.leave.allocation"].search(
                [
                    ("holiday_status_id", "=", recovery_type_id.id),
                    ("employee_id", "=", sheet.employee_id.id),
                ]
            )
            total_allocation_ids = sum(
                recovery_allocation_ids.mapped("number_of_hours_display")
            )
            total_recovery_ids = sum(recovery_ids.mapped("number_of_hours_display"))
            sheet.total_recovery_hours = (
                total_allocation_ids
                + total_recovery_ids
                + sum(
                    sheet.employee_stats_ids.filtered(
                        lambda stat: stat.date <= fields.Date.today()
                    ).mapped("gap_hours")
                )
            )

    def _get_contract_in_progress_during_timesheet_sheet_time_period(self):
        """
        get the contract which was in progress during the timesheet sheet range time : 
        - the contrat start date must be before the timesheet sheet start date
        - the contrat end date can be not defined or must be after the timesheet sheet end date
        - the state can be closed today or still open
        """
        contract_in_progress_during_timesheet = self.env["hr.contract"].search(
            [
                ("employee_id", "=", self.employee_id.id),
                ("state", "in", ("open","close")),
                ("date_start", "<=", self.date_start),
                ("date_end", ">=", self.date_end or None),
            ],
            order="date_start desc",
            limit=1,
        )
        return contract_in_progress_during_timesheet

    def _check_new_contract_starting_during_timesheet(self):
        """
        check if there was a contract starting during the timesheet sheet range time
        :return: raise error if there is a contract starting during the timesheet sheet range time
        """
        contract_starting_during_timesheet_ids = self.env["hr.contract"].search(
            [
                ("employee_id", "=", self.employee_id.id),
                ("state", "in", ("open","close")),
                ("date_start", ">", self.date_start),
                ("date_start", "<=", self.date_end),
            ],
        )
        if contract_starting_during_timesheet_ids:
            raise UserError(
                _("There is a contract starting during the timesheet sheet time period for the employee %s"
                  "Please create a new timesheet sheet starting from the new contract start date")
                % self.employee_id.display_name
            )

    def _get_calendar_in_progress_during_timesheet_time_period(self):
        """
        get the ressource calendar which was used during the timesheet sheet time period 
        """
        # get work contrat in progress for the employe during the timesheet sheet time period
        contract_during_timesheet_sheet = self._get_contract_in_progress_during_timesheet_sheet_time_period()
        if contract_during_timesheet_sheet:
            # check if a new contract start during timesheet sheet time period. If yes, raise an error
            self._check_new_contract_starting_during_timesheet()
            # get the ressource calendar id according to the work contract
            return contract_during_timesheet_sheet.resource_calendar_id
        elif self.employee_id.resource_calendar_id:
            return self.employee_id.resource_calendar_id
        elif self.env.company.resource_calendar_id:
            return self.env.company.resource_calendar_id
        return None

    def _get_working_hours_per_week(self):
        """
        Get the weekly working hours for the employee, which is defined by:
        - the employee's work contract,
        - or their resource calendar,
        - or the company's resource calendar,
        - or the default value of 40 hours per week.
        :return: limit recovery hours
        """
        # get ressource calendar id used during the timesheet sheet time period
        ressource_calendar_id = self._get_calendar_in_progress_during_timesheet_time_period()
        if ressource_calendar_id:
            resource_calendar_attendance_ids = self.env[
                "resource.calendar.attendance"
            ].search([("calendar_id", "=", ressource_calendar_id.id)])
            # calculate working hours per week according to the employee's resource calendar
            weekly_working_hours = 0
            for day in resource_calendar_attendance_ids:
                weekly_working_hours += day.hour_to - day.hour_from
            return weekly_working_hours
        return HOURS_PER_DAY * 5

    def _get_working_hours_per_day(self):
        """
        Get the hours per day for the employee according to:
        - the employee's work contract,
        - or their resource calendar,
        - or the company's resource calendar,
        - or the default value of 8 hours per day.
        :return: hours per day
        """
        # get ressource calendar id used during the timesheet sheet time period
        ressource_calendar_id = self._get_calendar_in_progress_during_timesheet_time_period()
        if ressource_calendar_id:
            return ressource_calendar_id.hours_per_day
        return HOURS_PER_DAY

    def _get_max_allowed_recovery_hours(self):
        """
        Get the maximum number of hours beyond which new recovery allowances cannot be created 
        """
        return self._get_working_hours_per_week()

    def action_generate_recovery_allocation(self):
        # check if the user has the right to review the timesheet sheet
        self.ensure_one()
        self._check_can_review()
        recovery_type_id = self.env.company.recovery_type_id
        employee_id = self.employee_id

        if not employee_id or not recovery_type_id:
            raise UserError(
                _("Employe not defined for the timesheet sheet or recovery type not defined in settings") 
            )

        # check if allocation already exists for this timesheet sheet, if yes, refuse it
        allocations = (
            self.env["hr.leave.allocation"]
            .sudo()
            .search(
                [
                    ("timesheet_sheet_id.id", "=", self.id),
                    ("state", "!=", "refuse"),
                ]
            )
        )
        if allocations:
            allocations.write({"state": "refuse"})

        # get recovery hours from total gap hours of the timesheet sheet
        recovery_hours = self._get_timesheet_sheet_recovery_hours()

        # get recovery hours cap
        max_allowed_recovery_hours = self._get_max_allowed_recovery_hours()
        if max_allowed_recovery_hours:
            # find recovery remaining leaves for the employee
            recovery_type_id = self.env.company.recovery_type_id
            # get virtual remaining leaves for the employee and the recovery leaves type
            data_days = recovery_type_id.get_employees_days([employee_id.id])[employee_id.id]
            total_recovery_type_leaves = data_days.get(recovery_type_id.id,{})
            total_virtual_remaining_recovery_type_leaves = total_recovery_type_leaves.get('virtual_remaining_leaves', 0)
            # TODO vérifier si ça marche avec un recovery type dont l'unité de mesure est le jour
            # add the recovery hours to the total remaining leaves recovery type, and check if the limit of recovery hours is exceeded
            exceeded_hours = total_virtual_remaining_recovery_type_leaves + recovery_hours - max_allowed_recovery_hours
            # if limit recovery hours is exceeded, don't create a new allocation
            if exceeded_hours > 0:
                raise UserError(
                    _(
                        "The number of recovery hours exceeds the authorized limit (%s h) by %s hours"
                    )
                    % (max_allowed_recovery_hours, exceeded_hours)
                )
        # convert recovery hours into days
        recovery_days = recovery_hours / self._get_working_hours_per_day()
        
        # create an allocation (positive or negative) according to the total gap hours for the timesheet sheet range time
        new_alloc = self.env["hr.leave.allocation"].create(
            {
                "private_name": "Allocation : %s - %s" % (recovery_type_id.name, employee_id.display_name),
                "holiday_status_id": recovery_type_id.id,
                "employee_id": employee_id.id,
                "number_of_days": recovery_days,
                "timesheet_sheet_id": self.id,
                "allocation_type": 'accrual',
            }
        )

        # set the allocation to validate or not
        if self.env.company.auto_validate_recovery_allocation:
            new_alloc.write({"state": "validate"})

        return {
            "type": "ir.actions.act_window",
            "res_model": "hr.leave.allocation",
            "res_id": new_alloc.id,
            "view_mode": "form",
            "target": "current",
            "views": [
                (
                    self.env.ref("hr_holidays.hr_leave_allocation_view_form").id,
                    "form",
                )
            ],
        }           
            
