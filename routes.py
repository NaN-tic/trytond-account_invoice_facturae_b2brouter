# This file is part of Tryton.  The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.
import logging
from werkzeug.exceptions import abort
from trytond.wsgi import app
from trytond.protocols.wrappers import with_pool, with_transaction


logger = logging.getLogger(__name__)


@app.route('/b2brouter', methods=['GET', 'POST', 'PUT'])
@with_pool
@with_transaction()
def invoice_state(request, pool):
    print('REQUEST CORRECTA')
    Invoice = pool.get('account.invoice')

    invoice_id = request.json().get('invoice_id')
    invoices = Invoice.search([('b2b_router_id', '=', invoice_id)], limit=1)
    if not invoices:
        return abort(405)
    invoice, = invoices
    invoice.b2b_router_state = request.json().get('state')
    invoice.save()

