# sys_views/rate_limit_key.py

import hashlib

def getKey(group, request):
    """
    Generate a rate limit key with essential factors.
    """
    ip = request.META.get('HTTP_X_FORWARDED_FOR', request.META.get('REMOTE_ADDR', '0.0.0.0'))
    if ',' in ip:
        ip = ip.split(',')[0].strip()
    user_agent = request.META.get('HTTP_USER_AGENT', 'unknown')[:50]
    accept_language = request.META.get('HTTP_ACCEPT_LANGUAGE', 'unknown')[:30]
    platform = request.META.get('HTTP_SEC_CH_UA_PLATFORM', 'unknown')
    raw_key = f"{ip}|{user_agent}|{accept_language}|{platform}"
    hashed_key = hashlib.sha256(raw_key.encode()).hexdigest()[:32]
    
    return hashed_key