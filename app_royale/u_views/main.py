from django.shortcuts import render

def main_page(request):
    return render(request, "main_page.html")

def products(request):
    return render(request, "products.html")