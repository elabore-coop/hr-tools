# -*- coding: utf-8 -*-

from odoo import fields, models, api

class HrExpense(models.Model):
    _inherit = "hr.expense"

    project_id = fields.Many2one('project.project', string="Projet", required=True)

    @api.onchange('project_id')
    def set_analytic_account(self):
        self.analytic_account_id = self.project_id.analytic_account_id
        