# -*- coding: utf-8 -*-

from odoo import api, fields, models
from datetime import date, timedelta
import re

from odoo.exceptions import UserError

class HrTimesheetImportFromCalendarWizard(models.TransientModel):
    _name = 'hr.timesheet.import.from.calendar.wizard'

    imported = fields.Boolean()
    date_from = fields.Date('Du', default=lambda self: self._default_date_from(), required=True)
    date_to = fields.Date('Au', default=lambda self: self._default_date_to(), required=True)
    lines = fields.One2many('hr.timesheet.import.from.calendar.wizard.line', 'wizard_id', string="Lines")
    warning = fields.Boolean()

    def _default_date_from(self):
        return date.today()-timedelta(days=date.today().weekday())-timedelta(days=7)
    
    def _default_date_to(self):
        return date.today()-timedelta(days=date.today().weekday())-timedelta(days=1)
    
    def action_import(self):
        self.lines.unlink()

        calendar_events = self.env['calendar.event'].search([
            ('user_id','=',self.env.user.id), 
            ('start','>=',self.date_from), 
            ('start','<=',self.date_to), 
        ]).sorted('start')

        for event in calendar_events:
            project_id = None
            if '[' in event.name and ']' in event.name:
                analytic_account_codes = re.findall(r'\[(.*?)\]', event.name)
                if analytic_account_codes:
                    analytic_account_code = analytic_account_codes[0]
                    analytic_account = self.env['account.analytic.account'].search([('code','=',analytic_account_code)], limit=1)
                    if analytic_account:
                        project = self.env['project.project'].search([('analytic_account_id','=',analytic_account.id)], limit=1)
                        project_id = project.id

            # Check if analytic account line already created by this event
            existing_lines = self.env['account.analytic.line'].search([('calendar_event_origin_id','=',event.id)])
            warning = False
            if existing_lines:
                warning = True
                self.warning = True
            
            self.env['hr.timesheet.import.from.calendar.wizard.line'].create({
                'wizard_id':self.id, 
                'date': event.start, 
                'name': event.name, 
                'project_id':project_id, 
                'unit_amount':event.duration,
                'calendar_event_origin_id': event.id, 
                'warning':warning
            })

        self.imported = True


        return {
            'type': 'ir.actions.act_window',
            'name': 'Importer depuis le calendrier',
            'res_model': 'hr.timesheet.import.from.calendar.wizard',
            'res_id': self.id,  # Garde le même enregistrement ouvert
            'view_mode': 'form',
            'target': 'new',  # Wizard modal
        }
    
    @api.onchange('lines')
    def check_warning(self):
        for line in self.lines:
            if line.warning:
                self.warning = True
                return
        self.warning = False

    def action_confirm(self):
        if not all([l.project_id for l in self.lines]):
            raise UserError("Vous devez indiquer un projet sur chaque ligne. Si une ligne n'est pas concernée, vous devez la supprimer.")
        for line in self.lines:
            self.env['account.analytic.line'].create({
                'date':line.date, 
                'project_id':line.project_id.id, 
                'name':line.name, 
                'unit_amount':line.unit_amount, 
                'calendar_event_origin_id':line.calendar_event_origin_id.id
            })
        action = self.env["ir.actions.act_window"]._for_xml_id("hr_timesheet.act_hr_timesheet_line")
        action['target'] = 'main' # clear breadcrump
        return action
    

class HrTimesheetImportFromCalendarWizardLine(models.TransientModel):
    _name = 'hr.timesheet.import.from.calendar.wizard.line'

    wizard_id = fields.Many2one('hr.timesheet.import.from.calendar.wizard')
    date = fields.Date()
    project_id = fields.Many2one('project.project')
    name = fields.Char('Description')
    unit_amount = fields.Float('Heures passées')
    calendar_event_origin_id = fields.Many2one('calendar.event')
    warning = fields.Boolean()