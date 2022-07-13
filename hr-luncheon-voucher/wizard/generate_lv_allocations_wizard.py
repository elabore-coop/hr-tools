from odoo import _, api, fields, models


class GenerateLVAllocationRequests(models.TransientModel):
    _name = "generate.lv.allocation.requests"
    _description = "Generate Luncheon Vouchers Allocations Requests"

    date_from = fields.Datetime(
        string=_("Start Date"),
    )
    date_to = fields.Datetime(
        string=_("End Date"),
    )

    def generate_lv_allocations(self):
        values = {}
        values["date_from"] = self.date_from
        values["date_to"] = self.date_to
        employees = self.env["hr.employee"].search(
            [
                ("id", "in", self.env.context.get("active_ids")),
            ]
        )
        employees.generate_mass_lv_allocation(values)
        # Open lv allocation tree view
        return {
            "type": "ir.actions.act_window",
            "name": _("Luncheon vouchers allocations"),
            "res_model": "hr.lv.allocation",
            "view_mode": "tree",
            "views": [
                (
                    self.env.ref("hr-luncheon-voucher.hr_lv_allocation_tree").id,
                    "tree",
                )
            ],
        }
