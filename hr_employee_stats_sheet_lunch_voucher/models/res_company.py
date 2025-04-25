from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    lunch_voucher_min_worked_hours = fields.Float(default=5)
