from django.shortcuts import render
from app_royale.year_gen import year_gen
from django_ratelimit.decorators import ratelimit
from sys_views.rate_limit_key import getKey

@ratelimit(key=getKey, rate='20/m', block=True)
def main_page(request):
    return render(request, "main_page.html", {"year": year_gen()})

@ratelimit(key=getKey, rate='20/m', block=True)
def profile_page(request):
    return render(request, "profile.html", {"year": year_gen()})

@ratelimit(key=getKey, rate='20/m', block=True)
def products(request):
    return render(request, "products.html", {"year": year_gen()})

@ratelimit(key=getKey, rate='20/m', block=True)
def about_us(request):
    return render(request, "about_us.html", {"year": year_gen()})

@ratelimit(key=getKey, rate='20/m', block=True)
def qr_code_gen(request):
    return render(request, "qr_code_gen.html", {"year": year_gen()})

@ratelimit(key=getKey, rate='20/m', block=True)
def qr_api_keys(request):
    api_keys = [
        'RoyaleIe56Wx1NZg5wZOde8legJEvaMS5SCU',
        'Royalemx964pT50XIZuylUDmzAYvIuD4QguR',
        'Royales2fePluzZFFGyzGuYJ2wsJNUOyHLE0',
        'RoyaleYNkzLRh9KavZgujPoJHC4c1vrXXfLq',
        'RoyaleR7j2rV1MgiBmT5lTxxWaQSIe8nxU0a',
        'RoyaleSSJXKi4U1qHHDopnrDSzx0RWOulLYF',
    ]
    return render(request, "qr_api_keys.html", {"year": year_gen(), "api_keys": api_keys})

@ratelimit(key=getKey, rate='20/m', block=True)
def royale_tv(request):
    return render(request, "royale_tv.html")

# def buy_royale_tv():

"""
    src -> we render the source code of a script where :-
    filename -> the name of the script file (with txt)
    page_title -> the title of the page
    code_lang -> the language of the code (e.g. py, js, html, css, cpp, java, php, etc)
    year -> the current year
"""
@ratelimit(key=getKey, rate='20/m', block=True)
def qr_gen_scr(request):
    context = {
        "year": year_gen(), 
        "filename": "qr_gen_scr.txt", 
        "page_title": "QR Generator Source", 
        "code_lang": "py"
        }
    return render(request, "scr_code.html", context)

@ratelimit(key=getKey, rate='20/m', block=True)
def pretty_printer_src(request):
    context = {
        "year": year_gen(), 
        "filename": "pretty_printer.txt", 
        "page_title": "Pretty Printer", 
        "code_lang": "py"
        }
    return render(request, "scr_code.html", context)