# This file is part account_invoice_facturae_b2brouter module for Tryton.
# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
from trytond.pool import Pool
from . import invoice
from . import cron

def register():
    Pool.register(
        invoice.Invoice,
        invoice.GenerateFacturaeStart,
        cron.Cron,
        module='account_invoice_facturae_b2brouter', type_='model')
