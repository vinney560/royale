from django.http import JsonResponse

def more_products(request):
    page = int(request.GET.get('page', 1))
    search = request.GET.get('search', '').strip().lower()
    limit = int(request.GET.get('limit', 0))
    per_page = 4

    all_products = [
        {
            'id': 1,
            'name': 'YouTube Downloader',
            'description': 'Download videos, playlists, and audio from YouTube in high quality. Supports 4K, 60fps, and multiple formats including MP4, WebM, and MP3.',
            'icon': 'fab fa-youtube',
            'iconColor': 'text-red-400',
            'tags': ['Popular', '4K Support'],
            'link': 'https://google.com',
            'featured': True,
            'stats': {'downloads': '12K+', 'rating': '4.9'}
        },
        {
            'id': 2,
            'name': 'Facebook Downloader',
            'description': 'Save videos and reels from Facebook with one click. HD quality, no watermark, works on public and private posts. Supports 1080p.',
            'icon': 'fab fa-facebook',
            'iconColor': 'text-blue-400',
            'tags': ['HD Quality', 'No Watermark'],
            'link': '#',
            'featured': False,
            'stats': {'downloads': '8K+', 'rating': '4.7'}
        },
        {
            'id': 3,
            'name': 'Uptime & Pinger',
            'description': 'Monitor your websites 24/7. Get instant alerts on downtime, track response times, and keep your services online with 99.9% SLA.',
            'icon': 'fas fa-heartbeat',
            'iconColor': 'text-green-400',
            'tags': ['24/7', '99.9% SLA', 'Alerts'],
            'link': '#',
            'featured': False,
            'stats': {'uptime': '99.97%', 'alerts': 'Instant'}
        },
        {
            'id': 4,
            'name': 'Custom Scripts',
            'description': 'Need something specific? We build tailored automation scripts, web scrapers, API integrations, and custom software solutions for your business.',
            'icon': 'fas fa-terminal',
            'iconColor': 'text-teal-400',
            'tags': ['Bespoke', 'Automation', 'API'],
            'link': '#',
            'featured': True,
            'stats': {'projects': '200+', 'clients': '40+'}
        },
        {
            'id': 5,
            'name': 'Twitter Video Downloader',
            'description': 'Download videos from Twitter/X with ease. Supports HD quality, works with any tweet containing videos. Simple paste and download.',
            'icon': 'fab fa-twitter',
            'iconColor': 'text-sky-400',
            'tags': ['New', 'HD Quality'],
            'link': '#',
            'featured': False,
            'stats': {'downloads': '5K+', 'rating': '4.6'}
        },
        {
            'id': 6,
            'name': 'Instagram Downloader',
            'description': 'Save photos, videos, and reels from Instagram. No watermark, supports multiple formats. Works with public and private accounts.',
            'icon': 'fab fa-instagram',
            'iconColor': 'text-pink-400',
            'tags': ['Popular', 'No Watermark'],
            'link': '#',
            'featured': False,
            'stats': {'downloads': '9K+', 'rating': '4.8'}
        },
        {
            'id': 7,
            'name': 'Web Scraper API',
            'description': 'Extract data from any website with our powerful scraping API. Get structured data in JSON format. Supports pagination, proxies, and custom selectors.',
            'icon': 'fas fa-spider',
            'iconColor': 'text-purple-400',
            'tags': ['API', 'Automation', 'Pro'],
            'link': '#',
            'featured': True,
            'stats': {'requests': '1M+', 'uptime': '99.99%'}
        },
        {
            'id': 8,
            'name': 'Bulk Email Verifier',
            'description': 'Verify email addresses in bulk. Check deliverability, catch-all domains, and syntax validation. Perfect for marketing campaigns.',
            'icon': 'fas fa-envelope',
            'iconColor': 'text-amber-400',
            'tags': ['Email', 'Bulk', 'Marketing'],
            'link': '#',
            'featured': False,
            'stats': {'verified': '500K+', 'accuracy': '98.5%'}
        },
        {
            'id': 9,
            'name': 'QR Code Generator',
            'description': 'Generate custom QR codes with logos, colors, and tracking. Download in PNG, SVG, and EPS formats. Track scans in real-time.',
            'icon': 'fas fa-qrcode',
            'iconColor': 'text-indigo-400',
            'tags': ['QR Code', 'Tracking', 'Custom'],
            'link': '#',
            'featured': False,
            'stats': {'generated': '250K+', 'scans': '1.2M+'}
        },
        {
            'id': 10,
            'name': 'PDF Tools Suite',
            'description': 'Merge, split, compress, and convert PDFs. Extract text and images. Works with large files up to 500MB. All processing is done client-side.',
            'icon': 'fas fa-file-pdf',
            'iconColor': 'text-red-500',
            'tags': ['PDF', 'Tools', 'Free'],
            'link': '#',
            'featured': False,
            'stats': {'processed': '1M+', 'formats': '12+'}
        },
        {
            'id': 11,
            'name': 'Image Optimizer',
            'description': 'Compress images without losing quality. Supports JPEG, PNG, WebP, and AVIF. Batch processing available for up to 50 images at once.',
            'icon': 'fas fa-image',
            'iconColor': 'text-cyan-400',
            'tags': ['Image', 'Optimization', 'Batch'],
            'link': '#',
            'featured': False,
            'stats': {'optimized': '3M+', 'saved': '2.5TB'}
        },
        {
            'id': 12,
            'name': 'Cron Job Manager',
            'description': 'Schedule and manage cron jobs with ease. Monitor execution logs, get failure alerts, and track job history. Supports complex scheduling intervals.',
            'icon': 'fas fa-clock',
            'iconColor': 'text-lime-400',
            'tags': ['Automation', 'Schedule', 'Monitor'],
            'link': '#',
            'featured': True,
            'stats': {'jobs': '50K+', 'uptime': '99.95%'}
        }
    ]

    # Apply search filter
    if search:
        all_products = [
            p for p in all_products
            if search in p['name'].lower() or
               search in p['description'].lower() or
               any(search in tag.lower() for tag in p['tags'])
        ]

    if limit > 0:
        products_page = all_products[:limit]
        response = {
            'products': products_page,
            'total': len(all_products),
            'limit': limit
        }
        return JsonResponse(response)

    # Normal pagination
    start = (page - 1) * per_page
    end = start + per_page
    products_page = all_products[start:end]
    has_more = end < len(all_products)

    response = {
        'products': products_page,
        'has_more': has_more,
        'page': page,
        'total': len(all_products),
        'search': search
    }

    return JsonResponse(response)