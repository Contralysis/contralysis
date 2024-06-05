# import requests

# API_KEY = '1KCV8T5FCSQJ2MGSBZFM9BQ933VX1T3PA8'

# def check_address(address):
#     url = f'https://api.etherscan.io/api?module=contract&action=getsourcecode&address={address}&apikey={API_KEY}'
#     response = requests.get(url)
#     data = response.json()

#     if response.status_code != 200:
#         return 'error', None

#     if data['status'] == '1':
#         if data['result'] == '':  # Empty result indicates a wallet address
#             return 'wallet', None
#         elif data['result'][0]['SourceCode']:  # Check if source code is present
#             return 'contract', data['result'][0]['SourceCode']
#         else:
#             return 'error', None
#     else:
#         return 'error', None

import requests

API_KEY = '1KCV8T5FCSQJ2MGSBZFM9BQ933VX1T3PA8'

def check_address(address):
    url = f'https://api-sepolia.etherscan.io/api?module=contract&action=getsourcecode&address={address}&apikey={API_KEY}'
    response = requests.get(url)
    data = response.json()

    if response.status_code != 200:
        return 'error', None

    if data['status'] == '1':
        if data['result'][0]['SourceCode'] == '':  # Empty result indicates a wallet address
            return 'wallet', None
        elif data['result'][0]['SourceCode']:  # Check if source code is present
            return 'contract', data['result'][0]['SourceCode']
        else:
            return 'error', None
    else:
        return 'error', None
    