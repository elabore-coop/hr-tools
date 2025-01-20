from odoo import fields, models, api

class TimesheetsAnalysisReport(models.Model):
    _inherit = "timesheets.analysis.report"

    timesheet_id = fields.Many2one("account.analytic.line", string="Timesheet", readonly=True, help="Feuille de temps")

    @api.model
    def _select(self):
        return super()._select() + """,
            A.id AS timesheet_id
        """