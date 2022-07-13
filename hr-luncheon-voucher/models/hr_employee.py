# -*- coding: utf-8 -*-

from odoo import fields, models, api, _


class HrEmployeeBase(models.AbstractModel):
    _inherit = "hr.employee.base"

    lv_allocations_ids = fields.One2many("hr.lv.allocation", "employee_id")

    total_acquired_lv = fields.Integer(
        string=_("Total allocated luncheon vouchers"), store=True, copy=False
    )
    distributed_lv = fields.Integer(
        string=_("Distributed luncheon vouchers"), store=True, copy=False
    )
    dued_lv = fields.Integer(
        string=_("Remaining luncheon vouchers"), store=True, copy=False
    )

    default_monthly_lv = fields.Integer(
        string=_("Default monthly distribution"), store=True, copy=True
    )

    @api.onchange("lv_allocations_ids.state")
    def refresh_lv_values(self):
        for record in self:
            record._compute_total_acquired_lv()
            record._compute_distributed_lv()
            record._compute_dued_lv()

    def _compute_total_acquired_lv(self):
        for record in self:
            allocations = self.env["hr.lv.allocation"].search(
                [("employee_id", "=", record.id), ("state", "=", "confirmed")]
            )
            record.total_acquired_lv = sum(allocations.mapped("number_acquired_lv"))

    def _compute_distributed_lv(self):
        for record in self:
            allocations = self.env["hr.lv.allocation"].search(
                [("employee_id", "=", record.id), ("state", "=", "distributed")]
            )
            record.distributed_lv = sum(allocations.mapped("number_distributed_lv"))

    @api.onchange("total_acquired_lv", "distributed_lv")
    def _compute_dued_lv(self):
        for record in self:
            record.dued_lv = record.total_acquired_lv - record.distributed_lv

    def generate_mass_lv_allocation(self, values):
        for record in self:
            record.generate_lv_allocation(values)

    def generate_lv_allocation(self, values):
        self.ensure_one()
        values["employee_id"] = self.id
        self.env["hr.lv.allocation"].create(values)

    def action_lv_allocations(self):
        return {
            "type": "ir.actions.act_window",
            "name": _("Luncheon vouchers allocations"),
            "res_model": "hr.lv.allocation",
            "res_id": self.id,
            "view_mode": "form",
            "view_type": "form",
            "views": [
                (
                    self.env.ref("hr-luncheon-voucher.hr_lv_allocation_tree").id,
                    "tree",
                )
            ],
            "context": {"employee_id": self.id},
        }

    def action_lv_allocations_requests_wizard(self):
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "hr-luncheon-voucher.lv_allocations_requests_wizard_action"
        )
        ctx = dict(self.env.context)
        ctx["active_ids"] = self.ids
        action["context"] = ctx
        return action
