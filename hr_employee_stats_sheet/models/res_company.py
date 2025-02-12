from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    recovery_type_id = fields.Many2one(
        "hr.leave.type", string="Leave recovery type"
    )
    coef = fields.Float("Coef", default=25)

    auto_validate_recovery_allocation = fields.Boolean("Auto validate recovery allocation", default=True)