# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': "hr_usability Elabore",
    'version': '16.0.1.0.0',
    'depends': ['base','hr'],
    'author': "Laetitia",
    'category': 'Human Resources/Employees',
    'summary' : "In times off type form view, add 'create_calendar_meeting' field",
    'description': """
 
    Go to Times off app > "Setings" > "Type time off"
    Select a type
    The 'create_calendar_meeting' is check by default
    Uncheck it if do not want to display times off in the calendar

    One the checkbox is unchecked for a time off type, the next approuved times off (of that type) won't be created as a meeting and won't appear in the calendar

    """,
    'data': [
        'views/hr_leave_type_views.xml',
    ],
    'demo': [
    ],
    'application': False,
    'license': 'LGPL-3',
}