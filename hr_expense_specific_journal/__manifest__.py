# Copyright 2023 Stéphan Sainléger (Elabore)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "hr_expense_specific_journal",
    "version": "14.0.1.0.0",
    "author": "Elabore",
    "website": "https://elabore.coop",
    "maintainer": "Clément Thomas",
    "license": "AGPL-3",
    "category": "Tools",
    "summary": "Allow user to only select expense journal in expenses",
    # any module necessary for this one to work correctly
    "depends": [
        "hr_expense","account"
    ],
    "qweb": [
    ],
    "external_dependencies": {
        "python": [],
    },
    # always loaded
    "data": [
        'views/account_journal_views.xml',
        'views/hr_expense_sheet_views.xml'
    ],
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