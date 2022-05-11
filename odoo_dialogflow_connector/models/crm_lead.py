# -*- coding: utf-8 -*-

import logging
from odoo import models, fields, api, _


class CrmLead(models.Model):
    _inherit = "crm.lead"

    telegram_user_id = fields.Char(string='User ID Telegram')
    telegram_username = fields.Char(string='Username Telegram')

    def _prepare_customer_values(self, partner_name, is_company, parent_id=False):
        lead_partner_data = super(CrmLead, self)._prepare_customer_values(
            partner_name, is_company, parent_id
        )
        if self.telegram_user_id and self.telegram_username:
            lead_partner_data.update({
                'telegram_user_id': self.telegram_user_id,
                'telegram_username': self.telegram_username,
            })
        return lead_partner_data
        