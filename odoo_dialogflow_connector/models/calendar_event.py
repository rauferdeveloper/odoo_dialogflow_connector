# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
import pytz as tz
from datetime import datetime, timedelta, time
import telebot
import logging


class Meeting(models.Model):
    _inherit = "calendar.event"

    def create_event_dialogflow(self, output_contexts, parameters_result, partner, valueRequest):
        TOKEN_BOT_TELEGRAM = self.env['ir.config_parameter'].sudo(
        ).get_param('telegram_token')
        bot = telebot.TeleBot(TOKEN_BOT_TELEGRAM)

        calendar_event_obj = self.env[self._name]
        vals = {}
        name_event = ''
        time_d = ''
        datetime_event = ''
        for out in output_contexts:
            if out.get('lifespanCount'):
                parameters = out['parameters']
                for key, param in parameters.items():
                    if key == 'date':
                        datetime_event = param
                    elif key == 'time':
                        if 'date_time' in param:
                            time_d = param['date_time']
                        else:
                            time_d = param
        # Create event
        if datetime_event:
            datetime_event = datetime_event[:10] + ' ' + datetime_event[11:19]
            datetime_event = datetime.strptime(
                datetime_event, DEFAULT_SERVER_DATETIME_FORMAT)
        if time_d:
            time_d = time_d[:10] + ' ' + time_d[11:19]

            time_d = datetime.strptime(time_d, DEFAULT_SERVER_DATETIME_FORMAT)
            timezone = tz.timezone("Europe/Madrid")
            local_date = timezone.localize(time_d, is_dst=None)
            date_utc = local_date.astimezone(tz.utc)
            if datetime_event == '':
                datetime_event = date_utc
            name_event = valueRequest['queryResult']['queryText']
        end_time = datetime_event + timedelta(minutes=1)
        datetime_event = datetime(datetime_event.year, datetime_event.month,
                                  datetime_event.day, date_utc.hour, date_utc.minute)
        end_time = datetime(datetime_event.year, datetime_event.month,
                            datetime_event.day, date_utc.hour, date_utc.minute + 1)
        vals = {
            'allday': False,
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
            bot.send_message(int(partner.telegram_user_id),
                             "Se ha guardado el evento, Gracias")

        name_event = ''
        time_d = ''
        datetime_event = ''
        vals = {}

    def get_event_dialogflow(self, output_contexts, parameters_result, partner, valueRequest):
        TOKEN_BOT_TELEGRAM = self.env['ir.config_parameter'].sudo(
        ).get_param('telegram_token')
        bot = telebot.TeleBot(TOKEN_BOT_TELEGRAM)

        calendar_event_obj = self.env[self._name]
        vals = {}
        name_event = ''
        time_d = ''
        datetime_event = ''
        hour_concret = False
        eventos = ''
        domain = [('user_id', '=', partner.user_ids[0].id)]
        for out in output_contexts:
            if out.get('lifespanCount'):
                parameters = out['parameters']
                for key, param in parameters.items():
                    if key == 'date':
                        datetime_event = param
                    elif key == 'time' and time_d == '':
                        if 'date-time' in param:
                            if param['date-time'] !='':
                                time_d = param['date_time']
                        else:
                            if param != '':
                                time_d = param
                            
                    elif key == 'date-time':
                        if 'date_time' in param:
                            if param['date_time'] !='':
                                time_d = param['date_time']
                        else:
                            if param != '':
                                time_d = param
        if time_d != '' and datetime_event == '':
            hour_concret = True
            time_d = time_d[:10] + ' ' + time_d[11:19]

            time_d = datetime.strptime(time_d, DEFAULT_SERVER_DATETIME_FORMAT)
            timezone = tz.timezone("Europe/Madrid")
            local_date = timezone.localize(time_d, is_dst=None)
            date_utc = local_date.astimezone(tz.utc)
            if datetime_event == '':
                datetime_event = date_utc
        # get event
        if datetime_event:
            if not hour_concret:
                datetime_event = datetime_event[:10] + ' ' + datetime_event[11:19]
                datetime_event = datetime.strptime(
                    datetime_event, DEFAULT_SERVER_DATETIME_FORMAT)
            # datetime_event_str = datetime_event.strftime('%d/%m/%Y')
            if not hour_concret:
                domain.append(('start', '>=', datetime.combine(datetime_event.date(), time(0,0,0))))
                domain.append(('start', '<=', datetime.combine(datetime_event.date(), time(23,59,59))))
            else: 
                domain.append(('start', '>=', datetime.combine(datetime_event.date(), time(datetime_event.hour,0,0))))
                domain.append(('start', '<=', datetime.combine(datetime_event.date(), time(datetime_event.hour,59,59))))
            events = calendar_event_obj.search(
                domain, order='start DESC')
            if events:
                eventos += 'Aquí tienes los eventos disponibles:\n\n'
                for i in range(len(events.ids)):
                    eventos += str(i+1) + ' - ' + events[i].name+' ✅ \n'

        if eventos == "":
            bot.send_message(int(partner.telegram_user_id),
                             "No tienes eventos disponibles con la fecha indicada, Gracias")
        else:
            bot.send_message(int(partner.telegram_user_id),
                             eventos)

        datetime_event = ""
