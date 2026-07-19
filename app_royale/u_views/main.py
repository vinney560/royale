from django.shortcuts import render
from django.http import HttpResponse
from datetime import datetime
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

@ratelimit(key=getKey, rate='20/m', block=True)
def song_search(request):
    return render(request, "song_search.html", {"year": year_gen()})
# ============================================================
# Privacy Policy & Terms of Usage
# ============================================================
def terms(request):
    context = {
        "last_updated": "July 17, 2026",
        "year": year_gen()
    }
    return render(request, "terms.html", context)
def privacy(request):
    context = {
        "last_updated": "July 17, 2026",
        "year": year_gen()
    }
    return render(request, "privacy.html", context)
# ============================================================
# ROBOTS.TXT
# ============================================================

def robots_txt(request):
    lines = [
        "User-agent: *",
        "Allow: /",
        "",
        "Disallow: /admin/",
        "Disallow: /static/admin/",
        "Disallow: /api/",
        "Disallow: /accounts/",
        "Disallow: /profile/",
        "",
        "Allow: /static/css/",
        "Allow: /static/js/",
        "Allow: /static/uploads/",
        "",
        "Sitemap: https://royale.de5.net/sitemap.xml",
        "Crawl-delay: 1",
    ]
    return HttpResponse("\n".join(lines), content_type="text/plain")


# ============================================================
# SITEMAP.XML
# ============================================================

class PageSitemap:
    """Define page priority and changefreq for each URL"""
    
    PAGES = {
        # Main pages
        '/': {'priority': '1.0', 'changefreq': 'weekly'},
        '/about/': {'priority': '0.8', 'changefreq': 'monthly'},
        '/contact/': {'priority': '0.8', 'changefreq': 'monthly'},
        '/profile/': {'priority': '0.5', 'changefreq': 'monthly'},

        # Legal pages
        '/terms/': {'priority': '0.8', 'changefreq': 'yearly'},
        '/privacy/': {'priority': '0.8', 'changefreq': 'yearly'},

        # Products
        '/products/': {'priority': '0.9', 'changefreq': 'weekly'},
        '/products/qr/': {'priority': '0.7', 'changefreq': 'weekly'},
        '/products/qr/scr/': {'priority': '0.5', 'changefreq': 'monthly'},
        '/products/qr/api-keys/': {'priority': '0.5', 'changefreq': 'monthly'},
        '/products/pretty-printer/scr/': {'priority': '0.5', 'changefreq': 'monthly'},
        '/products/web-scraper/': {'priority': '0.7', 'changefreq': 'weekly'},
        '/products/song-search/': {'priority': '0.7', 'changefreq': 'weekly'},
        '/products/tv/': {'priority': '0.7', 'changefreq': 'weekly'},

        # Market
        '/market/place/': {'priority': '0.8', 'changefreq': 'weekly'},
        '/market/softwares/hotspot/': {'priority': '0.7', 'changefreq': 'weekly'},

        # Downloaders
        '/downloader/fb/': {'priority': '0.8', 'changefreq': 'weekly'},
        '/downloader/instagram/': {'priority': '0.8', 'changefreq': 'weekly'},

        # Learning
        '/learn/': {'priority': '0.7', 'changefreq': 'weekly'},
        '/learn/c/': {'priority': '0.6', 'changefreq': 'monthly'},
        '/learn/html/': {'priority': '0.6', 'changefreq': 'monthly'},
        '/learn/flowchart/': {'priority': '0.6', 'changefreq': 'monthly'},

        # Viu Live
        '/viulive/': {'priority': '1.0', 'changefreq': 'weekly'},

        # Special files
        '/robots.txt': {'priority': '0.1', 'changefreq': 'yearly'},
        '/sitemap.xml': {'priority': '0.1', 'changefreq': 'yearly'},
    }    

    @classmethod
    def get_all_urls(cls):
        """Return all URLs with their metadata"""
        urls = []
        for url, data in cls.PAGES.items():
            urls.append({
                'url': url,
                'priority': data.get('priority', '0.5'),
                'changefreq': data.get('changefreq', 'weekly'),
            })
        return urls

def sitemap_xml(request):
    today = datetime.now().strftime('%Y-%m-%d')
    domain = 'https://royale.de5.net'
    
    xml_lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"',
        '        xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"',
        '        xsi:schemaLocation="http://www.sitemaps.org/schemas/sitemap/0.9',
        '        http://www.sitemaps.org/schemas/sitemap/0.9/sitemap.xsd">',
    ]
    
    for page in PageSitemap.get_all_urls():
        xml_lines.append('    <url>')
        xml_lines.append(f'        <loc>{domain}{page["url"]}</loc>')
        xml_lines.append(f'        <lastmod>{today}</lastmod>')
        xml_lines.append(f'        <changefreq>{page["changefreq"]}</changefreq>')
        xml_lines.append(f'        <priority>{page["priority"]}</priority>')
        xml_lines.append('    </url>')
    
    xml_lines.append('</urlset>')
    
    return HttpResponse('\n'.join(xml_lines), content_type='application/xml')
# =======================================================