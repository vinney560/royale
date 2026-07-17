from django.shortcuts import render
from django.http import JsonResponse, StreamingHttpResponse
from app_royale.year_gen import year_gen
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse

from sys_views.pretty_printer import print_error

def web_scraper(request):
    return render(request, 'web_scraper.html', { 'year': year_gen()})

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
    'DNT': '1',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'none',
    'Sec-Fetch-User': '?1',
    'Cache-Control': 'max-age=0',
    'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
}

class ScrapeURL:
    def __init__(self):
        pass
    
    def fetch(self, url):
        try:
            response = requests.get(url, headers=HEADERS, timeout=10)
            response.raise_for_status()

            # encoding handling
            # print the encoding of result
            print(f"[Result Encoding] {response.encoding}")
            # ======= DEBUG ===============
            print(f"[Result] {response.text[:300]}")
            response.encoding = response.apparent_encoding or 'utf-8'
            html = response.text

            soup = BeautifulSoup(html, 'html.parser')
            return soup.prettify()
        except requests.exceptions.Timeout:
            print_error("Request timed out")
            return 1
        except requests.exceptions.ConnectionError:
            print_error("Connection error")
            return 2
        except requests.exceptions.HTTPError as e:
            print_error(f"HTTP error: {e}")
            return 3
        except Exception as e:
            print_error(f"Unexpected error: {e}")
            return 4

# Crreate an Instance
scraper = ScrapeURL()

def scrape(request):
    if request.method == 'POST':
        url = request.POST.get('url')
        if not url:
            return JsonResponse({
                'success': False,
                'message': 'Please provide a URL to scrape'
            }, status=400)
    
        # Validate URL format
        parsed = urlparse(url)
        if not parsed.scheme or not parsed.netloc:
            return JsonResponse({
                'success': False,
                'message': 'Please provide a valid URL with http:// or https://'
            }, status=400)
        
        result = scraper.fetch(url)
        if result == 1:
            return JsonResponse({
                'success': False,
                'message': 'Request timed out, please try again later'
            }, status=400)
        if result == 2:
            return JsonResponse({
                'success': False,
                'message': 'Connection error, check your internet connection'
            }, status=400)
        if result == 3:
            return JsonResponse({
                'success': False,
                'message': 'HTTP error, check the URL or try again later'
            }, status=400)
        if result == 4:
            return JsonResponse({
                'success': False,
                'message': 'Unexpected error, please try again later'
            }, status=400)

        import json
        response_data = json.dumps({
            'success': True,
            'html': result
        }, ensure_ascii=False)

        response_bytes = response_data.encode('utf-8')

        def generate():
            yield response_bytes

        response = StreamingHttpResponse(
            generate(),
            content_type='application/json; charset=utf-8'
        )
        response['Content-Type'] = 'application/json; charset=utf-8'
        response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response['Content-Encoding'] = 'identity'
        response['Vary'] = 'Accept-Encoding'

        return response
    else:
        return JsonResponse({'success': False, 'message': 'Invalid request method'})