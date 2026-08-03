
def get_client_id(request):
    """
    Get Client Ip.
    """
    ip = request.META.get('REMOTE_ADDR')
    return ip