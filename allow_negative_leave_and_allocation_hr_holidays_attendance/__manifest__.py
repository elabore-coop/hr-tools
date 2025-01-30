# Copyright 2025 Elabore ()
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "allow_negative_leave_and_allocation_hr_holidays_attendance",
    "version": "16.0.1.0.0",
    "author": "Elabore",
    "website": "https://elabore.coop",
    "maintainer": "Elabore",
    "license": "AGPL-3",
    "category": "HR",
    "summary": "manage heritance of Duration in TimeOffCard",
    # any module necessary for this one to work correctly
    "depends": [
        "base","allow_negative_leave_and_allocation","hr_holidays_attendance",
    ],
    "qweb": [],
    "external_dependencies": {
        "python": [],
    },
    # always loaded
    "data": [],
    "assets": {
        'web.assets_backend': [
            'allow_negative_leave_and_allocation_hr_holidays_attendance/static/src/xml/time_off_card.xml',
        ],
    },
    # only loaded in demonstration mode
    "demo": [],
    "js": [],
    "css": [],
    "installable": True,
    # Install this module automatically if all dependency have been previously
    # and independently installed.  Used for synergetic or glue modules.
    "auto_install": True,
    "application": False,
}