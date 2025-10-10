import requests

url = "https://app-staging.b2brouter.net/users/invoice_states.json"
#url = "https://app.b2brouter.net/users/invoice_states.json"

headers = {
    "accept": "application/json",
    "X-B2B-API-Key": "POSAR EL CODI DEL CLIENT"
}

response = requests.get(url, headers=headers)

print(response.text)
