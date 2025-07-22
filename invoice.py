# This file is part of Tryton.  The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.
import base64
import requests
import socket

from logging import getLogger

from trytond.pool import Pool, PoolMeta
from trytond.i18n import gettext
from trytond.exceptions import UserError
from trytond.config import config as config_
from trytond.model import fields
from datetime import timedelta

B2BROUTER_PRODUCTION = config_.getboolean('b2brouter', 'production', default=False)
B2BROUTER_ACCOUNT = config_.get('b2brouter', 'account', default=None)
B2BROUTER_API_KEY = config_.get('b2brouter', 'key', default=None)
B2BROUTER_BASEURL = ('https://app.b2brouter.net'
    if B2BROUTER_PRODUCTION else 'https://app-staging.b2brouter.net')

_logger = getLogger(__name__)

def basic_auth(username, password):
    token = base64.b64encode(f"{username}:{password}".encode('utf-8')).decode("ascii")
    return f'Basic {token}'


class Invoice(metaclass=PoolMeta):
    __name__ = 'account.invoice'

    b2brouter_id = fields.Integer('B2BRouter ID', readonly=True)
    b2brouter_state = fields.Char('B2BRouter State', readonly=True)

    @classmethod
    def __setup__(cls):
        super().__setup__()
        cls._check_modify_exclude |= {'b2brouter_id', 'b2brouter_state'}

    def generate_facturae(self, certificate=None, service=None):
        pool = Pool()
        Date = pool.get('ir.date')
        Configuration = pool.get('account.configuration')

        config = Configuration(1)

        if (self.invoice_date > Date.today() and
                ((service == 'b2brouter') or
                (not service and config.facturae_service == 'b2brouter'))):
            raise UserError(gettext(
                'account_invoice_facturae_b2brouter.msg_error_send_b2brouter_future',
                id=self.id))
        super().generate_facturae(certificate, service)

    def send_facturae_b2brouter(self):
        url = (
            "{base_url}/projects/{account}/invoices/import.json"
            "?send_after_import=true".format(
                base_url=B2BROUTER_BASEURL,
                account=B2BROUTER_ACCOUNT,
            )
        )

        payload = (
            "data:application/octet-stream;name=facturae-20250131.xsig;base64," +
            base64.b64encode(self.invoice_facturae).decode('utf-8')
        )
        headers = {
            "content-type": "application/octet-stream",
            "X-B2B-API-Key": B2BROUTER_API_KEY,
        }

        try:
            response = requests.post(url, data=payload, headers=headers)
        except Exception as message:
            _logger.warning(
                'Error send b2brouter factura-e: %s' % self.rec_name)
            raise UserError(gettext(
                'account_invoice_facturae_b2brouter.msg_error_send_b2brouter',
                invoice=self.rec_name,
                error=message))
        except:
            _logger.warning(
                'Error send b2brouter factura-e: %s' % self.rec_name)
            raise UserError(gettext(
                'account_invoice_facturae_b2brouter.msg_error_send_b2brouter',
                invoice=self.rec_name,
                error=''))

        try:
            if response.status_code in (200, 201):
                self.invoice_facturae_sent = True
                self.b2brouter_id = response.json().get('invoice').get('id')
                self.b2brouter_state = response.json().get('invoice').get(
                    'state')
                self.save()
            else:
                _logger.warning(
                    'Error send b2brouter factura-e status code: %s %s' % (
                        response.status_code, response.text))
                raise UserError(gettext(
                    'account_invoice_facturae_b2brouter.msg_error_send_b2brouter_status',
                    invoice=self.rec_name,
                    status_code=response.status_code,
                    text=response.text))
        except socket.timeout as err:
            _logger.warning(
                'Error send b2brouter factura-e timeout: %s' % self.rec_name)
            _logger.error('%s' % str(err))
            raise UserError(gettext(
                'account_invoice_facturae_b2brouter.msg_error_send_b2brouter_timeout',
                invoice=self.rec_name,
                error=str(err)))
        except socket.error as err:
            _logger.warning(
                'Error send b2brouter factura-e: %s' % self.rec_name)
            _logger.error('%s' % str(err))
            raise UserError(gettext(
                'account_invoice_facturae_b2brouter.msg_error_send_b2brouter_error',
                invoice=self.rec_name,
                error=str(err)))

    @classmethod
    def cron_update_invoice_b2brouter_state(cls):
        cls.update_invoice_b2brouter_state()

    @classmethod
    def update_invoice_b2brouter_state(cls):
        pool = Pool()
        Date = pool.get('ir.date')
        Config = pool.get('account.configuration')
        config = Config(1)
        today = Date.today()

        date_from = today - timedelta(days=config.b2brouter_state_update_days)
        date_to = config_.get('b2brouter', 'date_to', default=today)

        offset = 0
        limit = 500
        invoice_states = {}
        while True:
            url = (
                "{base_url}/projects/{account}/invoices.json?offset={offset}"
                "&limit={limit}&date_from={date_from}&date_to={date_to}"
                .format(
                    base_url=B2BROUTER_BASEURL,
                    account=B2BROUTER_ACCOUNT,
                    offset=offset,
                    limit=limit,
                    date_from=date_from,
                    date_to=date_to,
                    )
                )

            headers = {
                "accept": "application/json",
                "X-B2B-API-Key": B2BROUTER_API_KEY,
                }

            response = requests.get(url, headers=headers)
            if response.status_code != 200:
                raise UserError(gettext(
                    'account_invoice_facturae_b2brouter.msg_error_b2brouter',
                    error='%s %s' % (response.status_code, response.reason),
                    ))
            b2b_invoices = response.json().get('invoices')

            if not b2b_invoices:
                break

            for b2b_invoice in b2b_invoices:
                invoice_states[b2b_invoice.get('id')] = b2b_invoice.get('state')
            offset += limit

        invoices = cls.search([('b2brouter_id', 'in', invoice_states.keys())])
        for invoice in invoices:
            invoice.b2brouter_state = invoice_states[invoice.b2brouter_id]
            if invoice_states[invoice.b2brouter_id] == 'new':
                send_url = "{base_url}/invoices/send_invoice/{invoice_id}.json".format(
                    base_url=B2BROUTER_BASEURL,
                    invoice_id=invoice.b2brouter_id,
                    )
                send_headers = {
                    "accept": "application/xml",
                    "X-B2B-API-Key": B2BROUTER_API_KEY,
                    }
                requests.post(send_url, headers=send_headers)
        cls.save(invoices)




class GenerateFacturaeStart(metaclass=PoolMeta):
    __name__ = 'account.invoice.generate_facturae.start'

    @classmethod
    def __setup__(cls):
        super().__setup__()
        cls.service.selection += [('b2brouter', 'B2BRouter')]
