from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    recovery_type_id = fields.Many2one(
        "hr.leave.type",
        related="company_id.recovery_type_id",
        string="Leave recovery type",
        readonly=False,
    )

    coef = fields.Float(
        related="company_id.coef",
        required=True,
        string="Coef (in %)",
        domain="[('company_id', '=', company_id)]",
        readonly=False,
        help="The coef is applied to recovery hours"
        "Example : an employe make 1h overtime, if coef is set to 25%, the recovery hours allocated will be 1,25h",
    )

    auto_validate_recovery_allocation = fields.Boolean(
        related="company_id.auto_validate_recovery_allocation",
        readonly=False,
        domain="[('company_id', '=', company_id)]",
    )
