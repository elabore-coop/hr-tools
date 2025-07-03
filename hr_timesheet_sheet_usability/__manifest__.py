{
    "name": "hr_timesheet_sheet_usability",
    "version": "16.0.1.0.0",
    "description": "Various changes to improve the usability of hr_timesheet_sheet application",
    "summary": "",
    "author": "Elabore",
    "website": "https://github.com/Alusage/odoo-hr-addons",
    "license": "LGPL-3",
    "category": "Human Resources",
    "depends": [
        "base","hr_timesheet","hr_timesheet_sheet",
    ],
    "data": [
        "views/hr_timesheet_sheet_menu.xml",
        "views/account_analytic_line_views.xml",
    ],
    "installable": True,
    "application": False,
}
