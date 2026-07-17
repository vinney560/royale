from django.shortcuts import render
from app_royale.year_gen import year_gen

def insta_downloader(request):
    return render(request, "insta_downloader.html", {'year': year_gen()})