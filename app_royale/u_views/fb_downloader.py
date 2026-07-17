# views.py
from django.shortcuts import render
from django.http import JsonResponse, StreamingHttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import requests
import re
import json
import time
import threading
from urllib.parse import urlparse, unquote
from datetime import datetime
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

# ============================================================
# FACEBOOK-SCRAPER IMPORTS
# ============================================================

try:
    from facebook_scraper import get_post, set_cookies, set_user_agent, get_page_info
    FACEBOOK_SCRAPER_AVAILABLE = True
    print("[FacebookDownloader] facebook-scraper loaded successfully")
except ImportError as e:
    print(f"[FacebookDownloader] facebook-scraper not available: {e}")
    FACEBOOK_SCRAPER_AVAILABLE = False

# ============================================================
# FAKE USER-AGENT
# ============================================================

ua = UserAgent()

def get_headers():
    """Get random headers with fake user-agent"""
    headers = {
        'User-Agent': ua.random,
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Cache-Control': 'max-age=0',
    }
    return headers

# ============================================================
# FACEBOOK VIDEO DOWNLOADER
# ============================================================

class FacebookVideoDownloader:
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
        
        # Configure facebook-scraper
        if FACEBOOK_SCRAPER_AVAILABLE:
            try:
                # Set custom user-agent for facebook-scraper
                set_user_agent(ua.random)
                
                # Set cookies
                set_cookies({
                    'locale': 'en_US',
                    'sb': 'random_string',
                    'datr': 'random_string',
                    'c_user': '1000',
                    'xs': 'random_string',
                })
                print("[FacebookDownloader] facebook-scraper configured")
            except Exception as e:
                print(f"[FacebookDownloader] Error configuring facebook-scraper: {e}")
    
    def is_valid_facebook_url(self, url):
        try:
            parsed = urlparse(url)
            if not parsed.netloc.endswith('facebook.com') and 'fb.watch' not in parsed.netloc:
                return False
            return True
        except:
            return False
    
    def extract_video_id(self, url):
        """Extract video ID from Facebook URL"""
        # Pattern for watch URLs: /watch?v=123456789
        watch_match = re.search(r'[?&]v=(\d+)', url)
        if watch_match:
            return watch_match.group(1)
        
        # Pattern for reel URLs: /reel/123456789
        reel_match = re.search(r'/reel/(\d+)', url)
        if reel_match:
            return reel_match.group(1)
        
        # Pattern for share URLs: /share/v/123456789
        share_match = re.search(r'/share/v/(\d+)', url)
        if share_match:
            return share_match.group(1)
        
        # Pattern for post URLs: /posts/123456789
        post_match = re.search(r'/posts/(\d+)', url)
        if post_match:
            return post_match.group(1)
        
        # Pattern for fb.watch URLs
        if 'fb.watch' in url:
            try:
                headers = get_headers()
                response = requests.head(url, headers=headers, timeout=5, allow_redirects=True)
                return self.extract_video_id(response.url)
            except:
                pass
        
        # Try to extract any number from URL
        number_match = re.search(r'(\d{10,})', url)
        if number_match:
            return number_match.group(1)
        
        return None
    
    def extract_metadata(self, url):
        cache_key = f"metadata_{hash(url)}"
        current_time = time.time()
        
        with self.lock:
            if cache_key in self.cache:
                cached_data, timestamp = self.cache[cache_key]
                if current_time - timestamp < self.cache_timeout:
                    return cached_data
        
        try:
            print(f"Processing URL: {url}")
            
            # ============================================================
            # TRY FACEBOOK-SCRAPER FIRST
            # ============================================================
            
            if FACEBOOK_SCRAPER_AVAILABLE:
                try:
                    # Try with get_page_info first
                    try:
                        page_info = get_page_info(url)
                        if page_info:
                            print(f"[facebook-scraper] get_page_info succeeded")
                            metadata = self._parse_page_info(page_info, url)
                            with self.lock:
                                self.cache[cache_key] = (metadata, current_time)
                            return metadata
                    except Exception as e:
                        print(f"[facebook-scraper] get_page_info failed: {e}")
                    
                    # Extract video ID and try get_post
                    video_id = self.extract_video_id(url)
                    if video_id:
                        try:
                            post = get_post(video_id, options={"comments": False})
                            if post and post.get('video'):
                                print(f"[facebook-scraper] get_post succeeded for ID: {video_id}")
                                metadata = self._parse_post_data(post, url)
                                with self.lock:
                                    self.cache[cache_key] = (metadata, current_time)
                                return metadata
                        except Exception as e:
                            print(f"[facebook-scraper] get_post failed: {e}")
                            
                except Exception as e:
                    print(f"[facebook-scraper] Error: {e}")
            
            # ============================================================
            # FALLBACK: MANUAL EXTRACTION
            # ============================================================
            
            print("Trying manual extraction...")
            actual_url, html_content = self.get_actual_video_url(url)
            
            if not html_content:
                return {'error': 'Could not fetch video page. The video might be private or require login.'}
            
            soup = BeautifulSoup(html_content, 'html.parser')
            
            page_title = soup.title.string if soup.title else ""
            print(f"Page title: {page_title}")
            
            if 'login' in page_title.lower() or 'log in' in page_title.lower():
                return {'error': 'Facebook is requiring login. Try using a different video or check if the video is public.'}
            
            metadata = self.extract_metadata_from_html(soup, actual_url, html_content)
            
            if not metadata.get('video_urls'):
                print("No video URLs found in primary extraction, trying alternatives...")
                alternative_urls = self.extract_video_urls_alternative(html_content)
                if alternative_urls:
                    metadata['video_urls'] = alternative_urls
                    metadata['quality_options'] = self.generate_quality_options(alternative_urls)
            
            with self.lock:
                self.cache[cache_key] = (metadata, current_time)
            
            print(f"Extraction completed: {len(metadata.get('video_urls', []))} video URLs found")
            return metadata
            
        except requests.exceptions.RequestException as e:
            return {'error': f'Network error: {str(e)}'}
        except Exception as e:
            return {'error': f'Error extracting metadata: {str(e)}'}
    
    def _parse_page_info(self, page_info, url):
        """Parse page info from facebook-scraper"""
        metadata = {
            'success': True,
            'url': url,
            'title': page_info.get('title', 'Facebook Video'),
            'description': page_info.get('description', ''),
            'duration': self._format_duration(page_info.get('duration', 0)),
            'views': self._format_views(page_info.get('views', 0)),
            'upload_date': page_info.get('upload_date', ''),
            'uploader': page_info.get('author', 'Unknown Uploader'),
            'uploader_url': page_info.get('author_url', ''),
            'thumbnail_url': page_info.get('thumbnail', ''),
            'video_urls': [],
            'quality_options': [],
            'formats': ['MP4'],
            'extracted_at': datetime.now().isoformat(),
            'message': 'Metadata extracted successfully (facebook-scraper)'
        }
        
        # Extract video source
        source = page_info.get('source', {})
        if isinstance(source, dict):
            for quality, video_url in source.items():
                if video_url and 'http' in video_url:
                    metadata['video_urls'].append(video_url)
        elif isinstance(source, str) and 'http' in source:
            metadata['video_urls'].append(source)
        
        # Also check for individual quality URLs
        for key in ['sd_src', 'hd_src', 'src']:
            if key in page_info and page_info[key]:
                metadata['video_urls'].append(page_info[key])
        
        if metadata['video_urls']:
            metadata['quality_options'] = self.generate_quality_options(metadata['video_urls'])
        
        return metadata
    
    def _parse_post_data(self, post, url):
        """Parse post data from facebook-scraper get_post"""
        metadata = {
            'success': True,
            'url': url,
            'title': post.get('text', 'Facebook Video')[:100],
            'description': post.get('text', ''),
            'duration': self._format_duration(post.get('duration', 0)),
            'views': self._format_views(post.get('views', 0)),
            'upload_date': post.get('time', ''),
            'uploader': post.get('username', 'Unknown Uploader'),
            'uploader_url': post.get('profile_url', ''),
            'thumbnail_url': post.get('image', ''),
            'video_urls': [],
            'quality_options': [],
            'formats': ['MP4'],
            'extracted_at': datetime.now().isoformat(),
            'message': 'Metadata extracted successfully (facebook-scraper)'
        }
        
        # Extract video URL from post
        video = post.get('video', {})
        if isinstance(video, dict):
            for key in ['source', 'sd_src', 'hd_src', 'src']:
                if key in video and video[key]:
                    metadata['video_urls'].append(video[key])
        
        if isinstance(video, str) and 'http' in video:
            metadata['video_urls'].append(video)
        
        # Try other video sources
        for key in ['video_url', 'video_source', 'source']:
            if key in post and post[key]:
                metadata['video_urls'].append(post[key])
        
        if metadata['video_urls']:
            metadata['quality_options'] = self.generate_quality_options(metadata['video_urls'])
        
        return metadata
    
    def _format_duration(self, seconds):
        """Format duration from seconds to MM:SS"""
        try:
            seconds = int(seconds)
            minutes = seconds // 60
            secs = seconds % 60
            return f"{minutes:02d}:{secs:02d}"
        except:
            return "00:00"
    
    def _format_views(self, views):
        """Format views count"""
        try:
            views = int(views)
            if views >= 1000000:
                return f"{views/1000000:.1f}M"
            elif views >= 1000:
                return f"{views/1000:.1f}K"
            else:
                return str(views)
        except:
            return "Unknown"
    
    def get_actual_video_url(self, url):
        try:
            headers = get_headers()
            response = requests.get(url, headers=headers, timeout=10, allow_redirects=True)
            final_url = response.url
            
            if 'login' in final_url or 'facebook.com/login' in final_url:
                mobile_headers = get_headers()
                mobile_headers['User-Agent'] = 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_1_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Mobile/15E148 Safari/604.1'
                response = requests.get(url, headers=mobile_headers, timeout=10, allow_redirects=True)
                final_url = response.url
            
            return final_url, response.text
            
        except Exception as e:
            print(f"Error getting actual URL: {e}")
            return url, ""
    
    def extract_metadata_from_html(self, soup, url, html_content):
        metadata = {
            'success': True,
            'url': url,
            'title': self.extract_title(soup, html_content),
            'description': self.extract_description(soup, html_content),
            'duration': self.extract_duration(html_content),
            'views': self.extract_views(html_content),
            'upload_date': self.extract_upload_date(html_content),
            'uploader': self.extract_uploader(html_content),
            'uploader_url': self.extract_uploader_url(html_content),
            'thumbnail_url': self.extract_thumbnail(soup, html_content),
            'video_urls': self.extract_video_urls(html_content),
            'quality_options': [],
            'formats': ['MP4'],
            'extracted_at': datetime.now().isoformat(),
            'message': 'Metadata extracted successfully (manual)'
        }
        
        if metadata['video_urls']:
            metadata['quality_options'] = self.generate_quality_options(metadata['video_urls'])
        
        return metadata
    
    def extract_title(self, soup, html_content):
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
    
    def extract_description(self, soup, html_content):
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
    
    def extract_duration(self, html_content):
        patterns = [
            r'"playableDurationInMs":(\d+)',
            r'"duration":(\d+)',
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
    
    def extract_views(self, html_content):
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
    
    def extract_upload_date(self, html_content):
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
    
    def extract_uploader(self, html_content):
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
    
    def extract_uploader_url(self, html_content):
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
    
    def extract_thumbnail(self, soup, html_content):
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
    
    def extract_video_urls(self, html_content):
        video_urls = []
        
        patterns = [
            r'"browser_native_hd_url":"([^"]+)"',
            r'"browser_native_sd_url":"([^"]+)"',
            r'"playable_url_quality_hd":"([^"]+)"',
            r'"playable_url_quality_sd":"([^"]+)"',
            r'"hd_src":"([^"]+)"',
            r'"sd_src":"([^"]+)"',
            r'"playable_url":"([^"]+)"',
            r'"src":"([^"]+)"',
            r'"video_url":"([^"]+)"',
            r'"contentUrl":"([^"]+)"',
            r'"url":"([^"]+)"',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, html_content)
            for match in matches:
                video_url = match.replace('\\/', '/')
                video_url = unquote(video_url)
                
                if any(ext in video_url.lower() for ext in ['.mp4', '.mov', '.avi', '.webm', 'video']):
                    if any(domain in video_url.lower() for domain in ['facebook.com', 'fbcdn.net', 'cdn.fbsbx.com', 'video.xx.fbcdn.net']):
                        if video_url not in video_urls:
                            video_urls.append(video_url)
        
        url_pattern = r'(https?://[^\s"<>]*?(?:\.mp4|\.mov|\.avi|\.webm|/video/[^\s"<>]*))'
        matches = re.findall(url_pattern, html_content, re.IGNORECASE)
        for match in matches:
            clean_url = match.replace('\\/', '/')
            clean_url = unquote(clean_url)
            
            if any(domain in clean_url for domain in ['facebook.com', 'fbcdn.net', 'cdn.fbsbx.com', 'video.xx.fbcdn.net']):
                if clean_url not in video_urls:
                    video_urls.append(clean_url)
        
        return list(dict.fromkeys(video_urls))
    
    def extract_video_urls_alternative(self, html_content):
        video_urls = []
        
        url_pattern = r'(https?://[^\s"<>]*?(?:\.mp4|\.mov|\.avi|\.webm|/video/[^\s"<>]*))'
        matches = re.findall(url_pattern, html_content, re.IGNORECASE)
        
        for url in matches:
            clean_url = url.replace('\\/', '/')
            clean_url = unquote(clean_url)
            
            if any(domain in clean_url for domain in ['facebook.com', 'fbcdn.net', 'cdn.fbsbx.com', 'video.xx.fbcdn.net']):
                if clean_url not in video_urls:
                    video_urls.append(clean_url)
        
        return list(set(video_urls))
    
    def generate_quality_options(self, video_urls):
        qualities = []
        
        for i, url in enumerate(video_urls):
            quality = 'SD'
            label = 'Standard Quality'
            
            if 'hd' in url.lower() or '720' in url or '1080' in url:
                quality = 'HD'
                label = 'High Definition'
            elif '360' in url:
                quality = '360p'
                label = '360p Quality'
            elif '480' in url:
                quality = '480p'
                label = '480p Quality'
            elif '720' in url:
                quality = '720p'
                label = '720p HD'
            elif '1080' in url:
                quality = '1080p'
                label = '1080p Full HD'
            
            qualities.append({
                'url': url,
                'quality': quality,
                'label': label,
                'index': i
            })
        
        quality_order = {'1080p': 0, '720p': 1, 'HD': 2, '480p': 3, '360p': 4, 'SD': 5}
        qualities.sort(key=lambda x: quality_order.get(x['quality'], 6))
        
        return qualities
    
    def download_video(self, url, quality_index=0):
        try:
            metadata = self.extract_metadata(url)
            
            if 'error' in metadata:
                return {'error': metadata['error']}
            
            if not metadata.get('video_urls'):
                return {'error': 'No video URLs found. The video might be private or restricted.'}
            
            if quality_index >= len(metadata['video_urls']):
                quality_index = 0
            
            video_url = metadata['video_urls'][quality_index]
            filename = self.generate_filename(metadata)
            
            headers = get_headers()
            headers['Range'] = 'bytes=0-1'
            try:
                head_response = requests.head(video_url, headers=headers, timeout=10)
                if head_response.status_code == 200 or head_response.status_code == 206:
                    content_length = head_response.headers.get('content-length', '0')
                    size_mb = int(content_length) / (1024 * 1024) if content_length.isdigit() else 0
                else:
                    test_response = requests.get(video_url, headers=headers, stream=True, timeout=10)
                    content_length = test_response.headers.get('content-length', '0')
                    size_mb = int(content_length) / (1024 * 1024) if content_length.isdigit() else 0
            except:
                size_mb = 0
            
            return {
                'success': True,
                'video_url': video_url,
                'filename': filename,
                'size_mb': round(size_mb, 2),
                'metadata': metadata,
                'message': f'Video ready to download ({size_mb:.2f} MB)'
            }
            
        except requests.exceptions.RequestException as e:
            return {'error': f'Network error: {str(e)}'}
        except Exception as e:
            return {'error': f'Failed to prepare video: {str(e)}'}
    
    def generate_filename(self, metadata):
        title = metadata.get('title', 'facebook_video')
        
        title_clean = re.sub(r'[^\w\s-]', '', title)
        title_clean = re.sub(r'\s+', '_', title_clean)
        title_clean = title_clean[:30]
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        return f"fb_{title_clean}_{timestamp}.mp4"

# ============================================================
# INITIALIZE DOWNLOADER
# ============================================================

downloader = FacebookVideoDownloader()

# ============================================================
# VIEWS
# ============================================================

@csrf_exempt
def facebook_v_downloader(request):
    return render(request, 'fb_vid_downloader.html')

@csrf_exempt
@require_http_methods(["POST"])
def extract_metadata(request):
    try:
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
        
        try:
            url = unquote(url)
        except:
            pass
        
        print(f"\n=== EXTRACTING METADATA ===")
        print(f"Input URL: {url}")
        
        metadata = downloader.extract_metadata(url)
        
        if 'error' in metadata:
            print(f"ERROR: {metadata['error']}")
            return JsonResponse({
                'success': False,
                'error': metadata['error'],
                'message': metadata['error']
            }, status=400)
        
        print(f"SUCCESS: Title='{metadata.get('title', 'N/A')}'")
        print(f"Video URLs found: {len(metadata.get('video_urls', []))}")
        for i, video_url in enumerate(metadata.get('video_urls', [])[:3]):
            print(f"  URL {i+1}: {video_url[:100]}...")
        print("=== EXTRACTION COMPLETE ===\n")
        
        metadata['success'] = True
        return JsonResponse(metadata, json_dumps_params={'ensure_ascii': False})
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON data'
        }, status=400)
    except Exception as e:
        print(f"Unexpected error in extract_metadata: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e),
            'message': f'Unexpected error: {str(e)}'
        }, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def direct_download(request):
    try:
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
        
        try:
            url = unquote(url)
        except:
            pass
        
        print(f"Downloading video: {url[:100]}..., quality index: {quality_index}")
        
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
        
        print(f"Streaming video from: {video_url[:100]}...")
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': 'https://www.facebook.com/',
            'Origin': 'https://www.facebook.com',
        }
        
        video_response = requests.get(video_url, headers=headers, stream=True, timeout=60)
        video_response.raise_for_status()
        
        content_type = video_response.headers.get('Content-Type', 'video/mp4')
        content_length = video_response.headers.get('Content-Length', '')
        
        def generate():
            for chunk in video_response.iter_content(chunk_size=8192):
                if chunk:
                    yield chunk
        
        response = StreamingHttpResponse(
            generate(),
            content_type=content_type
        )
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        if content_length:
            response['Content-Length'] = content_length
        response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response['Pragma'] = 'no-cache'
        response['Expires'] = '0'
        
        return response
        
    except requests.exceptions.RequestException as e:
        print(f"Network error during download: {e}")
        return JsonResponse({
            'success': False,
            'error': f'Network error: {str(e)}'
        }, status=500)
    except Exception as e:
        print(f"Download error: {e}")
        return JsonResponse({
            'success': False,
            'error': f'Download failed: {str(e)}'
        }, status=500)

def test_endpoint(request):
    test_urls = [
        "https://www.facebook.com/watch/?v=123456789",
        "https://fb.watch/abc123def/",
        "https://www.facebook.com/reel/123456789"
    ]
    
    return JsonResponse({
        'status': 'online',
        'service': 'Facebook Video Downloader',
        'test_urls': test_urls,
        'timestamp': datetime.now().isoformat()
    })