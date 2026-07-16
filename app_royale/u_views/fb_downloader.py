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
from django_ratelimit.decorators import ratelimit
from sys_views.rate_limit_key import getKey

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

class FacebookVideoDownloader:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(HEADERS)
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
    
    def is_valid_facebook_url(self, url):
        try:
            parsed = urlparse(url)
            if not parsed.netloc.endswith('facebook.com') and 'fb.watch' not in parsed.netloc:
                return False
            return True
        except:
            return False
    
    def get_actual_video_url(self, url):
        try:
            response = self.session.get(url, timeout=10, allow_redirects=True)
            final_url = response.url
            
            if 'login' in final_url or 'facebook.com/login' in final_url:
                mobile_headers = HEADERS.copy()
                mobile_headers['User-Agent'] = 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1'
                response = requests.get(url, headers=mobile_headers, timeout=10, allow_redirects=True)
                final_url = response.url
            
            return final_url, response.text
            
        except Exception as e:
            print(f"Error getting actual URL: {e}")
            return url, ""
    
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
            
            actual_url, html_content = self.get_actual_video_url(url)
            print(f"Actual URL: {actual_url}")
            
            if not html_content:
                return {'error': 'Could not fetch video page. The video might be private or require login.'}
            
            soup = BeautifulSoup(html_content, 'html.parser')
            
            page_title = soup.title.string if soup.title else ""
            print(f"Page title: {page_title}")
            
            if 'login' in page_title.lower() or 'log in' in page_title.lower():
                return {'error': 'Facebook is requiring login. Try using a different video or check if the video is public.'}
            
            if 'discover popular videos' in page_title.lower():
                return {'error': 'Facebook redirected to generic page. The video might not be accessible or the URL is incorrect.'}
            
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
            'message': 'Metadata extracted successfully'
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
        
        json_ld = soup.find('script', type='application/ld+json')
        if json_ld:
            try:
                data = json.loads(json_ld.string)
                if isinstance(data, dict) and 'name' in data:
                    return data['name']
            except:
                pass
        
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
        
        json_ld = soup.find('script', type='application/ld+json')
        if json_ld:
            try:
                data = json.loads(json_ld.string)
                if isinstance(data, dict) and 'description' in data:
                    return data['description']
            except:
                pass
        
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
                        date_part = date_str.split('T')[0]
                        return date_part
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
        
        json_ld = soup.find('script', type='application/ld+json')
        if json_ld:
            try:
                data = json.loads(json_ld.string)
                if isinstance(data, dict) and 'thumbnailUrl' in data:
                    return data['thumbnailUrl']
            except:
                pass
        
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
        
        return "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b8/YouTube_play_button_icon_%282013%E2%80%932017%29.svg/1200px-YouTube_play_button_icon_%282013%E2%80%932017%29.svg.png"
    
    def extract_video_urls(self, html_content):
        video_map = {}
        
        patterns_with_quality = [
            (r'"browser_native_hd_url":"([^"]+)"', 'HD'),
            (r'"browser_native_sd_url":"([^"]+)"', 'SD'),
            (r'"playable_url_quality_hd":"([^"]+)"', 'HD'),
            (r'"playable_url_quality_sd":"([^"]+)"', 'SD'),
            (r'"hd_src":"([^"]+)"', 'HD'),
            (r'"sd_src":"([^"]+)"', 'SD'),
            (r'"playable_url":"([^"]+)"', 'Auto'),
            (r'"src":"([^"]+)"', 'Unknown'),
            (r'"source":"([^"]+)"', 'Unknown'),
            (r'"video_url":"([^"]+)"', 'Unknown'),
            (r'"contentUrl":"([^"]+)"', 'Unknown'),
            (r'"url":"([^"]+)"', 'Unknown'),
        ]
        
        for pattern, quality in patterns_with_quality:
            match = re.search(pattern, html_content)
            if match:
                video_url = match.group(1).replace('\\/', '/')
                video_url = unquote(video_url)
                
                if any(ext in video_url.lower() for ext in ['.mp4', '.mov', '.avi', '.webm', 'video']):
                    if any(domain in video_url.lower() for domain in ['facebook.com', 'fbcdn.net', 'cdn.fbsbx.com', 'video.xx.fbcdn.net']):
                        detected_quality = self.detect_quality_from_url(video_url)
                        final_quality = detected_quality if detected_quality != 'Unknown' else quality
                        
                        if final_quality not in video_map:
                            video_map[final_quality] = video_url
                        elif quality == 'HD' and final_quality in ['SD', 'Unknown']:
                            video_map[final_quality] = video_url
        
        unique_urls = {}
        for quality, url in video_map.items():
            url_normalized = url.split('?')[0]
            if url_normalized not in unique_urls.values():
                unique_urls[quality] = url
        
        quality_order = {
            'HD': 0, '4K': 0, '1440p': 1, '1080p': 2, 
            '720p': 3, '480p': 4, '360p': 5, '240p': 6, 
            'SD': 7, 'Auto': 8, 'Unknown': 9
        }
        
        video_urls = [
            url for quality, url in sorted(
                unique_urls.items(), 
                key=lambda x: quality_order.get(x[0], 99)
            )
        ]
        
        return video_urls
    
    def detect_quality_from_url(self, video_url):
        quality_patterns = [
            (r'(\d{3,4})p', lambda m: f'{m.group(1)}p'),
            (r'(hd|high)', 'HD'),
            (r'(sd|standard|low)', 'SD'),
            (r'(4k|2160)', '4K'),
            (r'(1440)', '1440p'),
            (r'(1080)', '1080p'),
            (r'(720)', '720p'),
            (r'(480)', '480p'),
            (r'(360)', '360p'),
            (r'(240)', '240p'),
        ]
        
        video_url_lower = video_url.lower()
        
        for pattern, quality in quality_patterns:
            match = re.search(pattern, video_url_lower)
            if match:
                if callable(quality):
                    return quality(match)
                return quality
        
        return 'Unknown'
    
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
        
        base64_pattern = r'data:video/[^;]+;base64,[A-Za-z0-9+/=]+'
        base64_matches = re.findall(base64_pattern, html_content)
        
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
            
            headers = HEADERS.copy()
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

# Initialize downloader
downloader = FacebookVideoDownloader()

@ratelimit(key=getKey, rate='20/m', block=True)
def facebook_v_downloader(request):
    """Render the Facebook video downloader page"""
    return render(request, 'fb_vid_downloader.html')

@csrf_exempt
@require_http_methods(["POST"])
@ratelimit(key=getKey, rate='20/m', block=True)
def extract_metadata(request):
    """Extract metadata from Facebook video URL"""
    try:
        if request.content_type and 'application/json' in request.content_type:
            data = json.loads(request.body)
            url = data.get('url', '').strip()
        else:
            url = request.POST.get('url', '').strip()
        
        if not url:
            return JsonResponse({
                'success': False,
                'error': 'URL is required',
                'message': 'Please enter a Facebook video URL'
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
        return JsonResponse(metadata)
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON data',
            'message': 'Invalid JSON data'
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
@ratelimit(key=getKey, rate='20/m', block=True)
def direct_download(request):
    """Download video directly"""
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
            'Sec-Fetch-Dest': 'video',
            'Sec-Fetch-Mode': 'no-cors',
            'Sec-Fetch-Site': 'cross-site',
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