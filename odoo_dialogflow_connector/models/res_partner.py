# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class ResPartner(models.Model):
    _inherit = "res.partner"

    telegram_user_id = fields.Char(string='User ID Telegram')
    telegram_username = fields.Char(string='Username Telegram')

    