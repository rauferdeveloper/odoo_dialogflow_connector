# -*- coding: utf-8 -*-

import json
import logging
from datetime import datetime
import time
import dateutil.parser
import telebot

from odoo import http, _

from odoo.http import Response
from odoo.http import request
from odoo.tools import safe_eval
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT

_logger = logging.getLogger(__name__)

class MainApi(http.Controller):

    @http.route(['/webhook/data/create'], methods=['POST'], type="json", auth="public", csrf=False, website=True)
    def api_dialog_create(self, **kwargs):
        TOKEN_BOT_TELEGRAM = request.env['ir.config_parameter'].sudo().get_param('telegram_token')
        bot = telebot.TeleBot(TOKEN_BOT_TELEGRAM)
        valueRequest = request.jsonrequest
        app_message = valueRequest['originalDetectIntentRequest']
        calendar_event_obj = request.env['calendar.event'].sudo()
        res_partner_obj = request.env['res.partner'].sudo()
        crm_lead_obj = request.env['crm.lead'].sudo()
        output_contexts = request.jsonrequest['queryResult']['outputContexts']
        parameters = request.jsonrequest['queryResult']['parameters']
        email = parameters.get('email')
        traervento = parameters.get('traerevento')
        if app_message.get('source') in ['telegram']:
            user_telegram_id = str(int(app_message['payload']['data']['from']['id']))
            user_telegram_name = app_message['payload']['data']['from']['username']
            
            search_partner = res_partner_obj.search([
                ('telegram_user_id', '=', user_telegram_id),
                ('user_ids', '!=', False)
            ])
            if search_partner:
                if traervento:
                    calendar_event_obj.get_event_dialogflow(output_contexts, parameters, search_partner, valueRequest)
                else:
                    calendar_event_obj.create_event_dialogflow(output_contexts, parameters, search_partner, valueRequest)
            else:
                if email:
                    search_partner = res_partner_obj.search([
                        ('email', '=', email),
                        ('user_ids', '!=', False)
                    ])
                    if search_partner:
                        search_partner.write({'telegram_user_id': user_telegram_id})
                        bot.send_message(int(search_partner.telegram_user_id), "Se han guardado tus datos.\nMuchas gracias!")

                    else:
                        search_crm_lead = crm_lead_obj.search([('telegram_user_id', '=', user_telegram_id)])
                        if search_crm_lead:
                            bot.send_message(int(search_crm_lead.telegram_user_id), "Ya esta guardada tu informacíón\nGracias.")
                        else:
                            new_crm = crm_lead_obj.create({
                                'type': 'lead',
                                'telegram_user_id': user_telegram_id,
                                'telegram_username': user_telegram_name,
                                'name': user_telegram_name,
                                'email_from': email
                            })
                            bot.send_message(int(new_crm.telegram_user_id), 'Se han guardado tus datos.\nMuchas gracias!')
        
        