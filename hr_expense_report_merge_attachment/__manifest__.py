# Copyright 2023 Stéphan Sainléger (Elabore)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "hr_expense_report_merge_attachment",
    "version": "14.0.0.0.0",
    "author": "Elabore",
    "website": "https://elabore.coop",
    "maintainer": "Clément Thomas",
    "license": "AGPL-3",
    "category": "Tools",
    "summary": "Merge attachments in expense report",
    # any module necessary for this one to work correctly
    "depends": [
        "hr_expense",
    ],
    "qweb": [
    ],
    "external_dependencies": {
        "python": [],
    },
    # always loaded
    "data": [
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