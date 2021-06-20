# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
import pytz as tz
from datetime import datetime, timedelta
import telebot
import logging

class Meeting(models.Model):
    _inherit = "calendar.event"
    
    def create_event_dialogflow(self, output_contexts, parameters_result, partner, valueRequest):
        TOKEN_BOT_TELEGRAM = self.env['ir.config_parameter'].sudo().get_param('telegram_token')
        bot = telebot.TeleBot(TOKEN_BOT_TELEGRAM)

        calendar_event_obj = self.env[self._name]
        vals = {}
        name_event = ''
        time = ''
        datetime_event = ''
        for out in output_contexts:
            if out.get('lifespanCount'):
                parameters = out['parameters']
                for key, param in parameters.items():
                    if key == 'date':
                        datetime_event = param
                    elif key == 'time':
                        time = param
        # Create event
        if datetime_event:
            datetime_event = datetime_event[:10] +' ' + datetime_event[11:19]
            datetime_event = datetime.strptime(datetime_event, DEFAULT_SERVER_DATETIME_FORMAT) 
        if time:
            time = time[:10] +' ' + time[11:19]
          
            time = datetime.strptime(time, DEFAULT_SERVER_DATETIME_FORMAT)
            timezone = tz.timezone("Europe/Madrid")
            local_date = timezone.localize(time, is_dst=None)
            date_utc = local_date.astimezone(tz.utc)

            name_event = valueRequest['queryResult']['queryText']
        end_time = datetime_event + timedelta(minutes=1)
        datetime_event = datetime(datetime_event.year, datetime_event.month, datetime_event.day, date_utc.hour, date_utc.minute)
        end_time =  datetime(datetime_event.year, datetime_event.month, datetime_event.day, date_utc.hour , date_utc.minute + 1)
        vals = {
            'allday':True,
            'name': name_event,
            'start': datetime_event,
            'stop': end_time,
        }
        if partner:
            vals['partner_ids'] = [(4, partner.id)]
            if partner.user_ids:
                vals['user_id'] = partner.user_ids[0].id
        new_event = calendar_event_obj.create(vals)
           
        if new_event:
            bot.send_message(int(partner.telegram_user_id), "Se ha guardado el evento, Gracias")
       
        name_event = ''
        time = ''
        datetime_event = ''
        vals = {}
        