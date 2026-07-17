from django.shortcuts import render
from app_royale.year_gen import year_gen
from django_ratelimit.decorators import ratelimit
from sys_views.rate_limit_key import getKey

@ratelimit(key=getKey, rate='20/m', block=True)
def contact_us(request):
    return render(request, "contact.html", {'year': year_gen()})