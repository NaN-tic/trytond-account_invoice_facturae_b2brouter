import requests
from trytond.modules.account_invoice_facturae_b2brouter.invoice import (
    B2BROUTER_API_VERSION)

url = "https://api-staging.b2brouter.net/invoice_states"
#url = "https://api.b2brouter.net/invoice_states"

headers = {
    "accept": "application/json",
    "X-B2B-API-Key": "POSAR EL CODI DEL CLIENT",
    "X-B2B-API-Version": B2BROUTER_API_VERSION,
}

response = requests.get(url, headers=headers)

print(response.text)
