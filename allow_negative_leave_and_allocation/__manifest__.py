# Copyright 2024 Elabore ()
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "allow_negative_leave_and_allocation",
    "version": "16.0.1.0.1",
    "author": "Elabore",
    "website": "https://elabore.coop",
    "maintainer": "Elabore",
    "license": "AGPL-3",
    "category": "hr",
    "summary": "allow negative leaves and allocations",
    # any module necessary for this one to work correctly
    "depends": [
        "base","hr_holidays",
    ],
    "qweb": [],
    "external_dependencies": {
        "python": [],
    },
    # always loaded
    "data": [
        "views/hr_leave_type_views.xml",
        "views/hr_leave_views.xml",
    ],
    "assets": {
        'web.assets_backend': [
            'allow_negative_leave_and_allocation/static/src/xml/time_off_card.xml',
        ],
    },
    # only loaded in demonstration mode
    "demo": [],
    "js": [],
    "css": [],
    "installable": True,
    # Install this module automatically if all dependency have been previously
    # and independently installed.  Used for synergetic or glue modules.
    "auto_install": False,
    "application": False,
}