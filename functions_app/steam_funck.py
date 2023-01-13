import requests
import random

def check_steam(acount_name):
    x = str(random.randint(1, 10))
    param = {'accountname': acount_name, 'count': x}
    url = f'https://store.steampowered.com/join/checkavail/'
    try:
        return requests.post(url, data=param).json()['bAvailable']
    except requests.exceptions.ConnectionError:
        return 'no_info'

def approximate_price(tenge):
    pass