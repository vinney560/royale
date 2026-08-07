# views.py - Hybrid Facebook Video Downloader
from django.shortcuts import render
from django.http import JsonResponse, StreamingHttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from sys_views.pretty_printer import print_error
import requests, re, json, time, threading, random
from urllib.parse import unquote
from datetime import datetime
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

# ============================================================
# USER AGENTS & HEADERS
# ============================================================

ua = UserAgent()

def get_headers():
    """Generate random headers for requests"""
    return {
        'User-Agent': ua.random,
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Cache-Control': 'max-age=0',
    }

MOBILE_USER_AGENTS = [
    'Mozilla/5.0 (iPhone; CPU iPhone OS 17_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1',
    'Mozilla/5.0 (Linux; Android 14; Pixel 8) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.6099.230 Mobile Safari/537.36',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 17_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Mobile/15E148 Safari/604.1',
    'Mozilla/5.0 (Linux; Android 14; SM-S918B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.6099.230 Mobile Safari/537.36',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1',
    'Mozilla/5.0 (Linux; Android 13; OnePlus 11) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.6045.163 Mobile Safari/537.36',
]

MOBILE_HEADERS = {
    'User-Agent': random.choice(MOBILE_USER_AGENTS),
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Accept-Language': 'en-US,en;q=0.9',
    'DNT': '1',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'none',
    'Sec-Fetch-User': '?1',
    'Cache-Control': 'max-age=0',
    'sec-ch-ua': '"Not_A Brand";v="99", "Safari";v="17.1", "Mobile";v="17.1"',
    'sec-ch-ua-mobile': '?1',
}

# ============================================================
# HYBRID VIDEO DOWNLOADER
# ============================================================

