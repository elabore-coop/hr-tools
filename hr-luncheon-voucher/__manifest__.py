# -*- coding: utf-8 -*-
{
    "name": "HR Luncheon Voucher",
    "category": "Human Resources",
    "version": "14.0.1.0",
    "summary": "Manage luncheon vouchers credit and distribution",
    "author": "Elabore",
    "website": "https://elabore.coop/",
    "installable": True,
    "application": True,
    "auto_install": False,
    "description": """
===================
HR Luncheon Voucher
===================
This module allows the management of Luncheon Vouchers attribution and distribution.
Employees can  indicate which days are not concerned by luncheon vouchers.
HR managers can ajust the number of luncheon vouchers to distribute, and follow each employee credit.

Installation
============
Just install hr-luncheon-voucher, all dependencies will be installed by default.

Known issues / Roadmap
======================

Bug Tracker
===========
Bugs are tracked on `GitHub Issues
<https://github.com/elabore-coop/hr-tools/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smashing it by providing a detailed and welcomed feedback.

Credits
=======

Images
------
* Elabore: `Icon <https://elabore.coop/web/image/res.company/1/logo?unique=f3db262>`_.

Contributors
------------
* Stéphan Sainléger <https://github.com/stephansainleger>

Funders
-------
The development of this module has been financially supported by:
* Elabore (https://elabore.coop)
* Amaco (https://amaco.org)

Maintainer
----------
This module is maintained by ELABORE.

""",
    "depends": [
        "base",
        "calendar",
        "hr",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/event_type.xml",
        "views/hr_employee_views.xml",
        "views/hr_lv_allocation_views.xml",
        "views/menus.xml",
        "wizard/generate_lv_allocations_wizard.xml",
        "data/event_type_data.xml",
    ],
    "qweb": [],
}
