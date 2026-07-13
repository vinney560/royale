from django.shortcuts import render
from app_royale.year_gen import year_gen

def main_page(request):
    return render(request, "main_page.html", {"year": year_gen()})

def products(request):
    return render(request, "products.html", {"year": year_gen()})

def about_us(request):
    return render(request, "about_us.html", {"year": year_gen()})

def qr_code_gen(request):
    return render(request, "qr_code_gen.html", {"year": year_gen()})
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

def qr_gen_scr(request):
    page_title = "QR Generator Source"
    code_lang="py" # we use extension (e.g. py, js, html, css, cpp, java, php, etc)
    filename = "qr_gen_scr.txt" # BASE DIR is /static/scr_code
    return render(request, "scr_code.html", 
                  {"year": year_gen(), "filename": filename, "page_title": page_title, "code_lang": code_lang})
