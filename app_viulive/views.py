from django.shortcuts import render
from django.http import JsonResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.conf import settings
from app_lyxmab.year_gen import year_gen
from sys_views.pretty_printer import print_error
from sys_views.get_yt_v_id import get_live_video_id
from .models import Channel
import re


DEFAULT_LOGO = "https://lyxmab.de5.net/static/uploads/og-image.png"


def channel_json(channel):
    return {
        "id": channel.id,
        "name": channel.name,
        "group-title": channel.group_title,
        "logo": channel.logo or DEFAULT_LOGO,
    }


def url_fields(urls):
    def sort_key(field_name):
        suffix = field_name.removeprefix("url")
        suffix = suffix.removeprefix("-")
        return (0 if not suffix else int(suffix) if suffix.isdigit() else 999, field_name)

    return sorted((key for key, value in urls.items() if key.startswith("url") and value), key=sort_key)


def viulive_home(request):
    year = year_gen()
    return render(request, "viulive_home.html", {'year': year})


def watching(request, channel_id):
    channel_data = Channel.objects.filter(id=channel_id).first()
    if channel_data is None:
        return JsonResponse({
            "success": False,
            "message": "Channel not found",
            "data": None
        }, status=404)
    year = year_gen()
    
    context = {
        'year': year,
        'channel_id': channel_id,
        'channel_name': channel_data.name,
        'channel_logo': channel_data.logo or DEFAULT_LOGO,
        'channel_group': channel_data.group_title,
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
    
    filtered_channels = list(Channel.objects.filter(
        name__icontains=query
    ) | Channel.objects.filter(id__icontains=query))
    
    # Remove URLs from results
    channels_without_urls = []
    for channel in filtered_channels:
        channel_copy = channel_json(channel)
        channel_copy["url_count"] = len(url_fields(channel.urls))
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
    groups = {
        re.sub(r"\s+", " ", g).strip().lower()
        for g in Channel.objects.exclude(group_title__in=["", None]).values_list("group_title", flat=True)
        if g and g.strip()
    }
    return JsonResponse({
        "success": True,
        "message": "Groups fetched successfully",
        "data": {
            "groups": sorted(groups)
        },
    })


def get_channels(request):
    """Get channels with optional group filter"""
    group_filter = request.GET.get('group', '').strip()
    query = request.GET.get('search', '').strip()
    page = request.GET.get('page', 1)
    per_page = request.GET.get('per_page', 50)
    
    filtered_channels = Channel.objects.all()
    
    # Apply group filter
    if group_filter:
        filtered_channels = filtered_channels.filter(group_title__iexact=group_filter)
    
    # Apply search filter
    if query:
        filtered_channels = filtered_channels.filter(
            name__icontains=query
        ) | filtered_channels.filter(id__icontains=query)
    
    # Remove URLs from results and count URL fields
    channels_without_urls = []
    for channel in filtered_channels:
        channel_copy = channel_json(channel)
        channel_copy["url_count"] = len(url_fields(channel.urls))
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
    
    channel_data = Channel.objects.filter(id=channel_id).first()
    if channel_data is None:
        return JsonResponse({
            "success": False,
            "message": "Channel not found",
            "data": None
        }, status=404)
    available_urls = url_fields(channel_data.urls)
    
    stream_num = request.GET.get('stream', 1)
    
    try:
        stream_num = int(stream_num)
        if stream_num < 1 or stream_num > len(available_urls):
            return JsonResponse({
                "success": False,
                "message": f"Invalid stream. Use 1 to {len(available_urls)}",
                "data": None
            }, status=400)
        
        field = available_urls[stream_num - 1]
        url_value = channel_data.urls.get(field, '')
        
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
                    "name": channel_data.name,
                    "url": stream_url,
                    "group-title": channel_data.group_title,
                    "logo": channel_data.logo or DEFAULT_LOGO
                }
            }
        })
    except ValueError:
        return JsonResponse({
            "success": False,
            "message": f"Invalid stream parameter. Use a number between 1 and {len(available_urls)}",
            "data": None
        }, status=400)

def is_request_from_our_domain(request):

    # If Debug is True then return True
    if settings.DEBUG:
        return True
    
    referer = request.META.get('HTTP_REFERER', '')
    origin = request.META.get('HTTP_ORIGIN', '')
    
    allowed_domains = [
        'lyxmab.de5.net',
        'www.lyxmab.de5.net',
        'royole.vercel.app',
    ]
    
    if origin:
        return any(domain in origin for domain in allowed_domains)
    
    if referer:
        return any(domain in referer for domain in allowed_domains)
    
    return False