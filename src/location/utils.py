from django.conf import settings

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


# @with_ip_geolocation
# def get_client_city_data(request):
#     IP2LocObj = IP2Location.IP2Location()
#     geo_dir = settings.GEO_DIR
#     IP2LocObj.open(geo_dir+'/IP2LOCATION-LITE-DB3.BIN')
#     # print(geo_dir)
#
#
#
#     ip_address = get_client_ip(request)
#     print(ip_address)
#     rec = IP2LocObj.get_all('192.168.200.106')
#     print(rec.region)
#     # gl = request.geolocation
#     print(ip_address)
