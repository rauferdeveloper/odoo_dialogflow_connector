# -*- coding: utf-8 -*-
{
    'name': "Odoo Dialogflow Connector",

    'summary': """Connect Dialogflow with Odoo ERP""",

    'description': """
        This module connect dialogflow with odoo and create events and opportunities
    """,
    "category": "Tools",
    'version': "15.0.0.1",
    "website": "https://github.com/rauferdeveloper",
    "author": "Raúl Fernández",
    "license": "LGPL-3",
    'depends': [
        'base',
        'contacts',
        'calendar',
        'crm'
    ],
    'data': [
        'data/settings.xml'

    ],
    'application': True,
    "installable": True,
}
