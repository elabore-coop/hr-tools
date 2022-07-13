# -*- coding: utf-8 -*-

from odoo import fields, models, _


class MeetingType(models.Model):

    _inherit = "calendar.event.type"

    ref = fields.Char(
        string=_("Reference"),
        copy=False,
        store=True,
    )
    remove_luncheon_voucher = fields.Boolean(
        string=_("Remove luncheon voucher"),
        copy=True,
        store=True,
    )
