import requests
import json
from naver_geolocation import get_address


def get_client_ip():
    ip = requests.get('http://ip.jsontest.com')
    ip = json.loads(ip.text)['ip']
    return ip


def get_client_city_data(ip_address):
    # public ip 획득
    user_address = get_address(ip_address)

    return user_address
