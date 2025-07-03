{
    "name": "hr_employee_stats_sheet_lunch_voucher",
    "version": "16.0.1.0.0",
    "description": "Add global sheet for employee stats",
    "summary": "Add global sheet for employee stats",
    "author": "Elabore",
    "website": "https://elabore.coop",
    "license": "LGPL-3",
    "category": "Human Resources",
    "depends": [
        "hr_employee_stats_sheet",
    ],
    "data": [
        "views/hr_employee_stats.xml",
        "views/hr_timesheet_sheet.xml",
        "views/res_config_settings_views.xml",
    ],
    "installable": True,
    "application": False,
}
