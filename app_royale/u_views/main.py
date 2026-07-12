from django.shortcuts import render
from app_royale.year_gen import year_gen

def main_page(request):
    return render(request, "main_page.html", {"year": year_gen()})

def products(request):
    return render(request, "products.html", {"year": year_gen()})

def about_us(request):
    return render(request, "about_us.html", {"year": year_gen()})