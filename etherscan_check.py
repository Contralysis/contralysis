import os
import requests
from dotenv import load_dotenv
from bs4 import BeautifulSoup

load_dotenv()

API_KEY = os.getenv('ETHERSCAN_API_KEY')

def get_bytecode(address):
    url = f'https://oko.palkeo.com/{address}/code/'

    response = requests.get(url)
    
    if response.status_code != 200:
        return False
        raise Exception(f"Failed to retrieve the URL: {url} (Status code: {response.status_code})")
        
    soup = BeautifulSoup(response.content, 'html.parser')
    
    content = soup.find(class_='content')
    if not content:
        return False
        raise Exception("No element with class 'content' found on the page.")
    
    highlighted_texts = content.find_all(class_='highlight')
    
    # Concatenate the text inside these elements
    concatenated_text = ''.join([element.get_text() for element in highlighted_texts])
    
    return concatenated_text


def check_address(address):
    url = f'https://api-sepolia.etherscan.io/api?module=contract&action=getsourcecode&address={address}&apikey={API_KEY}'
    response = requests.get(url)
    data = response.json()


    if response.status_code != 200:
        return 'error', None

    if data['status'] == '0':
        return data

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
            # convert byte code to source code 
            return get_bytecode(address)

print(check_address('0x95222290DD7278Aa3Ddd389Cc1E1d165CC4BAfe5'))
if API_KEY != None and API_KEY != "":
    print("there are api key\n")
    print(API_KEY)
    
