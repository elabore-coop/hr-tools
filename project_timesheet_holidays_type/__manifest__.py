# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': "project timesheet holidays type",
    'version': '16.0.1.0.0',
    'depends': ['project_timesheet_holidays'],
    'author': "Élabore",
    'category': 'Human Resources/Employees',
    'summary' : "add holidays type in project timesheet holidays type description",
    'description': """
    In project timesheet holidays, all holidays types are name 'Times off (d/d)' in description.
    This module changes 'Times off' by the holiday type for better description. 
    """,
    'data': [
    ],
    'demo': [
    ],
    'application': False,
    'license': 'LGPL-3',
}