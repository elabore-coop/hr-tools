from odoo import models, fields, api

class HrExpenseSheet(models.Model):
    _inherit = 'hr.expense.sheet'    

    @api.model
    def _default_journal_id(self):
        """ The journal is determining the company of the accounting entries generated from expense. We need to force journal company and expense sheet company to be the same. """
        default_company_id = self.default_get(['company_id'])['company_id']
        journal = self.env['account.journal'].search([('company_id', '=', default_company_id), ('is_expense_journal','=',True)], limit=1)
        return journal.id
    
    journal_id = fields.Many2one(default=_default_journal_id)