class FacebookDownloader:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(get_headers())
        self.session.cookies.update({
            'locale': 'en_US',
            'sb': 'random_string',
            'datr': 'random_string',
            'c_user': '1000',
            'xs': 'random_string',
        })
        self.cache = {}
        self.cache_timeout = 300
        self.lock = threading.Lock()
    
    # ============================================================
    # ORIGINAL EXTRACTION - Gets FULL metadata
    # ============================================================
    
    def extract_metadata_from_original(self, url):
        """Extract full metadata (title, description, views, etc.) from Facebook page"""
        try:
            actual_url, html_content = self._fetch_page(url)
            if not html_content:
                return None
            
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Skip if login page
            page_title = soup.title.string if soup.title else ""
            if 'login' in page_title.lower() or 'log in' in page_title.lower():
                return None
            
            return {
                'title': self._extract_title(soup, html_content),
                'description': self._extract_description(soup, html_content),
                'duration': self._extract_duration(html_content),
                'views': self._extract_views(html_content),
                'upload_date': self._extract_upload_date(html_content),
                'uploader': self._extract_uploader(html_content),
                'uploader_url': self._extract_uploader_url(html_content),
                'thumbnail_url': self._extract_thumbnail(soup, html_content),
            }
        except Exception as e:
            print_error(f"Original metadata extraction failed: {e}")
            return None
    
    # ============================================================
    # RAPIDAPI EXTRACTION - Gets WORKING video URLs
    # ============================================================
    
    def extract_video_urls_from_rapidapi(self, url):
        """Get working video URLs with valid hashes from RapidAPI"""
        try:
            rapidapi_url = "https://free-facebook-downloader.p.rapidapi.com/external-api/facebook-video-downloader"
            
            response = requests.post(
                rapidapi_url,
                json={},
                headers={
                    "x-rapidapi-key": "4406e83311msh635cb32b3525e4bp17f9c1jsn874626c65441",
                    "x-rapidapi-host": "free-facebook-downloader.p.rapidapi.com",
                    "Content-Type": "application/json"
                },
                params={"url": url},
                timeout=30
            )
            
            if response.status_code != 200:
                return None
            
            result = response.json()
            if not result.get('success'):
                return None
            
            links = result.get('links', {})
            video_urls = []
            quality_options = []
            
            for link_key, video_url in links.items():
                if video_url and 'http' in video_url:
                    # Determine quality from link label
                    quality = "SD"
                    label = "Standard Quality"
                    if any(x in link_key.lower() for x in ['high', 'hd', '1080', '720']):
                        quality = "HD"
                        label = "High Quality"
                    elif any(x in link_key.lower() for x in ['low', 'sd', '360']):
                        quality = "SD"
                        label = "Standard Quality"
                    elif 'medium' in link_key.lower():
                        quality = "MD"
                        label = "Medium Quality"
                    
                    video_urls.append(video_url)
                    quality_options.append({
                        'url': video_url,
                        'quality': quality,
                        'label': label,
                        'index': len(quality_options)
                    })
            
            if video_urls:
                return {
                    'video_urls': video_urls,
                    'quality_options': quality_options,
                    'video_id': result.get('id', ''),
                    'title': result.get('title', 'Facebook Video')
                }
            return None
            
        except Exception as e:
            print_error(f"RapidAPI extraction failed: {e}")
            return None
    
    # ============================================================
    # HYBRID COMBINER
    # ============================================================
    
    def extract_metadata(self, url):
        """Combine original metadata + RapidAPI video URLs"""
        cache_key = f"metadata_{hash(url)}"
        current_time = time.time()
        
        # Check cache
        with self.lock:
            if cache_key in self.cache:
                cached_data, timestamp = self.cache[cache_key]
                if current_time - timestamp < self.cache_timeout:
                    return cached_data
        
        try:
            # Get metadata from original method
            original_metadata = self.extract_metadata_from_original(url)
            
            # Get working URLs from RapidAPI
            rapidapi_data = self.extract_video_urls_from_rapidapi(url)
            
            if not original_metadata and not rapidapi_data:
                return {'error': 'Could not extract video. The video might be private.'}
            
            # Build combined metadata
            metadata = {
                'success': True,
                'url': url,
                'title': 'Facebook Video',
                'description': 'No description available',
                'duration': '00:00',
                'views': 'Unknown',
                'upload_date': datetime.now().strftime('%Y-%m-%d'),
                'uploader': 'Unknown Uploader',
                'uploader_url': '',
                'thumbnail_url': '',
                'video_urls': [],
                'quality_options': [],
                'formats': ['MP4'],
                'extracted_at': datetime.now().isoformat(),
                'method': 'hybrid'
            }
            
            # Merge original metadata
            if original_metadata:
                for key, value in original_metadata.items():
                    if value:
                        metadata[key] = value
            
            # Merge RapidAPI URLs
            if rapidapi_data:
                metadata['video_urls'] = rapidapi_data.get('video_urls', [])
                metadata['quality_options'] = rapidapi_data.get('quality_options', [])
                metadata['video_id'] = rapidapi_data.get('video_id', '')
                if metadata['title'] == 'Facebook Video' and rapidapi_data.get('title'):
                    metadata['title'] = rapidapi_data.get('title', 'Facebook Video')
            
            # Cache and return
            with self.lock:
                self.cache[cache_key] = (metadata, current_time)
            
            return metadata
            
        except Exception as e:
            print_error(f"Hybrid extraction error: {e}")
            return {'error': 'Failed to extract metadata. Please try again later.'}
    
    # ============================================================
    # HELPER EXTRACTION METHODS
    # ============================================================
    
    def _fetch_page(self, url):
        """Fetch Facebook page with proper headers"""
        try:
            headers = get_headers()
            response = requests.get(url, headers=headers, timeout=10, allow_redirects=True)
            
            # If login required, try mobile version
            if 'login' in response.url or 'facebook.com/login' in response.url:
                mobile_headers = MOBILE_HEADERS.copy()
                response = requests.get(url, headers=mobile_headers, timeout=10, allow_redirects=True)
            
            return response.url, response.text
        except Exception as e:
            print_error(f"Error fetching page: {e}")
            return url, ""
    
    def _extract_title(self, soup, html_content):
        """Extract video title from page"""
        og_title = soup.find('meta', property='og:title')
        if og_title and og_title.get('content'):
            return og_title.get('content')
        
        meta_title = soup.find('meta', {'name': 'title'})
        if meta_title and meta_title.get('content'):
            return meta_title.get('content')
        
        if soup.title:
            title = soup.title.string
            if title and 'facebook' not in title.lower():
                return title
        
        title_match = re.search(r'"videoTitle":"([^"]+)"', html_content)
        if title_match:
            return title_match.group(1).replace('\\', '')
        
        return 'Facebook Video'
    
    def _extract_description(self, soup, html_content):
        """Extract video description"""
        og_desc = soup.find('meta', property='og:description')
        if og_desc and og_desc.get('content'):
            return og_desc.get('content')
        
        meta_desc = soup.find('meta', {'name': 'description'})
        if meta_desc and meta_desc.get('content'):
            return meta_desc.get('content')
        
        desc_match = re.search(r'"snippet":"([^"]+)"', html_content)
        if desc_match:
            return desc_match.group(1).replace('\\', '')
        
        return 'No description available'
    
    def _extract_duration(self, html_content):
        """Extract video duration"""
        patterns = [
            r'"duration_ms":(\d+)',
            r'"video_duration":(\d+)',
            r'"length":(\d+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, html_content)
            if match:
                try:
                    ms = int(match.group(1))
                    minutes = ms // 60000
                    seconds = (ms % 60000) // 1000
                    return f"{minutes:02d}:{seconds:02d}"
                except:
                    pass
        return "00:00"
    
    def _extract_views(self, html_content):
        """Extract view count"""
        patterns = [
            r'"video_view_count":(\d+)',
            r'"viewCount":(\d+)',
            r'"views":(\d+)',
            r'"interactionCount":(\d+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, html_content)
            if match:
                try:
                    views = int(match.group(1))
                    if views >= 1000000:
                        return f"{views/1000000:.1f}M"
                    elif views >= 1000:
                        return f"{views/1000:.1f}K"
                    else:
                        return str(views)
                except:
                    pass
        return "Unknown"
    
    def _extract_upload_date(self, html_content):
        """Extract upload date"""
        patterns = [
            r'"uploadDate":"([^"]+)"',
            r'"datePublished":"([^"]+)"',
            r'"dateCreated":"([^"]+)"',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, html_content)
            if match:
                try:
                    date_str = match.group(1)
                    if 'T' in date_str:
                        return date_str.split('T')[0]
                    return date_str
                except:
                    pass
        return datetime.now().strftime('%Y-%m-%d')
    
    def _extract_uploader(self, html_content):
        """Extract uploader name"""
        patterns = [
            r'"ownerName":"([^"]+)"',
            r'"authorName":"([^"]+)"',
            r'"uploader":"([^"]+)"',
            r'"actor":"([^"]+)"',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, html_content)
            if match:
                name = match.group(1).replace('\\', '')
                if name and name != 'null':
                    return name
        return "Unknown Uploader"
    
    def _extract_uploader_url(self, html_content):
        """Extract uploader profile URL"""
        patterns = [
            r'"ownerProfileURL":"([^"]+)"',
            r'"authorUrl":"([^"]+)"',
            r'"actorUrl":"([^"]+)"',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, html_content)
            if match:
                url = match.group(1).replace('\\', '')
                if url and url != 'null' and 'http' in url:
                    return url
        return ""
    
    def _extract_thumbnail(self, soup, html_content):
        """Extract thumbnail URL"""
        og_image = soup.find('meta', property='og:image')
        if og_image and og_image.get('content'):
            return og_image.get('content')
        
        thumb_patterns = [
            r'"thumbnailUrl":"([^"]+)"',
            r'"thumbnail":"([^"]+)"',
            r'"poster":"([^"]+)"',
            r'"image":"([^"]+)"',
        ]
        
        for pattern in thumb_patterns:
            match = re.search(pattern, html_content)
            if match:
                thumb_url = match.group(1).replace('\\', '')
                if thumb_url and 'http' in thumb_url:
                    return thumb_url
        return ""
    
    def generate_filename(self, metadata):
        """Generate safe filename from metadata"""
        title = metadata.get('title', 'facebook_video')
        title_clean = re.sub(r'[^\w\s-]', '', title)
        title_clean = re.sub(r'\s+', '_', title_clean)
        title_clean = title_clean[:30] if title_clean else 'facebook_video'
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        return f"fb_{title_clean}_{timestamp}.mp4"

# Initialize downloader
downloader = FacebookDownloader()

# ============================================================
# VIEWS
# ============================================================

@csrf_exempt
def facebook_v_downloader(request):
    """Render the downloader page"""
    return render(request, 'fb_vid_downloader.html')

@csrf_exempt
@require_http_methods(["POST"])
def extract_metadata(request):
    """Extract video metadata and working URLs"""
    try:
        # Get URL from request
        if request.content_type and 'application/json' in request.content_type:
            data = json.loads(request.body)
            url = data.get('url', '').strip()
        else:
            url = request.POST.get('url', '').strip()
        
        if not url:
            return JsonResponse({
                'success': False,
                'error': 'URL is required'
            }, status=400)
        
        url = unquote(url)
        
        # Extract metadata
        metadata = downloader.extract_metadata(url)
        
        if 'error' in metadata:
            return JsonResponse({
                'success': False,
                'error': metadata['error']
            }, status=400)
        
        metadata['success'] = True
        return JsonResponse(metadata)
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON data'
        }, status=400)
    except Exception as e:
        print_error(f"Extract metadata error: {e}")
        return JsonResponse({
            'success': False,
            'error': "Failed to extract metadata. Please try again later."
        }, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def direct_download(request):
    """Stream video for download"""
    try:
        # Get URL from request
        if request.content_type and 'application/json' in request.content_type:
            data = json.loads(request.body)
            url = data.get('url', '').strip()
            quality_index = int(data.get('quality_index', 0))
        else:
            url = request.POST.get('url', '').strip()
            quality_index = int(request.POST.get('quality_index', 0))
        
        if not url:
            return JsonResponse({
                'success': False,
                'error': 'URL is required'
            }, status=400)
        
        url = unquote(url)
        
        # Get metadata and video URL
        metadata = downloader.extract_metadata(url)
        
        if 'error' in metadata:
            return JsonResponse({
                'success': False,
                'error': metadata['error']
            }, status=400)
        
        if not metadata.get('video_urls'):
            return JsonResponse({
                'success': False,
                'error': 'No video URLs found'
            }, status=400)
        
        if quality_index >= len(metadata['video_urls']):
            quality_index = 0
        
        video_url = metadata['video_urls'][quality_index]
        filename = downloader.generate_filename(metadata)
        
        # Stream video to browser
        mobile_headers = MOBILE_HEADERS.copy()
        video_response = requests.get(video_url, headers=mobile_headers.copy(), stream=True, timeout=60)
        video_response.raise_for_status()
        
        content_type = video_response.headers.get('Content-Type', 'video/mp4')
        content_length = video_response.headers.get('Content-Length', '')
        
        def generate():
            for chunk in video_response.iter_content(chunk_size=8192):
                if chunk:
                    yield chunk
        
        response = StreamingHttpResponse(generate(), content_type=content_type)
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        if content_length:
            response['Content-Length'] = content_length
        response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response['Pragma'] = 'no-cache'
        response['Expires'] = '0'
        
        return response
        
    except requests.exceptions.RequestException as e:
        print_error(f"Network error during download: {e}")
        return JsonResponse({
            'success': False,
            'error': "Poor internet connection. Check your internet connection and try again."
        }, status=500)
    except Exception as e:
        print_error(f"Download error: {e}")
        return JsonResponse({
            'success': False,
            'error': "Failed to download video. Please try again later."
        }, status=500)

def test_endpoint(request):
    """Test endpoint to verify service is running"""
    return JsonResponse({
        'status': 'online',
        'service': 'Facebook Video Downloader (Hybrid)',
        'timestamp': datetime.now().isoformat()
    })