# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': "hr_timesheet_import_from_calendar",
    'version': '16.0.1.0.0',
    'depends': ['hr_timesheet'],
    'author': "Élabore",
    'category': 'Human Resources/Employees',
    'summary' : "Import HR timesheet from calendar events",
    'description': """
    In HR timesheet list view, you can import directly from your calendar.
    """,
    'data': [
        'views/hr_timesheet_views.xml', 
        'wizard/hr_timesheet_import_from_calendar_wizard_views.xml', 
        'security/ir.model.access.csv'
    ],
    'demo': [
    ],
    'application': False,
    'license': 'LGPL-3',
}