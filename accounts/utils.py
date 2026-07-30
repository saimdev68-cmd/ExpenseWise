
def get_client_id(request):
    ip = request.META.get('REMOTE_ADDR')
    return ip