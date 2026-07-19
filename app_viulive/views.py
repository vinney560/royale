from django.shortcuts import render
from django.http import JsonResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.conf import settings
from app_royale.year_gen import year_gen
from sys_views.pretty_printer import print_error
from sys_views.get_yt_v_id import get_live_video_id
import os, json

app_dir = os.path.dirname(os.path.abspath(__file__))
channels_file = os.path.join(app_dir, 'channels-ke.json')

def load_channels():
    try:
        with open(channels_file, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return None
    except json.JSONDecodeError:
        return None

CHANNELS_DATA = load_channels()
CHANNELS_LIST = None

if CHANNELS_DATA:
    CHANNELS_LIST = []
    for ch_id, ch_data in CHANNELS_DATA.items():
        channel = {
            "id": ch_id,
            "name": ch_data.get("name", "Viu"),
            "group-title": ch_data.get("group-title", "Viu"),
            "logo": ch_data.get("logo", "https://royale.de5.net/static/uploads/og-image.png"),
        }
        
        # Add all URL fields dynamically
        for key, value in ch_data.items():
            if key.startswith('url'):
                channel[key] = value
        
        CHANNELS_LIST.append(channel)

def viulive_home(request):
    year = year_gen()
    return render(request, "viulive_home.html", {'year': year})

def watching(request, channel_id):
    if not CHANNELS_DATA or channel_id not in CHANNELS_DATA:
        return JsonResponse({
            "success": False,
            "message": "Channel not found",
            "data": None
        }, status=404)
    
    channel_data = CHANNELS_DATA[channel_id]
    year = year_gen()
    
    context = {
        'year': year,
        'channel_id': channel_id,
        'channel_name': channel_data.get('name', 'Viu'),
        'channel_logo': channel_data.get('logo', 'https://royale.de5.net/static/uploads/og-image.png'),
        'channel_group': channel_data.get('group-title', 'Viu'),
    }
    
    return render(request, "viulive_player.html", context)

def search_channel(request):
    query = request.GET.get('q', '').strip()
    
    if not query:
        return JsonResponse({
            "success": False,
            "message": "Search query is required",
            "data": None
        }, status=400)
    
    if CHANNELS_LIST is None:
        return JsonResponse({
            "success": False,
            "message": "Channels data unavailable",
            "data": None
        }, status=503)
    
    # Search in name and id (case-insensitive)
    query_lower = query.lower()
    filtered_channels = [
        channel for channel in CHANNELS_LIST
        if query_lower in channel['name'].lower() or query_lower in channel['id'].lower()
    ]
    
    # Remove URLs from results
    channels_without_urls = []
    for channel in filtered_channels:
        channel_copy = channel.copy()
        channel_copy.pop('url', None)
        channels_without_urls.append(channel_copy)
    
    # Pagination
    page = request.GET.get('page', 1)
    per_page = request.GET.get('per_page', 20)
    
    try:
        page = int(page)
        per_page = int(per_page)
        if per_page > 100:
            per_page = 100
    except ValueError:
        page = 1
        per_page = 20
    
    paginator = Paginator(channels_without_urls, per_page)
    
    try:
        paginated_channels = paginator.page(page)
    except (PageNotAnInteger, EmptyPage):
        paginated_channels = paginator.page(1)
    
    return JsonResponse({
        "success": True,
        "message": f"Found {paginator.count} channel(s)",
        "data": {
            "channels": list(paginated_channels),
            "pagination": {
                "current_page": paginated_channels.number,
                "per_page": per_page,
                "total_channels": paginator.count,
                "total_pages": paginator.num_pages,
            },
            "query": query
        }
    })

def get_channel_groups(request):
    """Get all unique channel groups"""
    if CHANNELS_LIST is None:
        return JsonResponse({
            "success": False,
            "message": "Channels data unavailable",
            "data": None
        }, status=503)
    
    groups = set()
    for channel in CHANNELS_LIST:
        group = channel.get('group-title', 'General')
        if group:
            groups.add(group)
    
    return JsonResponse({
        "success": True,
        "message": "Groups fetched successfully",
        "data": {
            "groups": sorted(list(groups))
        }
    })

def get_channels(request):
    """Get channels with optional group filter"""
    if CHANNELS_LIST is None:
        return JsonResponse({
            "success": False,
            "message": "Channels data unavailable",
            "data": None
        }, status=503)
    
    group_filter = request.GET.get('group', '').strip()
    query = request.GET.get('search', '').strip()
    page = request.GET.get('page', 1)
    per_page = request.GET.get('per_page', 50)
    
    filtered_channels = CHANNELS_LIST.copy()
    
    # Apply group filter
    if group_filter:
        filtered_channels = [
            ch for ch in filtered_channels
            if ch.get('group-title', 'General').lower() == group_filter.lower()
        ]
    
    # Apply search filter
    if query:
        query_lower = query.lower()
        filtered_channels = [
            ch for ch in filtered_channels
            if query_lower in ch['name'].lower() or query_lower in ch['id'].lower()
        ]
    
    # Remove URLs from results and count URL fields
    channels_without_urls = []
    for channel in filtered_channels:
        channel_copy = channel.copy()
        
        # Count how many URL fields exist (url, url-2, url-3, etc.)
        url_count = 0
        for key in channel_copy.keys():
            if key.startswith('url') and channel_copy.get(key):
                url_count += 1
        
        # Remove URL fields
        url_keys = [key for key in channel_copy.keys() if key.startswith('url')]
        for key in url_keys:
            channel_copy.pop(key, None)
        
        # Add metadata
        channel_copy['url_count'] = url_count
        channels_without_urls.append(channel_copy)
    
    # Pagination
    try:
        page = int(page)
        per_page = int(per_page)
        if per_page > 100:
            per_page = 100
    except ValueError:
        page = 1
        per_page = 50
    
    paginator = Paginator(channels_without_urls, per_page)
    
    try:
        paginated_channels = paginator.page(page)
    except (PageNotAnInteger, EmptyPage):
        paginated_channels = paginator.page(1)
    
    return JsonResponse({
        "success": True,
        "message": f"Found {paginator.count} channel(s)",
        "data": {
            "channels": list(paginated_channels),
            "pagination": {
                "current_page": paginated_channels.number,
                "per_page": per_page,
                "total_channels": paginator.count,
                "total_pages": paginator.num_pages,
            },
            "filters": {
                "group": group_filter,
                "search": query
            }
        }
    })

def process_url_field(url_value):
    """Process a URL field, replacing channel_id= with live video ID"""
    if not url_value or "channel_id=" not in url_value:
        return url_value
    
    # Extract channel ID
    channel_id_from_url = url_value.split("channel_id=")[1].split("&")[0].strip()
    try:
        # Fetch live video ID
        live_video_id = get_live_video_id(channel_id_from_url)
        return live_video_id if live_video_id else f"https://www.youtube.com/embed/live_stream?channel={channel_id_from_url}"
    except Exception as e:
        print_error(f"[ERROR] Processing URL: {str(e)}")
        return f"https://www.youtube.com/embed/live_stream?channel={channel_id_from_url}"

def get_channel_url(request, channel_id):
    if not is_request_from_our_domain(request):
        print_error(f"[SECURITY] Unauthorized access attempt: {channel_id}")
        return JsonResponse({
            "success": False,
            "message": "Unauthorized access",
            "data": None
        }, status=403)
    
    if not CHANNELS_DATA or channel_id not in CHANNELS_DATA:
        return JsonResponse({
            "success": False,
            "message": "Channel not found",
            "data": None
        }, status=404)
    
    channel_data = CHANNELS_DATA[channel_id]
    
    url_fields = []
    for key in channel_data.keys():
        if key.startswith('url'):
            url_fields.append(key)
    url_fields.sort()
    
    stream_num = request.GET.get('stream', 1)
    
    try:
        stream_num = int(stream_num)
        if stream_num < 1 or stream_num > len(url_fields):
            return JsonResponse({
                "success": False,
                "message": f"Invalid stream. Use 1 to {len(url_fields)}",
                "data": None
            }, status=400)
        
        field = url_fields[stream_num - 1]
        url_value = channel_data.get(field, '')
        
        if url_value and "channel_id=" in url_value:
            channel_id_from_url = url_value.split("channel_id=")[1].split("&")[0].strip()
            live_video_id = get_live_video_id(channel_id_from_url)
            stream_url = live_video_id if live_video_id else url_value
        else:
            stream_url = url_value
        
        return JsonResponse({
            "success": True,
            "message": "Channel URL fetched successfully",
            "data": {
                "channel": {
                    "id": channel_id,
                    "name": channel_data.get("name", "Viu"),
                    "url": stream_url,
                    "group-title": channel_data.get("group-title", "Viu"),
                    "logo": channel_data.get("logo", "https://royale.de5.net/static/uploads/og-image.png")
                }
            }
        })
    except ValueError:
        return JsonResponse({
            "success": False,
            "message": f"Invalid stream parameter. Use a number between 1 and {len(url_fields)}",
            "data": None
        }, status=400)

def is_request_from_our_domain(request):

    # If Debug is True then return True
    if settings.DEBUG:
        return True
    
    referer = request.META.get('HTTP_REFERER', '')
    origin = request.META.get('HTTP_ORIGIN', '')
    
    allowed_domains = [
        'royale.de5.net',
        'www.royale.de5.net',
        'royole.vercel.app',
    ]
    
    if origin:
        return any(domain in origin for domain in allowed_domains)
    
    if referer:
        return any(domain in referer for domain in allowed_domains)
    
    return False