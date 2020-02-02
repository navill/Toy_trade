import requests
import json


def get_client_ip():
    # test ip_address - 역삼동
    # ip_address = '27.1.185.30'
    # test ip_address - 논현동
    ip_address = '27.1.175.30'

    # ip = requests.get('https://api.ip.pe.kr/json/')
    # ip = json.loads(ip.text)['ip']

    return ip_address  # 논현동