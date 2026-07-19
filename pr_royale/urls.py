from django.contrib import admin
from django.urls import path

# =============================================
# HTTP ERROR HANDLERS
from django.conf.urls import handler404, handler500, handler403
from app_royale.http_error_handlers.all_handlers import (
    handler_404_request, handler_500_request, handler_403_request
    )

handler404 = handler_404_request
handler500 = handler_500_request
handler403 = handler_403_request
# =============================================

urlpatterns = [
    path('admin/', admin.site.urls),
]
# ================= U_VIEW ===================
# u_ -> User views
from app_royale.u_views import (
    main, contact, products, qr_gen, learn_modules, 
    market_place, fb_downloader, insta_downloader
)
from sys_views import (
    web_scraper
)
# =============================================
urlpatterns += [
    path('robots.txt', main.robots_txt, name='robots_txt'),
    path('sitemap.xml', main.sitemap_xml, name='sitemap_xml'),
]

urlpatterns += [
    path('terms/', main.terms, name="terms"),
    path('privacy/', main.privacy, name="privacy"),
]
# --------------------------------------------
urlpatterns += [
    path('', main.main_page, name="main_page"),
    path('/favicon.ico', main.favivon, name="favicon_ico"),
    path('profile/', main.profile_page, name="profile_page"),
    path('about/', main.about_us, name="about_us"),
    path('contact/', contact.contact_us, name="contact"),
    path('products/', main.products, name="products"),
    path('api/products', products.more_products, name="more_products"),
]

# --------------------------------------------
# Products
urlpatterns += [
    # QR GEN
    path('products/qr/', main.qr_code_gen, name="qr_code_gen"),
    path('api/products/qr-code-gen/', qr_gen.generate_qr_code, name="generate_qr_code"),
    path('products/qr/api-keys/', main.qr_api_keys, name="qr_api_keys"),
    path('products/qr/scr/', main.qr_gen_scr, name="qr_gen_scr"),
    
    # Pretty Printer
    path('products/pretty-printer/scr/', main.pretty_printer_src, name="pretty_printer_src"),

    # Web Scraper
    path('products/web-scraper/', web_scraper.web_scraper, name="web_scraper"),
    path('api/products/web/scrape/', web_scraper.scrape, name="scrape_url"),

    # Song Search
    path("products/song-search/", main.song_search, name="song_search"),
]
# --------------------------------------------
# Market Place
urlpatterns += [
    path('market/place/', market_place.market_place, name="market_place"),

    # Wi-Fi Hotspot
    path('market/softwares/hotspot/', market_place.softwares_toSale_hotspot, name="softwares_forSale"),

]
# --------------------------------------------
# TV
urlpatterns += [
    path('products/tv/', main.royale_tv, name="royale_tv"),
    #path('products/tv/buy/', main.royale_tv_buy, name="royale_tv_buy"),
]
# --------------------------------------------
# Facebook Downloader
urlpatterns += [
    path('downloader/fb/', fb_downloader.facebook_v_downloader, name='facebook_downloader'),
    path('api/fb/extract/metadata/', fb_downloader.extract_metadata, name='extract_metadata'),
    path('api/fb/dl-video/', fb_downloader.direct_download, name='direct_download'),
]

# Instagram Downloader
urlpatterns += [
    path('downloader/instagram/', insta_downloader.insta_downloader, name='instagram_downloader'),
]
# --------------------------------------------
# Learning modules
urlpatterns += [
    path('learn/', learn_modules.modules_to_learn, name="modules_to_learn"),
    path('learn/c/', learn_modules.learn_c, name='learn_c'),
    path('learn/html/', learn_modules.learn_html, name='learn_html'),
    path('learn/flowchart/', learn_modules.learn_flowchart, name='learn_flowchart'),

]
# ============================================

# ================ Viu Live ==================
from app_viulive.views import (
    viulive_home, get_channels, get_channel_url, watching, 
    search_channel, get_channel_groups
)
# --------------------------------------------
# In urls.py
urlpatterns += [
    path("viulive/", viulive_home, name="viulive_home"),
    path("api/viulive/channels/", get_channels, name="get_channels"),
    path("api/viulive/channels/groups/", get_channel_groups, name="get_channel_groups"),
    path("api/viulive/channels/search/", search_channel, name="search_channels"),
    path("api/viulive/channel/<str:channel_id>/url/", get_channel_url, name="get_channel_url"),
    path("viulive/watching/<str:channel_id>/", watching, name="watch_channel"),
]
# ============================================