from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    lunch_voucher_min_worked_hours = fields.Float(
        related="company_id.lunch_voucher_min_worked_hours",
        required=True,
        string="Minimal number of hours worked in a day to get a lunch voucher",
        domain="[('company_id', '=', company_id)]",
        readonly=False,
        help="5h by default, meaning that if an employee works 5h or more in a day, he will get a lunch voucher",
    )
