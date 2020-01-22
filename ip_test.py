import requests
import json
ip = requests.get('http://ip.jsontest.com')
# data = json.loads(urllib.urlopen("http://ip.jsontest.com/").read())
ip = json.loads(ip.text)['ip']
print(type(ip))
#
# from ipgetter2 import IPGetter
#
# getter = IPGetter()
# a = getter.get()
# print(a)