# This file is part account_invoice_facturae_b2brouter module for Tryton.
# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
from trytond.pool import Pool
from trytond.tests.test_tryton import ModuleTestCase, with_transaction


class AccountInvoiceFacturaeB2brouterTestCase(ModuleTestCase):
    'Test Account Invoice Facturae B2BRouter module'
    module = 'account_invoice_facturae_b2brouter'

    @with_transaction()
    def test_facturae_service_configuration(self):
        "B2BRouter is available as a company-dependent Factura-e service"
        pool = Pool()
        ConfigurationFacturae = pool.get('account.configuration.facturae')

        selection = ConfigurationFacturae.fields_get(
            ['facturae_service'])['facturae_service']['selection']

        self.assertIn(('b2brouter', 'B2BRouter'), selection)


del ModuleTestCase
