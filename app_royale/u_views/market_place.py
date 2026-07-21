from django.shortcuts import render
from app_royale.year_gen import year_gen
from django_ratelimit.decorators import ratelimit
from sys_views.rate_limit_key import getKey
import random
from datetime import datetime


@ratelimit(key=getKey, rate='20/m', block=True)
def market_place(request):
    """ Display Softwares to be sold in the market. The Meta data includes brief
        description of the software.

    Args:
        request (HTTPRequest): only the request method is needed and used

    Returns:
        HTTPResponse: Rendered HTML response.
    """
    context = {
        'year': year_gen(),
        'products': [
            {
                'name': 'Wi-Fi Hotspot',
                'version': '25.7',
                'icon': 'fas fa-wifi',
                'description': 'ROYALE Free WiFi Hotspot Software delivers reliable, stable internet sharing for small-scale operations. Even if you are using "Pay-WiFi" services, hotspot will still works. Designed for cafes, small offices, and home networks, this solution provides essential hotspot management features without the complexity or cost. Supports up to 10 concurrent users with seamless connectivity.',
                'old_price': 110,
                'new_price': 80,
                'badge': 'free',
                'features': ['10 Users', 'Stable', 'Small Office', 'Hotspot'],
                'premium': False,
                'info_url': '/market/softwares/hotspot/',
                'buy_url': '/market/purchased/'
            },
            {
                'name': 'Wi-Fi Hotspot Premium',
                'version': '31.2',
                'icon': 'fas fa-wifi',
                'description': 'ROYALE Premium WiFi Hotspot Software delivers enterprise-grade performance without the enterprise price tag. Made to hotspot using "PayWiFi" providers, so —Pay once and use with firends. Supports up to 255 concurrent users with zero lag, advanced management tools, and priority support. Built for businesses that demand reliability, speed, and scale. Extras; Social media blocking, Ads blocking, viewing sites your friends accessed with your wifi.',
                'old_price': 190,
                'new_price': 150,
                'badge': 'premium',
                'features': ['255 Users', 'Zero Lag', 'Enterprise', 'Priority Support'],
                'premium': True,
                'info_url': '/market/softwares/hotspot/',
                'buy_url': '/market/purchased/'
            },
        ]
    }
    return render(request, 'market_place.html', context)

@ratelimit(key=getKey, rate='20/m', block=True)
def softwares_toSale_hotspot(request):
    return render(request, 'softwares_hotspot.html', {'year': year_gen()})

def after_purchase(request):
    context = {
        'year': year_gen(),
        'order_id': random.randint(0000, 9999),
        'timestamp': datetime.now().strftime("%d-%m-%Y %H:%M:%S")
    }
    return render(request, 'after_purchase.html', context)