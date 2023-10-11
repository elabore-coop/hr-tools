from odoo import models, fields

class AccountJournal(models.Model):
    _inherit = 'account.journal'

    is_expense_journal = fields.Boolean('Is expense journal')