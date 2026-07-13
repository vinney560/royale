from django.contrib import admin
from django.urls import path

urlpatterns = [
    path('admin/', admin.site.urls),
]

# ================= U_VIEW ===================
from app_royale.u_views import (
    main, contact, products,
)
from qr_gen import generate_qr_code

# --------------------------------------------
urlpatterns += [
    path('', main.main_page, name="main_page"),
    path('about/', main.about_us, name="about_us"),
    path('products/', main.products, name="products"),
    path('api/products', products.more_products, name="more_products"),
    path('contact/', contact.contact_us, name="contact"),
]

# --------------------------------------------
# Products
urlpatterns += [
    # QR GEN
    path('products/qr/', main.qr_code_gen, name="qr_code_gen"),
    path('api/products/qr-code-gen/', generate_qr_code, name="generate_qr_code"),
    path('products/qr/api-keys/', main.qr_api_keys, name="qr_api_keys"),
    path('products/qr/scr/', main.qr_gen_scr, name="qr_gen_scr"),

    # 
]
# ============================================