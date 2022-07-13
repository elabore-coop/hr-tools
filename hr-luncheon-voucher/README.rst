===================
HR Luncheon Voucher
===================

.. |badge1| image:: https://img.shields.io/badge/maturity-Beta-yellow.png
    :target: https://odoo-community.org/page/development-status
    :alt: Beta
.. |badge2| image:: https://img.shields.io/badge/licence-AGPL--3-blue.png
    :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
    :alt: License: AGPL-3
.. |badge3| image:: https://img.shields.io/badge/github-OCA%2Faccount--analytic-lightgray.png?logo=github
    :target: https://github.com/elabore-coop/hr-tools
    :alt: elabore/hr-tools

|badge1| |badge2| |badge3|

This module allows the management of Luncheon Vouchers attribution and distribution.
Employees can  indicate which days are not concerned by luncheon vouchers.
HR managers can ajust the number of luncheon vouchers to distribute, and follow each employee credit.

Installation
============
Use Odoo normal module installation procedure to install ``hr-luncheon-voucher``.

Configuration
=============
1. Go to ``Configuration > Technical > Calendar > Meeting Types`` and define the meeting categories which cancel the daily luncheon voucher distribution.
2. Go to ``Configuration > General Settings > Employees`` and define if employees need to work the whole day to get a luncheon voucher.
3. Go to ``Employees`` and define for each employee the default number of luncheon vouchers to distribute in each distribution campaign.

Use
===
- when an calendar event makes the luncheon voucher distribution cancelled (Off-site or free lunch for instance), add the corresponding category to the event.
- for each distribution period, the HR manager should:
    - go in ``Employees`` tree view
    - select all the employees concerned by luncheon vouchers distribution
    - click on header button ``Generate luncheon vouchers allocation``
    - Fill the wizard form
- a voucher allocation request is created for each employee
- HR manager confirms an allocation request when the figures are confirmed
- HR manager marks the requests as "Distributed" when the vouchers has been effectively distributed
- HR manager can correct the allocation requests with ``Back to draft`` button
- employees' luncheon voucher counters are updated considering the vouchers acquired, dued and distributed at each campaign.

**Attribution rules:**

- a luncheon voucher is acquired for a working day if:
    - the employee worked on one or all the attendances of the day (depending if option ``Half working days cancel luncheon vouchers`` is True or not)
    - there is no meeting which cancel the voucher during that day (``Site off`` or ``Free lunch`` meeting for instance)
- an attendance is considered as worked as long as there is no leave on the whole attendance time slot

Known issues / Roadmap
======================
None yet.

Bug Tracker
===========
Bugs are tracked on `GitHub Issues
<https://github.com/elabore-coop/hr-tools/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smashing it by providing a detailed and welcomed feedback.

Credits
=======

Contributors
------------
- Stéphan Sainléger <https://github.com/stephansainleger>

Funders
-------
The development of this module has been financially supported by:

- Elabore (https://elabore.coop)
- Amaco (https://amaco.org)

Maintainer
----------
This module is maintained by ELABORE.
