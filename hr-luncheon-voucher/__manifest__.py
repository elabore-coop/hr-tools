# -*- coding: utf-8 -*-
{
    "name": "HR Luncheon Voucher",
    "category": "Human Resources",
    "version": "14.0.1.1.0",
    "summary": "Manage luncheon vouchers credit and distribution",
    "author": "Elabore",
    "website": "https://elabore.coop/",
    "installable": True,
    "application": True,
    "auto_install": False,
    "depends": [
        "base",
        "calendar",
        "hr",
        "hr_effective_attendance_period",
        "hr_holidays",
        "resource",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/event_type.xml",
        "views/hr_employee_views.xml",
        "views/hr_lv_allocation_views.xml",
        "views/res_config_settings_views.xml",
        "views/menus.xml",
        "wizard/generate_lv_allocations_wizard.xml",
        "data/event_type_data.xml",
    ],
    "qweb": [],
}