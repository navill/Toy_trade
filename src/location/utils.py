import requests
import json


def get_client_ip():
    # test ip_address - 역삼동
    # ip_address = '27.1.185.30'
    # ip_address = '27.1.173.100
    # test ip_address - 논현동
    # ip_address = '27.1.175.30'
    # 논현동
    # ip_address = '27.1.175.20'
    # 대치동
    # ip_address = {'ip': '27.1.174.100'}
    # 삼성동
    ip_address = {'ip': '27.1.180.100'}
    # ip = requests.get('https://api.ip.pe.kr/json/')
    # ip_address = json.loads(ip.text)['ip']
    return ip_address
