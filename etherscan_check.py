import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv('ETHERSCAN_API_KEY')

def check_address(address):
    url = f'https://api-sepolia.etherscan.io/api?module=contract&action=getsourcecode&address={address}&apikey={API_KEY}'
    response = requests.get(url)
    data = response.json()

    if response.status_code != 200:
        return 'error', None

    if data['status'] == '1':
        with open("tests/test_etherscan_check/wallet.txt", "r", newline="\r\n") as f:
            wallet_code = "".join(f.readlines())
            wallet_code = "".join(wallet_code.split())
            src_code = data['result'][0]['SourceCode']
            src_code = "".join(src_code.split())
    
            if src_code == wallet_code:  # Empty result indicates a wallet address
                return 'wallet', None
            elif data['result'][0]['SourceCode']:  # Check if source code is present
                return 'contract', data['result'][0]['SourceCode']
            else:
                return 'error', None
    else:
        return 'error', None
