from django.http import JsonResponse
from django_ratelimit.decorators import ratelimit
from sys_views.rate_limit_key import getKey


def annotate_products(products, start_index=0):
    return [
        {**product, 'number': start_index + idx + 1}
        for idx, product in enumerate(products)
    ]


@ratelimit(key=getKey, rate='20/m', block=True)
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
            'link': 'https://v6.www-y2mate.com/',
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
            'link': '/downloader/fb/',
            'featured': False,
            'stats': {'downloads': '8K+', 'rating': '4.7'}
        },
        {
            'id': 3,
            'name': 'Instagram Downloader',
            'description': 'Save photos, videos, and reels from Instagram. No watermark, supports multiple formats. Works with public and private accounts.',
            'icon': 'fab fa-instagram',
            'iconColor': 'text-pink-400',
            'tags': ['Popular', 'No Watermark'],
            'link': '/downloader/instagram/',
            'featured': False,
            'stats': {'downloads': '9K+', 'rating': '4.8'}
        },
        {
            'id': 4,
            'name': 'Cloudinary Connect',
            'description': 'Learn how to connect, upload, download and delete data from your Cloudinary Project.',
            'icon': 'fas fa-database',
            'iconColor': 'text-teal-400',
            'tags': ['Bespoke', 'Automation', 'API'],
            'link': '#',
            'featured': True,
            'stats': {'projects': '5+', 'clients': '4+'}
        },
        {
            'id': 5,
            'name': 'Pretty Printer',
            'description': 'Print styled messages to the console with ANSI escape codes, and custom styles & colors for each message.',
            'icon': 'fas fa-print',
            'iconColor': 'text-white',
            'tags': ['Styled', 'Colors', 'Offline'],
            'link': 'pretty-printer/scr/',
            'featured': False,
            'stats': {'coloring': '100%', 'styles': 'Instant'}
        },
        {
            'id': 6,
            'name': 'Song Search',
            'description': 'Search for any song using sound recognition technology. Download the song in high quality.',
            'icon': 'fab fa-spotify',
            'iconColor': 'text-green-400',
            'tags': ['All', 'Music'],
            'link': 'song-search/',
            'featured': False,
            'stats': {'usage': '5K+'}
        },
        {
            'id': 7,
            'name': 'Web Scraper API',
            'description': 'Extract data from any website with our powerful scraping API. Get structured data in JSON format. Supports pagination, proxies, and custom selectors.',
            'icon': 'fas fa-spider',
            'iconColor': 'text-purple-400',
            'tags': ['API', 'Automation', 'Pro'],
            'link': 'web-scraper/',
            'featured': True,
            'stats': {'requests': '1M+', 'uptime': '99.99%'}
        },
        {
            'id': 8,
            'name': 'View Tv',
            'description': 'Watch TV shows, live tvs, sports and movies online with ease. No watermark, supports multiple languages. Works with all devices.',
            'icon': 'fas fa-tv',
            'iconColor': 'text-amber-400',
            'tags': ['Live', 'Sports', 'Movies'],
            'link': 'https://viewstream-1.onrender.com',
            'featured': True,
            'stats': {'verified': '5K+', 'availability': '79%'}
        },
        {
            'id': 9,
            'name': 'QR Code Generator',
            'description': 'Generate custom QR codes with logos, colors, and tracking. Download in PNG, SVG, and EPS formats. Track scans in real-time.',
            'icon': 'fas fa-qrcode',
            'iconColor': 'text-indigo-400',
            'tags': ['QR Code', 'Tracking', 'Custom'],
            'link': 'qr/',
            'featured': False,
            'stats': {'generated': '25+', 'scans': '1.2K+'}
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
            'name': 'UptimeRobot',
            'description': 'Monitor website availability and uptime of your services with ease.',
            'icon': 'fas fa-heartbeat',
            'iconColor': 'text-lime-400',
            'tags': ['Automation', 'Schedule', 'Monitor'],
            'link': 'https://uptimerobot.com/',
            'featured': True,
            'stats': {'jobs': '50K+', 'uptime': '99.99%'}
        },
        {
            'id': 13,
            'name': 'TGive e-commerce',
            'description': 'E-commerce platform for small businesses. Supports product listing, inventory management, and payment processing.',
            'icon': 'fas fa-shopping-cart',
            'iconColor': 'text-green-400',
            'tags': ['For-Sale', 'ECommerce', 'Upgrade'],
            'link': 'https://t-give-3.onrender.com/',
            'featured': False,
            'stats': {'jobs': '5K+', 'uptime': '99.95%'}
        },
        {
            'id': 14,
            'name': 'Lyma Hub',
            'description': 'Join KONAMI Tournament now! Play with friends and win prizes. Have FUN!! 😏🥳',
            'icon': 'fas fa-futbol',
            'iconColor': 'text-purple-400',
            'tags': ['For-Sale', 'KONAMI', 'Quick Games'],
            'link': 'https://lymak.vercel.app/',
            'featured': False,
            'stats': {'participants': '600+', 'uptime': '99.95%'}
        },
        {
            'id': 15,
            'name': 'Royale Tv',
            'description': 'Enjoy seemless Football streaming, No lag! Fewer ads.',
            'icon': 'fas fa-tv',
            'iconColor': 'text-teal-400',
            'tags': ['For-Sale', 'Football', 'WC'],
            'link': 'tv/',
            'featured': False,
            'stats': {'participants': '600+'}
        },
    ]

    # Apply search filter
    # Search in name, description, and tags
    # Case-insensitive search (reduce noise)
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
        'products': annotate_products(products_page, start),
        'has_more': has_more,
        'page': page,
        'total': len(all_products),
        'search': search
    }

    return JsonResponse(response)