from django.shortcuts import render
from django.http import JsonResponse
from django_ratelimit.decorators import ratelimit
from sys_views.rate_limit_key import getKey

# ============================================================
# CUSTOM ERROR VIEWS
# ============================================================

@ratelimit(key=getKey, rate='5/m', block=True)
def handler_404_request(request, exception):
    """Custom 404 page handler"""
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'error': 'Page Not Found',
            'message': 'The requested resource was not found.'
        }, status=404)
    
    context = {
        'error_code': 404,
        'error_title': 'Page Not Found',
        'error_message': 'The page you are looking for does not exist.',
    }
    return render(request, "errors/404.html", context, status=404)


def handler_500_request(request):
    """Custom 500 page handler"""
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'error': 'Server Error',
            'message': 'Something went wrong on our end.'
        }, status=500)
    
    context = {
        'error_code': 500,
        'error_title': 'Server Error',
        'error_message': 'We are experiencing technical difficulties. Please try again later.',
    }
    return render(request, "errors/500.html", context, status=500)


@ratelimit(key=getKey, rate='5/m', block=True)
def handler_403_request(request, exception):
    """Custom 403 page handler"""
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'error': 'Access Denied',
            'message': 'You do not have permission to access this resource.'
        }, status=403)
    
    context = {
        'error_code': 403,
        'error_title': 'Access Denied',
        'error_message': 'You do not have permission to view this page.',
    }
    return render(request, "errors/403.html", context, status=403)


def handler_400_request(request, exception):
    """Custom 400 page handler"""
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'error': 'Bad Request',
            'message': 'The request could not be processed.'
        }, status=400)
    
    context = {
        'error_code': 400,
        'error_title': 'Bad Request',
        'error_message': 'The request could not be understood.',
    }
    return render(request, "errors/400.html", context, status=400)

def handler_429_request(request, exception):
    """Custom 429 page handler"""
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'error': 'Too Many Request',
            'message': 'Too many requests. Let the server grasp so air!'
        }, status=429)
    
    return render(request, "errors/429.html", status=429)